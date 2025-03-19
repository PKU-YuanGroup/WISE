import json
import os

MODEL_ORDER = [
    "FLUX.1-dev",
    "FLUX.1-schnell",
    "PixArt-XL-2-1024-MS",
    "playground-v2.5-1024px-aesthetic",
    "stable-diffusion-v1-5",
    "stable-diffusion-2-1",
    "stable-diffusion-3-medium-diffusers",
    "stable-diffusion-3.5-medium",
    "stable-diffusion-3.5-large",
    "Emu3-Gen",
    "Janus-1.3B",
    "JanusFlow-1.3B",
    "Janus-Pro-1B",
    "Janus-Pro-7B",
    "Orthus-7B-base",
    "Orthus-7B-instruct",
    "show-o-demo",
    "show-o-demo-512",
    "vila-u-7b-256",
    "stable-diffusion-xl-base-0.9"
]

def calculate_wiscore(consistency, realism, aesthetic_quality):
    return 0.7 * consistency + 0.2 * realism + 0.1 * aesthetic_quality

def process_jsonl_file(file_path):
    all_scores = []
    total_objects = 0
    has_9_9 = False
    
    with open(file_path, 'r') as file:
        for line in file:
            total_objects += 1
            data = json.loads(line)
            if 9.9 in [data['consistency'], data['realism'], data['aesthetic_quality']]:
                has_9_9 = True
            wiscore = calculate_wiscore(data['consistency'], data['realism'], data['aesthetic_quality'])
            all_scores.append(wiscore)
    
    if has_9_9 or total_objects < 400:
        print(f"Skipping file {file_path}: Contains 9.9 or has less than 400 objects.")
        return None
    
    total_score = sum(all_scores)
    avg_score = total_score / (len(all_scores)*2) if len(all_scores) > 0 else 0
    
    return {
        'total': total_score,
        'average': avg_score
    }

def main(directory):
    results = {}
    
    for filename in os.listdir(directory):
        if filename.endswith('_scores.jsonl'):
            parts = filename.split('_')
            if len(parts) >= 4:
                model_name = parts[3]# "Assume the filename format is 'cultural_common_sense_ModelName_scores.jsonl'"
                file_path = os.path.join(directory, filename)
                scores = process_jsonl_file(file_path)
                if scores is not None:
                    results[model_name] = scores
    
    for model in MODEL_ORDER:
        if model in results:
            print(f"Model: {model}")
            print(f"  Total Score: {results[model]['total']:.2f}")
            print(f"  Average Score: {results[model]['average']:.2f}\n")
        else:
            print(f"Model: {model} - No valid data found.\n")

main('/results/cultural_common_sense')
