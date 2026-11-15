import boto3
import os
from email import message_from_bytes, policy
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

bucket = os.getenv('MAIL_BUCKET')
prefix = os.getenv('MAIL_PREFIX', '')
sender = os.getenv('SENDER')
forward_to = os.getenv('FORWARD_TO')
for name, value in [('MAIL_BUCKET', bucket), ('SENDER', sender), ('FORWARD_TO', forward_to)]:
    if not value:
        raise ValueError(f"Environment variable '{name}' is not set.")

# SES SendRawEmail rejects messages over 10 MB.
MAX_FORWARD_BYTES = 10 * 1024 * 1024

s3 = boto3.client('s3', region_name='eu-central-1')
ses = boto3.client('ses', region_name='eu-central-1')


def build_forward(raw):
    # SES can only send from a verified identity, so the forward comes from our own address.
    # The original sender goes into Reply-To, so replying in the inbox answers them directly.
    message = message_from_bytes(raw, policy=policy.default)
    original_from = message.get('From', '')
    name, address = parseaddr(original_from)

    for header in ['From', 'Reply-To', 'Return-Path', 'Sender', 'DKIM-Signature', 'Message-ID']:
        del message[header]
    message['From'] = formataddr((f"{name or address} via useyourai", sender))
    message['Reply-To'] = original_from
    return message.as_bytes()


def build_notice(message_id, original_from, subject):
    notice = EmailMessage()
    notice['From'] = sender
    notice['To'] = forward_to
    notice['Subject'] = f"Message too large to forward: {subject}"
    notice.set_content(
        f"A message to {sender} from {original_from} was too large to forward.\n"
        f"It is stored in s3://{bucket}/{prefix}{message_id} until the bucket's lifecycle rule deletes it."
    )
    return notice.as_bytes()


def lambda_handler(event, context):
    # Triggered by the SES receipt rule after its S3 action stored the raw message.
    mail = event["Records"][0]["ses"]["mail"]
    receipt = event["Records"][0]["ses"]["receipt"]
    message_id = mail["messageId"]

    if receipt["virusVerdict"]["status"] == "FAIL":
        print(f"[forward_privacy_email] Dropped message {message_id}: virus scan failed")
        return

    raw = s3.get_object(Bucket=bucket, Key=f"{prefix}{message_id}")["Body"].read()

    if len(raw) > MAX_FORWARD_BYTES:
        headers = mail["commonHeaders"]
        data = build_notice(message_id, headers.get("from", ["unknown"])[0], headers.get("subject", ""))
        print(f"[forward_privacy_email] Message {message_id} is {len(raw)} bytes, sending a notice instead")
    else:
        data = build_forward(raw)

    ses.send_raw_email(Source=sender, Destinations=[forward_to], RawMessage={"Data": data})
    print(f"[forward_privacy_email] Forwarded message {message_id}")
