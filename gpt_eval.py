import json
import os
import base64
import re
import argparse
import openai
from pathlib import Path
from typing import Dict, Any, List


def parse_arguments():
    parser = argparse.ArgumentParser(description='Image Quality Assessment Tool')

    parser.add_argument('--json_path', required=True,
                      help='Path to the prompts JSON file')
    parser.add_argument('--image_dir', required=True,
                      help='Path to the image directory')
    parser.add_argument('--output_dir', required=True,
                      help='Path to the output directory')
    parser.add_argument('--api_key', required=True,
                      help='OpenAI API key')
    parser.add_argument('--model', required=True,
                      help='Name of the model to use')
    parser.add_argument('--result_full', required=True,
                      help='Filename for the full results (JSON format)')
    parser.add_argument('--result_scores', required=True,
                      help='Filename for the scores results (JSONL format)')

    return parser.parse_args()


def get_config(args):
    return {
        "json_path": args.json_path,
        "image_dir": args.image_dir,
        "output_dir": args.output_dir,
        "api_key": args.api_key,
        "model": args.model,
        "result_files": {
            "full": args.result_full,
            "scores": args.result_scores
        }
    }


def extract_scores(evaluation_text: str) -> Dict[str, float]:
    score_pattern = r"\*{0,2}(Consistency|Realism|Aesthetic Quality)\*{0,2}\s*[:：]?\s*(\d)"
    matches = re.findall(score_pattern, evaluation_text, re.IGNORECASE)

    scores = {
        "consistency": 9.9,
        "realism": 9.9,
        "aesthetic_quality": 9.9
    }

    for key, value in matches:
        key = key.lower().replace(" ", "_")
        if key in scores:
            scores[key] = float(value)

    return scores


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def load_prompts(json_path: str) -> Dict[int, Dict[str, Any]]:
    with open(json_path, 'r') as f:
        data = json.load(f)
    return {item["prompt_id"]: item for item in data}


