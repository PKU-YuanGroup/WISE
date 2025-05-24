import json
import os
import argparse
from collections import defaultdict

def calculate_wiscore(consistency, realism, aesthetic_quality):
    return (0.7 * consistency + 0.2 * realism + 0.1 * aesthetic_quality) / 2

def process_jsonl_file(file_path):
    categories = defaultdict(list)
    total_objects = 0
    has_error = False
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                total_objects += 1
                try:
                    data = json.loads(line)
                    
                    if 999 in [data.get('consistency'), data.get('realism'), data.get('aesthetic_quality')]:
                        has_error = True
                    
                    consistency = data.get('consistency')
                    realism = data.get('realism')
                    aesthetic_quality = data.get('aesthetic_quality')

                    if not all(isinstance(val, (int, float)) for val in [consistency, realism, aesthetic_quality]):
                        print(f"Warning: File '{file_path}', Line {line_num}: One or more score values are not numeric. Skipping this line for category calculation.")
                        continue

                    prompt_id = data.get('prompt_id', 0)
                    if 701 <= prompt_id <= 800:
                        category = 'Biology'
                    elif 801 <= prompt_id <= 900:
                        category = 'Physics'
                    elif 901 <= prompt_id <= 1000:
                        category = 'Chemistry'
                    else: # If a prompt_id is outside the defined ranges, it's not included in the categories.
                        continue # Skip this line if category is not recognized
                    
                    wiscore = calculate_wiscore(consistency, realism, aesthetic_quality)
                    categories[category].append(wiscore)
                except json.JSONDecodeError:
                    print(f"Warning: File '{file_path}', Line {line_num}: Invalid JSON format. Skipping this line.")
                except KeyError as e:
                    print(f"Warning: File '{file_path}', Line {line_num}: Missing expected key '{e}'. Skipping this line.")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None
    
    if has_error:
        print(f"Skipping file {file_path}: Contains 999 in scores.")
        return None
    
    if total_objects < 300: 
        print(f"Skipping file {file_path}: Has less than 300 objects ({total_objects} found).")
        return None
    
    total_scores = {category: sum(scores) for category, scores in categories.items()}
    avg_scores = {category: sum(scores) / len(scores) if len(scores) > 0 else 0 for category, scores in categories.items()}
    
    return {
        'total': total_scores,
        'average': avg_scores,
        'category_sample_counts': {category: len(scores) for category, scores in categories.items()}
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate a single JSONL file, categorizing scores by prompt_id for Natural Science models.")
    parser.add_argument('file_path', type=str, 
                        help="The path to the JSONL file to be evaluated (e.g., natural_science_ModelName_scores.jsonl)")
    
    args = parser.parse_args()
    
    file_path = args.file_path
    
    print(f"Processing file: {file_path}")
    results = process_jsonl_file(file_path)
    
    if results is not None:
        model_name = os.path.basename(file_path).replace('_scores.jsonl', '')
        if 'natural_science_' in model_name:
            model_name = model_name.split('natural_science_', 1)[1]

        print(f"\n--- Evaluation Results for Model: {model_name} ---")
        
        ordered_categories = ['Biology', 'Physics', 'Chemistry'] 

        for category in ordered_categories:
            total_score = results['total'].get(category, 0)
            avg_score = results['average'].get(category, 0)
            sample_count = results['category_sample_counts'].get(category, 0)
            print(f"  Category: {category}")
            print(f"    Total WiScore: {total_score:.2f}")
            print(f"    Average WiScore: {avg_score:.2f}")
            print(f"    Number of samples: {sample_count}\n")
    else:
        print(f"\nCould not generate a valid report for '{file_path}'. Please check previous warnings/errors.")

if __name__ == "__main__":
    main()
