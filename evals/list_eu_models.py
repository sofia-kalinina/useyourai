"""List the text models this account can call with processing kept in the EU, and test each with one tiny call.

Calls Bedrock, so run it by hand (costs well under a cent in total):

    AWS_PROFILE=<profile> python evals/list_eu_models.py

Counts as EU: `eu.` inference profiles from eu-central-1, and models offered on demand inside an EU region.
`global.`, `us.` and other profiles are skipped, since they can process outside the EU.
Skips Anthropic, Amazon and xAI.
"""
import boto3
from botocore.config import Config

EU_REGIONS = ["eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "eu-south-1", "eu-south-2", "eu-central-2"]
SKIP = ("anthropic", "amazon", "xai")


def candidates():
    found = []
    profiles = boto3.client("bedrock", region_name="eu-central-1").list_inference_profiles(maxResults=1000)
    for p in profiles["inferenceProfileSummaries"]:
        pid = p["inferenceProfileId"]
        if pid.startswith("eu.") and not any(s in pid for s in SKIP):
            found.append(("eu-central-1", pid, "eu. profile"))
    for region in EU_REGIONS:
        try:
            models = boto3.client("bedrock", region_name=region).list_foundation_models(byOutputModality="TEXT")["modelSummaries"]
        except Exception as e:
            print(f"SKIPPED {region}: {type(e).__name__}")
            continue
        for m in models:
            if "ON_DEMAND" in m.get("inferenceTypesSupported", []) and not any(s in m["modelId"] for s in SKIP) \
                    and "TEXT" in m.get("inputModalities", []):
                found.append((region, m["modelId"], "in-region"))
    return found


def main():
    for region, model_id, how in sorted(candidates()):
        # 30 s and no retries, so one hanging model can't block the rest
        runtime = boto3.client("bedrock-runtime", region_name=region,
                               config=Config(connect_timeout=10, read_timeout=30, retries={"total_max_attempts": 1}))
        print(f"...     {region:13} {how:12} {model_id}", end="\r", flush=True)
        try:
            r = runtime.converse(modelId=model_id, messages=[{"role": "user", "content": [{"text": "Reply with OK"}]}],
                                 inferenceConfig={"maxTokens": 20})
            text = "".join(b.get("text", "") for b in r["output"]["message"]["content"]).strip().replace("\n", " ")
            print(f"OK      {region:13} {how:12} {model_id}: {text[:30]}")
        except Exception as e:
            print(f"FAILED  {region:13} {how:12} {model_id}: {type(e).__name__}: {str(e)[:120]}")


if __name__ == "__main__":
    main()
