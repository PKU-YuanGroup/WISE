import json
import os
import base64
import re
import argparse
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List

import requests

REQUIRED_SCORE_KEYS = {"score"}
MAX_EXTRACT_RETRIES = 3


def parse_arguments():
    parser = argparse.ArgumentParser(description="Image Quality Assessment Tool (vLLM)")
    parser.add_argument("--json_path", required=True)
    parser.add_argument("--image_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--api_key", default="", type=str)
    parser.add_argument("--model", required=True)
    parser.add_argument("--result_full", required=True)  # .json
    parser.add_argument("--result_scores", required=True)  # .jsonl
    parser.add_argument("--api_base", default="http://127.0.0.1:8000/v1", type=str)
    parser.add_argument("--max_workers", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args()


def get_config(args):
    return {
        "json_path": args.json_path,
        "image_dir": args.image_dir,
        "output_dir": args.output_dir,
        "api_key": args.api_key,
        "api_base": args.api_base.rstrip("/"),
        "model": args.model,
        "result_files": {"full": args.result_full, "scores": args.result_scores},
        "max_workers": args.max_workers,
        "timeout": args.timeout,
    }


def load_jsonl(path: str) -> Dict[int, Dict]:
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return {}
    records = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            records[obj["prompt_id"]] = obj
    return records


def load_json(path: str) -> Dict[int, Dict]:
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["prompt_id"]: item for item in data}


def extract_scores(txt: str) -> Dict[str, float]:
    match = re.search(r"\*{0,2}Score\*{0,2}\s*[::]?\s*([01])\b", txt, re.IGNORECASE)
    if match:
        return {"score": float(match.group(1))}

    # Fallback: handle a bare single-line numeric output like:
    # 1
    nums = re.findall(r"(?m)^\s*([01])\s*$", txt)
    if len(nums) == 1:
        return {"score": float(nums[0])}
    return {}


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def load_prompts(path: str) -> Dict[int, Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["prompt_id"]: item for item in data}


