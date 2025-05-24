import json
import os
import argparse 
from collections import defaultdict


def calculate_wiscore(consistency, realism, aesthetic_quality):
    return (0.7 * consistency + 0.2 * realism + 0.1 * aesthetic_quality)/2

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
                    subcategory = data.get('Subcategory')

                    if not all(isinstance(val, (int, float)) for val in [consistency, realism, aesthetic_quality]) or not isinstance(subcategory, str):
                        print(f"Warning: File '{file_path}', Line {line_num}: Missing or invalid score/subcategory data. Skipping this line.")
                        continue

                    wiscore = calculate_wiscore(consistency, realism, aesthetic_quality)
                    
                    if subcategory in ['Longitudinal time', 'Horizontal time']:
                        categories['TIME'].append(wiscore)
                    else:
                        categories['SPACE'].append(wiscore)
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
        'num_samples_per_category': {category: len(scores) for category, scores in categories.items()} # Added count per category
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate a single JSONL file for spatio-temporal reasoning scores.")
    parser.add_argument('file_path', type=str, 
                        help="The path to the JSONL file to be evaluated (e.g., spatio-temporal_reasoning_ModelName_scores.jsonl)")
    
    args = parser.parse_args() 
    
    file_path = args.file_path
    
    print(f"Processing file: {file_path}")
    results = process_jsonl_file(file_path)
    
    if results is not None:
        model_name = os.path.basename(file_path).replace('_scores.jsonl', '')
        if 'spatio-temporal_reasoning_' in model_name:
            model_name = model_name.split('spatio-temporal_reasoning_', 1)[1]

        print(f"\n--- Evaluation Results for Model: {model_name} ---")
        
        print(f"  TIME Category:")
        print(f"    Total WiScore: {results['total'].get('TIME', 0):.2f}")
        print(f"    Average WiScore: {results['average'].get('TIME', 0):.2f}")
        print(f"    Number of samples: {results['num_samples_per_category'].get('TIME', 0)}\n")

        print(f"  SPACE Category:")
        print(f"    Total WiScore: {results['total'].get('SPACE', 0):.2f}")
        print(f"    Average WiScore: {results['average'].get('SPACE', 0):.2f}")
        print(f"    Number of samples: {results['num_samples_per_category'].get('SPACE', 0)}\n")

    else:
        print(f"\nCould not generate a valid report for '{file_path}'. Please check previous warnings/errors.")

if __name__ == "__main__":
    main()
