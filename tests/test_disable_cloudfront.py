import json
import os

import boto3
import pytest
from moto import mock_aws

os.environ["DISTRIBUTION_ID"] = "placeholder"

import disable_cloudfront  # noqa: E402


def make_event(state="ALARM"):
    message = {"AlarmName": "useyourai-test-cloudfront-requests", "NewStateValue": state}
    return {"Records": [{"Sns": {"Message": json.dumps(message)}}]}


@pytest.fixture
def distribution_id(monkeypatch):
    with mock_aws():
        client = boto3.client("cloudfront", region_name="us-east-1")
        distribution = client.create_distribution(DistributionConfig={
            "CallerReference": "test",
            "Comment": "",
            "Enabled": True,
            "Origins": {"Quantity": 1, "Items": [{"Id": "s3", "DomainName": "bucket.s3.amazonaws.com", "S3OriginConfig": {"OriginAccessIdentity": ""}}]},
            "DefaultCacheBehavior": {"TargetOriginId": "s3", "ViewerProtocolPolicy": "redirect-to-https", "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"},
        })["Distribution"]["Id"]
        monkeypatch.setattr(disable_cloudfront, "cloudfront", client)
        monkeypatch.setattr(disable_cloudfront, "distribution_id", distribution)
        yield distribution


def is_enabled(distribution_id):
    client = disable_cloudfront.cloudfront
    return client.get_distribution_config(Id=distribution_id)["DistributionConfig"]["Enabled"]


def test_alarm_disables_distribution(distribution_id):
    disable_cloudfront.lambda_handler(make_event(), {})
    assert is_enabled(distribution_id) is False


def test_already_disabled_distribution_is_left_alone(distribution_id):
    disable_cloudfront.lambda_handler(make_event(), {})
    disable_cloudfront.lambda_handler(make_event(), {})
    assert is_enabled(distribution_id) is False


def test_non_alarm_state_does_nothing(distribution_id):
    disable_cloudfront.lambda_handler(make_event(state="OK"), {})
    assert is_enabled(distribution_id) is True
