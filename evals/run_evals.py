"""Score the answer evaluation prompt against a labelled set of answers.

Calls Bedrock, so it costs money and is kept out of pytest and CI. Run it by hand:

    AWS_PROFILE=<profile> python evals/run_evals.py --model eu.anthropic.claude-sonnet-4-6

Uses EVAL_SYSTEM_PROMPT and the same user message and parsing as lambdas/submit_answer.py,
sent through the Converse API so any Bedrock model can be compared. Models that reject
temperature (such as Claude 5.x) need --no-temperature.
"""
import argparse
import json
import os
import pathlib
import re
import sys

import boto3

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lambdas"))
os.environ.setdefault("TABLE_NAME", "unused-by-evals")
from submit_answer import EVAL_SYSTEM_PROMPT, _strip_markdown_fences  # noqa: E402

CASES_PATH = ROOT / "evals" / "answers.jsonl"


def evaluate(client, args, case):
    # Same user message as submit_answer.lambda_handler
    eval_prompt = (
        f"Question: {case['question']}\n"
        f"Expected answer: {case['expected_answer']}\n"
        f"User's answer: <user_answer>{case['user_answer']}</user_answer>"
    )
    inference_config = {"maxTokens": 512}
    if not args.no_temperature:
        inference_config["temperature"] = args.temperature
    response = client.converse(
        modelId=args.model,
        system=[{"text": EVAL_SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": eval_prompt}]}],
        inferenceConfig=inference_config,
    )
    # Skip thinking blocks some models return before the text
    text = "".join(block["text"] for block in response["output"]["message"]["content"] if "text" in block)

    # Same parsing as submit_answer.lambda_handler; None means the Lambda would return 502
    stripped = _strip_markdown_fences(text, "evaluation")
    try:
        is_correct = json.loads(stripped).get("is_correct")
        if isinstance(is_correct, bool):
            return is_correct, text
    except (json.JSONDecodeError, ValueError, AttributeError):
        pass
    match = re.search(r'"is_correct"\s*:\s*(true|false)', stripped)
    return (match.group(1) == "true" if match else None), text


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, help="Bedrock model or inference profile ID")
    parser.add_argument("--region", default="eu-central-1")
    parser.add_argument("--temperature", type=float, default=0.3, help="default matches the Lambda")
    parser.add_argument("--no-temperature", action="store_true", help="for models that reject temperature")
    args = parser.parse_args()

    cases = [json.loads(line) for line in CASES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    client = boto3.client("bedrock-runtime", region_name=args.region)

    failures = []
    false_accepts = false_rejects = unparsed = 0
    by_kind = {}
    for case in cases:
        got, raw = evaluate(client, args, case)
        passed = got == case["should_pass"]
        kind_total, kind_passed = by_kind.get(case["kind"], (0, 0))
        by_kind[case["kind"]] = (kind_total + 1, kind_passed + passed)
        if passed:
            continue
        if got is None:
            unparsed += 1
        elif got:
            false_accepts += 1
        else:
            false_rejects += 1
        failures.append((case, got, raw))

    correct = len(cases) - len(failures)
    print(f"Model: {args.model}")
    print(f"Accuracy: {correct}/{len(cases)} ({correct / len(cases):.0%})")
    print(f"False accepts (wrong answer marked correct): {false_accepts}")
    print(f"False rejects (right answer marked wrong): {false_rejects}")
    print(f"Unparseable responses: {unparsed}")
    print("By kind: " + ", ".join(f"{kind} {ok}/{total}" for kind, (total, ok) in sorted(by_kind.items())))

    if failures:
        print("\nFailures:")
    for case, got, raw in failures:
        label = "UNPARSED" if got is None else ("FALSE ACCEPT" if got else "FALSE REJECT")
        print(f"- {case['id']} [{case['kind']}] {label}: {case['question']}")
        print(f"    expected: {case['expected_answer']} | user: {case['user_answer']}")
        if got is None:
            print(f"    raw: {raw[:200]!r}")


if __name__ == "__main__":
    main()
