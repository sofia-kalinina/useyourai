"""Generate a fixed set of exercise sets with one Bedrock model, to compare models and prompts.

Calls Bedrock, so it costs money and is kept out of pytest and CI. Run it by hand:

    AWS_PROFILE=<profile> python evals/run_generation.py --model eu.amazon.nova-pro-v1:0 --smoke
    AWS_PROFILE=<profile> python evals/run_generation.py --model eu.amazon.nova-pro-v1:0

--smoke runs one set so you can check real token use and cost first.
The full run is 30 sets (fixed requests and variety seeds, A1/B1/C1) plus 3 stress sets
(20 exercises, Ukrainian, C2). Running cost is printed after every call; Ctrl+C stops it.

System prompt = the app's generation prompt + docs/cefr_level_guide.md, as in scripts/sample_exercises.py.
User message = the app's message + a variety seed from evals/seeds-round5.json. Temperature 0.7 as in the app.
"""
import argparse
import json
import os
import pathlib
import re
import sys
import time

import boto3
from botocore.config import Config

ROOT = pathlib.Path(__file__).resolve().parent.parent
os.environ.setdefault("TABLE_NAME", "unused-by-evals")
sys.path.insert(0, str(ROOT / "lambdas"))
from create_session import LANG_INSTRUCTIONS, SYSTEM_PROMPT  # noqa: E402

GUIDE_PATH = ROOT / "docs" / "cefr_level_guide.md"
SEEDS_PATH = ROOT / "evals" / "seeds-round5.json"
OUT_ROOT = ROOT / "evals" / "results"

# Requests: seed key -> (request, interface language)
REQUESTS = {
    "english": ("English conditionals", "en"),
    "german-run1": ("German accusative and dative", "en"),
    "german-run2": ("German accusative and dative", "en"),
    "spanish": ("Spanish ser vs estar", "uk"),
    "french": ("French passé composé vs imparfait", "en"),
    "romanian": ("Romanian definite article", "en"),
    "ukrainian-run1": ("Ukrainian verb aspect, perfective vs imperfective", "en"),
    "ukrainian-run2": ("Ukrainian verb aspect, perfective vs imperfective", "en"),
    "greek": ("Greek past tenses: aorist vs imperfect", "en"),
    "finnish": ("Finnish partitive case", "en"),
}
LEVELS = ["A1", "B1", "C1"]
STRESS = {"request": "{n} exercises on Ukrainian verb aspect, perfective vs imperfective", "level": "C2", "lang": "uk", "runs": 3}

# Bedrock EU prices in USD per 1M tokens (input, output). Third-party trackers and the AWS price list,
# Nov 2026; Nova Pro uses the higher of the quoted EU rates. Confirm on the AWS price list before quoting.
PRICES = {
    "nova-pro": (1.05, 4.20),
    "nova-2-lite": (0.429, 3.597),
    "nova-lite": (0.078, 0.312),
    "qwen3-235b": (0.22, 0.88),  # US price from third-party trackers; EU may be higher
    "pixtral-large": (2.00, 6.00),
    "sonnet-4-6": (3.30, 16.50),
    "haiku-4-5": (1.10, 5.50),
}


def price_for(model_id):
    for key, price in PRICES.items():
        if key in model_id:
            return price
    return None


def seeds_by_level(seed_text):
    # "A1:\n  1. ...\nB1:\n  1. ..." -> {"A1": "  1. ...", ...}
    parts = re.split(r"^(A1|A2|B1|B2|C1|C2):\s*$", seed_text, flags=re.M)
    return {parts[i]: parts[i + 1].strip("\n") for i in range(1, len(parts), 2)}


def user_message(request, level, lang, seed):
    # Same shape as create_session, plus the seed the guide expects from the app.
    lang_line = f"\n{LANG_INSTRUCTIONS[lang]}" if lang in LANG_INSTRUCTIONS else ""
    seed_block = f"\nVariety seed:\n{seed}" if seed else ""
    return f"<user_prompt>{request}</user_prompt>\nTarget level: {level}{lang_line}{seed_block}"


