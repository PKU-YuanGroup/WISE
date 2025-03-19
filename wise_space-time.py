import json
import os
from collections import defaultdict

MODEL_ORDER = [
    "FLUX.1-dev",
    "FLUX.1-schnell",
    "PixArt-XL-2-1024-MS",
    "playground-v2.5-1024px-aesthetic",
    "stable-diffusion-v1-5",
    "stable-diffusion-2-1",
    "stable-diffusion-xl-base-0.9",
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
    "vila-u-7b-256"
]

def calculate_wiscore(consistency, realism, aesthetic_quality):
    return 0.7 * consistency + 0.2 * realism + 0.1 * aesthetic_quality

def process_jsonl_file(file_path):
    categories = defaultdict(list)
    total_objects = 0
    has_9_9 = False
    
    with open(file_path, 'r') as file:
        for line in file:
            total_objects += 1
            data = json.loads(line)
            if 9.9 in [data['consistency'], data['realism'], data['aesthetic_quality']]:
                has_9_9 = True
            subcategory = data['Subcategory']
            wiscore = calculate_wiscore(data['consistency'], data['realism'], data['aesthetic_quality'])
            if subcategory in ['Longitudinal time', 'Horizontal time']:
                categories['TIME'].append(wiscore)
            else:
                categories['SPACE'].append(wiscore)
    
    if has_9_9 or total_objects < 300:
        print(f"Skipping file {file_path}: Contains 9.9 or has less than 400 objects.")
        return None
    
    total_scores = {category: sum(scores) for category, scores in categories.items()}
    avg_scores = {category: sum(scores) / (len(scores) * 2 )if len(scores) > 0 else 0 for category, scores in categories.items()}
    
    return {
        'total': total_scores,
        'average': avg_scores
    }

def main(directory):
    results = {}
    
    for filename in os.listdir(directory):
        if filename.endswith('_scores.jsonl'):
            model_name = filename.split('_')[2]  # "Assume the filename format is 'spatio-temporal_reasoning_ModelName_scores.jsonl'"
            file_path = os.path.join(directory, filename)
            scores = process_jsonl_file(file_path)
            if scores is not None:
                results[model_name] = scores
    
    for model in MODEL_ORDER:
        if model in results:
            print(f"Model: {model}")
            print(f"  TIME - Total: {results[model]['total'].get('TIME', 0):.2f}, Average: {results[model]['average'].get('TIME', 0):.2f}")
            print(f"  SPACE - Total: {results[model]['total'].get('SPACE', 0):.2f}, Average: {results[model]['average'].get('SPACE', 0):.2f}")
        else:
            print(f"Model: {model} - No valid data found.")

main('spatio-temporal_reasoning')