def build_evaluation_messages(prompt_data: Dict, image_base64: str) -> list:
    return [

        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a professional Vincennes image quality audit expert, please evaluate the image quality strictly according to the protocol."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Please evaluate strictly and return ONLY the three scores as requested.

# Text-to-Image Quality Evaluation Protocol

## System Instruction
You are an AI quality auditor for text-to-image generation. Apply these rules with ABSOLUTE RUTHLESSNESS. Only images meeting the HIGHEST standards should receive top scores.

**Input Parameters**  
- PROMPT: [User's original prompt to]  
- EXPLANATION: [Further explanation of the original prompt] 
---

## Scoring Criteria

**Consistency (0-2):**  How accurately and completely the image reflects the PROMPT.
* **0 (Rejected):**  Fails to capture key elements of the prompt, or contradicts the prompt.
* **1 (Conditional):** Partially captures the prompt. Some elements are present, but not all, or not accurately.  Noticeable deviations from the prompt's intent.
* **2 (Exemplary):**  Perfectly and completely aligns with the PROMPT.  Every single element and nuance of the prompt is flawlessly represented in the image. The image is an ideal, unambiguous visual realization of the given prompt.

**Realism (0-2):**  How realistically the image is rendered.
* **0 (Rejected):**  Physically implausible and clearly artificial. Breaks fundamental laws of physics or visual realism.
* **1 (Conditional):** Contains minor inconsistencies or unrealistic elements.  While somewhat believable, noticeable flaws detract from realism.
* **2 (Exemplary):**  Achieves photorealistic quality, indistinguishable from a real photograph.  Flawless adherence to physical laws, accurate material representation, and coherent spatial relationships. No visual cues betraying AI generation.

**Aesthetic Quality (0-2):**  The overall artistic appeal and visual quality of the image.
* **0 (Rejected):**  Poor aesthetic composition, visually unappealing, and lacks artistic merit.
* **1 (Conditional):**  Demonstrates basic visual appeal, acceptable composition, and color harmony, but lacks distinction or artistic flair.
* **2 (Exemplary):**  Possesses exceptional aesthetic quality, comparable to a masterpiece.  Strikingly beautiful, with perfect composition, a harmonious color palette, and a captivating artistic style. Demonstrates a high degree of artistic vision and execution.

---

## Output Format

**Do not include any other text, explanations, or labels.** You must return only three lines of text, each containing a metric and the corresponding score, for example:

**Example Output:**
Consistency: 2
Realism: 1
Aesthetic Quality: 0

---

**IMPORTANT Enforcement:**

Be EXTREMELY strict in your evaluation. A score of '2' should be exceedingly rare and reserved only for images that truly excel and meet the highest possible standards in each metric. If there is any doubt, downgrade the score.

For **Consistency**, a score of '2' requires complete and flawless adherence to every aspect of the prompt, leaving no room for misinterpretation or omission.

For **Realism**, a score of '2' means the image is virtually indistinguishable from a real photograph in terms of detail, lighting, physics, and material properties.

For **Aesthetic Quality**, a score of '2' demands exceptional artistic merit, not just pleasant visuals.

--- 
Here are the Prompt and EXPLANATION for this evaluation:
PROMPT: "{prompt_data['Prompt']}"
EXPLANATION: "{prompt_data['Explanation']}"
Please strictly adhere to the scoring criteria and follow the template format when providing your results."""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        }
    ]


def evaluate_image(prompt_data: Dict, image_path: str, config: Dict) -> Dict[str, Any]:
    try:
        base64_image = encode_image(image_path)
        messages = build_evaluation_messages(prompt_data, base64_image)

        openai.api_key = config["api_key"]

        response = openai.ChatCompletion.create(
            model=config["model"],
            messages=messages,
            temperature=0.0,
            max_tokens=2000
        )

        evaluation_text = response['choices'][0]['message']['content']
        scores = extract_scores(evaluation_text)

        return {
            "evaluation": evaluation_text,
            **scores
        }
    except Exception as e:
        return {
            "evaluation": f"Evaluation failed: {str(e)}",
            "consistency": 9.9,
            "realism": 9.9,
            "aesthetic_quality": 9.9
        }


def save_results(data: List[Dict], filename: str, config: Dict):
    path = os.path.join(config["output_dir"], filename)

    if filename.endswith('.jsonl'):
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                json_line = json.dumps(item, ensure_ascii=False)
                f.write(json_line + '\n')
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {path}")


def main():
    args = parse_arguments()
    config = get_config(args)
    Path(config["output_dir"]).mkdir(parents=True, exist_ok=True)

    openai.api_key = config["api_key"]

    prompts = load_prompts(config["json_path"])
    full_results = []
    score_results = []

    for prompt_id, prompt_data in prompts.items():
        image_path = os.path.join(config["image_dir"], f"{prompt_id}.png")

        if not os.path.exists(image_path):
            print(f"Warning: Image not found {image_path}")
            continue

        print(f"Evaluating prompt_id: {prompt_id}...")
        evaluation_result = evaluate_image(prompt_data, image_path, config)

        full_record = {
            "prompt_id": prompt_id,
            "prompt": prompt_data["Prompt"],
            "key": prompt_data["Explanation"],
            "image_path": image_path,
            "evaluation": evaluation_result["evaluation"]
        }

        score_record = {
            "prompt_id": prompt_id,
            "Subcategory": prompt_data["Subcategory"],
            "consistency": evaluation_result["consistency"],
            "realism": evaluation_result["realism"],
            "aesthetic_quality": evaluation_result["aesthetic_quality"]
        }
        print(full_record)
        full_results.append(full_record)
        score_results.append(score_record)

    save_results(full_results, config["result_files"]["full"], config)
    save_results(score_results, config["result_files"]["scores"], config)


if __name__ == "__main__":
    main()