def build_evaluation_messages(prompt_data: Dict, image_base64: str) -> list:
    return [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a professional text-to-image quality auditor. Evaluate the image strictly according to the protocol.",
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Please evaluate this generated image for the WISE benchmark and return ONLY one binary score.

# WISE Text-to-Image Evaluation Protocol

## What WISE Is Evaluating
WISE is a knowledge-intensive text-to-image benchmark. Many prompts do not directly state the final visual answer. Instead, the model must use commonsense, cultural, scientific, spatial, or temporal knowledge to infer what should appear in the image.

Your job is not to judge whether the image is beautiful. Your job is to judge whether the generated image correctly realizes the knowledge-based meaning of the prompt and is visually usable.

## Input Fields

**PROMPT**
The original text-to-image prompt given to the image generation model. It may contain an implicit clue rather than the explicit final answer.

**EXPLANATION**
The reference interpretation used for judging. It explains the intended answer, the required knowledge reasoning chain, and the visual evidence that should appear in a correct image. Treat EXPLANATION as the ground-truth judging guide.

For example:
- If PROMPT says "the round pastry commonly shared during Mid-Autumn Festival family gatherings", EXPLANATION may specify mooncakes. A correct image should show mooncakes, not just any festival food.
- If PROMPT says "a plant kept for many days beside a bright one-sided window", EXPLANATION may specify phototropism. A correct image should show the plant bending toward the light source.
- If PROMPT says "a street in New York when it is midnight in Beijing", EXPLANATION may specify the corresponding local time and expected lighting/activity. A correct image should reflect that inferred local time, not simply show Beijing or generic night.

## How To Judge

Evaluate the image using these checks:
1. Does the image contain the main objects or scene required by the PROMPT?
2. Does it satisfy the intended knowledge-based answer described in the EXPLANATION?
3. Are important relations correct, such as spatial layout, temporal state, physical effect, biological behavior, cultural object, or scientific phenomenon?
4. Is the image visually usable for judging, without obvious collapse, severe deformation, unreadable main objects, or major artifacts?

## Binary Score

**Score: 1**
Give 1 only when both conditions are met:
- The image is semantically correct according to both PROMPT and EXPLANATION.
- The image has no obvious generation failure that prevents reliable judging.

Minor aesthetic weakness, ordinary composition, non-photorealistic style, or lack of artistic beauty should not by itself cause rejection if the semantic target is correct and the image is clear.

**Score: 0**
Give 0 if any of the following applies:
- The image misses the intended answer in EXPLANATION.
- The image only follows surface words in PROMPT but fails the required knowledge inference.
- Key objects, attributes, states, behaviors, or relations are missing or wrong.
- The image contradicts the prompt or explanation.
- The main visual evidence is ambiguous enough that a human judge could not confidently verify correctness.
- The image has obvious visual collapse, severe deformation, garbled main objects, impossible structure, or artifacts that interfere with evaluation.

If there is serious doubt, return 0.

## Output Format

Return exactly one line and nothing else:

Score: 0

or

Score: 1

---

PROMPT: "{prompt_data['Prompt']}"
EXPLANATION: "{prompt_data['Explanation']}"

Return only `Score: 0` or `Score: 1`.""",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                },
            ],
        },
    ]


def _chat_completion_via_vllm(messages: List[Dict[str, Any]], cfg: Dict) -> str:
    endpoint = f"{cfg['api_base']}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    payload = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 500,
        # NOTE: using raw requests here, so parameters must be top-level.
        "chat_template_kwargs": {"enable_thinking": False},
    }
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=cfg["timeout"])
    resp.raise_for_status()
    body = resp.json()
    content = body["choices"][0]["message"]["content"]
    # Fallback cleanup: some models may still output think tags.
    content = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL)
    content = re.sub(r"</think>\s*", "", content)
    return content.strip()


def evaluate_image(prompt_id: int, prompt: Dict, img_path: str, cfg: Dict):
    print(f"Evaluating {prompt_id} ...")
    img64 = encode_image(img_path)
    msgs = build_evaluation_messages(prompt, img64)

    for attempt in range(1, MAX_EXTRACT_RETRIES + 1):
        try:
            eval_txt = _chat_completion_via_vllm(msgs, cfg)
            scores = extract_scores(eval_txt)
            print(f"\n--- {prompt_id} (attempt {attempt}) ---\n{eval_txt}\n--------------\n")

            if REQUIRED_SCORE_KEYS.issubset(scores.keys()):
                return {
                    "status": "ok",
                    "full": {
                        "prompt_id": prompt_id,
                        "prompt": prompt["Prompt"],
                        "key": prompt["Explanation"],
                        "image_path": img_path,
                        "evaluation": eval_txt,
                    },
                    "score": {
                        "prompt_id": prompt_id,
                        "Subcategory": prompt["Subcategory"],
                        "score": scores["score"],
                    },
                }

            missing = sorted(REQUIRED_SCORE_KEYS - set(scores.keys()))
            print(f"[WARN] {prompt_id}: score parse incomplete, missing={missing}, attempt={attempt}/{MAX_EXTRACT_RETRIES}")
        except Exception as e:
            print(f"[ERR] {prompt_id}: attempt={attempt}/{MAX_EXTRACT_RETRIES}, err={e}")

    return {"status": "extract_fail", "prompt_id": prompt_id}


def save_results(data: List[Dict], filename: str, cfg: Dict):
    path = os.path.join(cfg["output_dir"], filename)
    if filename.endswith(".jsonl"):
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[SAVE] {path}")


def main():
    args = parse_arguments()
    cfg = get_config(args)
    Path(cfg["output_dir"]).mkdir(parents=True, exist_ok=True)

    prompts = load_prompts(cfg["json_path"])

    exist_scores = load_jsonl(os.path.join(cfg["output_dir"], cfg["result_files"]["scores"]))
    exist_full = load_json(os.path.join(cfg["output_dir"], cfg["result_files"]["full"]))
    done_ids = set(exist_scores.keys())

    tasks = []
    for pid, pdata in prompts.items():
        if pid in done_ids:
            continue
        img_path = os.path.join(cfg["image_dir"], f"{pid}.png")
        if not os.path.exists(img_path):
            print(f"[WARN] Missing image: {img_path}")
            continue
        tasks.append((pid, pdata, img_path))

    failed_extract_ids = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg["max_workers"]) as ex:
        future_to_id = {ex.submit(evaluate_image, pid, pd, ip, cfg): pid for pid, pd, ip in tasks}
        for fut in concurrent.futures.as_completed(future_to_id):
            res = fut.result()
            if not res or res.get("status") != "ok":
                if res and res.get("status") == "extract_fail":
                    failed_extract_ids.append(res["prompt_id"])
                continue
            full_rec = res["full"]
            score_rec = res["score"]
            exist_full[full_rec["prompt_id"]] = full_rec
            exist_scores[score_rec["prompt_id"]] = score_rec

    full_sorted = [exist_full[k] for k in sorted(exist_full.keys())]
    score_sorted = [exist_scores[k] for k in sorted(exist_scores.keys())]

    save_results(full_sorted, cfg["result_files"]["full"], cfg)
    save_results(score_sorted, cfg["result_files"]["scores"], cfg)
    if failed_extract_ids:
        print(f"[WARN] Failed to extract scores (skipped): {sorted(failed_extract_ids)}")


if __name__ == "__main__":
    main()
