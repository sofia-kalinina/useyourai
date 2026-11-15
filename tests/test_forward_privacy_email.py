import os
from email import message_from_bytes, policy

import boto3
import pytest
from moto import mock_aws

os.environ["MAIL_BUCKET"] = "placeholder"
os.environ["MAIL_PREFIX"] = "privacy/"
os.environ["SENDER"] = "privacy@example.com"
os.environ["FORWARD_TO"] = "owner@example.org"

import forward_privacy_email  # noqa: E402

RAW = (
    b"From: Jane Doe <jane@sender.example>\r\n"
    b"To: privacy@example.com\r\n"
    b"Subject: Delete my data\r\n"
    b"Message-ID: <abc@sender.example>\r\n"
    b"DKIM-Signature: v=1; a=rsa-sha256; d=sender.example\r\n"
    b"\r\n"
    b"Please delete my account.\r\n"
)


def make_event(message_id="msg-1", virus="PASS"):
    return {"Records": [{"ses": {
        "mail": {"messageId": message_id, "commonHeaders": {"from": ["Jane Doe <jane@sender.example>"], "subject": "Delete my data"}},
        "receipt": {"virusVerdict": {"status": virus}},
    }}]}


@pytest.fixture
def aws(monkeypatch):
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-central-1")
        s3.create_bucket(Bucket="mail-bucket", CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})
        sent = []
        ses = boto3.client("ses", region_name="eu-central-1")
        monkeypatch.setattr(ses, "send_raw_email", lambda **kwargs: sent.append(kwargs))
        monkeypatch.setattr(forward_privacy_email, "s3", s3)
        monkeypatch.setattr(forward_privacy_email, "ses", ses)
        monkeypatch.setattr(forward_privacy_email, "bucket", "mail-bucket")
        yield s3, sent


def test_forward_rewrites_sender_and_keeps_reply_to():
    forwarded = message_from_bytes(forward_privacy_email.build_forward(RAW), policy=policy.default)

    assert forwarded["From"] == "Jane Doe via useyourai <privacy@example.com>"
    assert forwarded["Reply-To"] == "Jane Doe <jane@sender.example>"
    assert forwarded["Subject"] == "Delete my data"
    assert forwarded["DKIM-Signature"] is None
    assert forwarded["Message-ID"] is None
    assert "Please delete my account." in forwarded.get_content()


def test_handler_forwards_stored_message(aws):
    s3, sent = aws
    s3.put_object(Bucket="mail-bucket", Key="privacy/msg-1", Body=RAW)

    forward_privacy_email.lambda_handler(make_event(), {})

    assert len(sent) == 1
    assert sent[0]["Source"] == "privacy@example.com"
    assert sent[0]["Destinations"] == ["owner@example.org"]


def test_handler_drops_message_that_failed_virus_scan(aws):
    s3, sent = aws

    forward_privacy_email.lambda_handler(make_event(virus="FAIL"), {})

    assert sent == []


def test_handler_sends_notice_for_oversized_message(aws, monkeypatch):
    s3, sent = aws
    s3.put_object(Bucket="mail-bucket", Key="privacy/msg-1", Body=RAW)
    monkeypatch.setattr(forward_privacy_email, "MAX_FORWARD_BYTES", 10)

    forward_privacy_email.lambda_handler(make_event(), {})

    notice = message_from_bytes(sent[0]["RawMessage"]["Data"], policy=policy.default)
    assert notice["Subject"] == "Message too large to forward: Delete my data"
    assert "s3://mail-bucket/privacy/msg-1" in notice.get_content()