def check_output(text, expected_count):
    """app_accepts: the Lambda would accept it as is. json_found: a JSON object can be pulled out for review."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    def valid(data):
        exercises = data.get("exercises") if isinstance(data, dict) else None
        return bool(exercises) and all(
            isinstance(ex, dict) and all(isinstance(ex.get(f), str) and ex.get(f) for f in ("id", "question", "expected_answer"))
            for ex in exercises
        )

    try:
        data = json.loads(stripped)
        app_accepts = valid(data)
    except (json.JSONDecodeError, ValueError):
        data, app_accepts = None, False
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                data = json.loads(text[start:end + 1])
            except (json.JSONDecodeError, ValueError):
                data = None
    count = len(data["exercises"]) if data is not None and valid(data) else 0
    return {"app_accepts": app_accepts, "json_found": count > 0, "exercise_count": count,
            "count_ok": count == expected_count, "parsed": data if count else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, help="Bedrock model or inference profile ID")
    parser.add_argument("--region", default="eu-central-1")
    parser.add_argument("--max-tokens", type=int, default=10000)
    parser.add_argument("--smoke", action="store_true", help="run one set only")
    parser.add_argument("--silent-plan", action="store_true", help="tell the model to plan in its head and return only the JSON")
    parser.add_argument("--short-keys", action="store_true", help="tell the model to keep expected_answer to the answer and its accepted alternatives")
    parser.add_argument("--stress-size", type=int, default=20, help="exercises per stress set (default 20)")
    parser.add_argument("--stress-only", action="store_true", help="run only the 3 stress sets")
    parser.add_argument("--only", help="comma-separated request names from REQUESTS, e.g. german-run1,spanish; stress sets always run")
    args = parser.parse_args()

    system_prompt = f"{SYSTEM_PROMPT}\n\nFollow this guide when writing the exercises:\n<guide>\n{GUIDE_PATH.read_text(encoding='utf-8')}\n</guide>"
    if args.silent_plan:
        system_prompt += ("\n\nDo the planning and the self-check from the guide in your head. Do not write the plan, notes or drafts: "
                          "your whole reply is the final JSON object and nothing else.")
    if args.short_keys:
        system_prompt += ("\n\nIn expected_answer write only the correct answer and, if there are any, the accepted alternatives "
                          "separated by \" / \". No explanations, rule names or reasons, except the five-word reason the "
                          "\"Choose the nuance\" format asks for.")
    seeds = json.loads(SEEDS_PATH.read_text(encoding="utf-8"))

    jobs = []
    only = [] if args.stress_only else (args.only.split(",") if args.only else list(REQUESTS))
    unknown = [k for k in only if k not in REQUESTS]
    if unknown:
        parser.error(f"unknown request names: {', '.join(unknown)}")
    for key in only:
        request, lang = REQUESTS[key]
        level_seeds = seeds_by_level(seeds[key])
        for level in LEVELS:
            jobs.append({"name": f"{key}-{level}", "request": request, "level": level, "lang": lang,
                         "seed": level_seeds[level], "expected_count": 5})
    for run in range(1, STRESS["runs"] + 1):
        jobs.append({"name": f"stress{args.stress_size}-{run}", "request": STRESS["request"].format(n=args.stress_size),
                     "level": STRESS["level"], "lang": STRESS["lang"], "seed": None, "expected_count": args.stress_size})
    if args.smoke:
        jobs = jobs[:1]

    # No retries: a retried timeout would bill the request twice.
    client = boto3.client("bedrock-runtime", region_name=args.region,
                          config=Config(read_timeout=300, retries={"total_max_attempts": 1}))
    price = price_for(args.model)
    label = args.model.split(".")[-1].split(":")[0]
    tag = ("-smoke" if args.smoke else ("-stress" if args.stress_only else ("-gate" if args.only else ""))) + ("-silent" if args.silent_plan else "") + ("-short" if args.short_keys else "")
    out_dir = OUT_ROOT / f"{label}{tag}-{time.strftime('%Y%m%d-%H%M%S')}"
    out_dir.mkdir(parents=True)

    cost = 0.0
    summary = []
    for i, job in enumerate(jobs, start=1):
        start = time.time()
        response = client.converse(
            modelId=args.model,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": user_message(job['request'], job['level'], job['lang'], job['seed'])}]}],
            inferenceConfig={"maxTokens": args.max_tokens, "temperature": 0.7},
        )
        seconds = round(time.time() - start, 1)
        text = "".join(block["text"] for block in response["output"]["message"]["content"] if "text" in block)
        usage = {"input_tokens": response["usage"]["inputTokens"], "output_tokens": response["usage"]["outputTokens"]}
        if price:
            cost += (usage["input_tokens"] * price[0] + usage["output_tokens"] * price[1]) / 1_000_000
        result = {**job, "model": args.model, "seconds": seconds, "stop_reason": response["stopReason"], **usage,
                  **check_output(text, job["expected_count"]), "text": text}
        (out_dir / f"{i:02d}-{job['name']}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        summary.append({k: v for k, v in result.items() if k not in ("text", "parsed", "seed")})

        flags = [] if result["app_accepts"] else ["APP WOULD REJECT"]
        if result["stop_reason"] == "max_tokens":
            flags.append("CUT OFF")
        if not result["count_ok"]:
            flags.append(f"{result['exercise_count']}/{job['expected_count']} exercises")
        running = f"${cost:.3f}" if price else "cost unknown"
        print(f"{i:02d}/{len(jobs)} {job['name']:22} {seconds:>6}s {usage['output_tokens']:>6} out  {running:>8}  {' | '.join(flags)}")

    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTotal: ${cost:.3f}" if price else "\nTotal: unknown model price")
    print(f"Saved to {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
