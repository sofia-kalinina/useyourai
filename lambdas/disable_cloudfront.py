import boto3
import json
import os

distribution_id = os.getenv('DISTRIBUTION_ID')
if not distribution_id:
    raise ValueError("Environment variable 'DISTRIBUTION_ID' is not set.")

cloudfront = boto3.client('cloudfront')


def lambda_handler(event, context):
    # Triggered through SNS by the CloudFront request alarm. Disabling the distribution stops
    # request and data transfer charges during a flood; the next Terraform apply re-enables it.
    alarm = json.loads(event["Records"][0]["Sns"]["Message"])
    if alarm.get("NewStateValue") != "ALARM":
        print(f"[disable_cloudfront] Ignoring alarm state {alarm.get('NewStateValue')}")
        return

    response = cloudfront.get_distribution_config(Id=distribution_id)
    config = response["DistributionConfig"]
    if not config["Enabled"]:
        print(f"[disable_cloudfront] Distribution {distribution_id} is already disabled")
        return

    config["Enabled"] = False
    cloudfront.update_distribution(Id=distribution_id, IfMatch=response["ETag"], DistributionConfig=config)
    print(f"[disable_cloudfront] Disabled distribution {distribution_id} after alarm {alarm.get('AlarmName')}")
