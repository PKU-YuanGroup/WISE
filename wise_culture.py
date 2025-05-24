import json
import os
import argparse

def calculate_wiscore(consistency, realism, aesthetic_quality):
    return (0.7 * consistency + 0.2 * realism + 0.1 * aesthetic_quality) / 2

def process_jsonl_file(file_path):
    all_scores = []
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
                    consistency = data.get('consistency')
                    realism = data.get('realism')
                    aesthetic_quality = data.get('aesthetic_quality')

                    if not all(isinstance(val, (int, float)) for val in [consistency, realism, aesthetic_quality]):
                        print(f"Warning: File '{file_path}', Line {line_num}: One or more score values are not numeric. Skipping this line.")
                        continue

                    if 999 in [consistency, realism, aesthetic_quality]:
                        has_error = True
                    wiscore = calculate_wiscore(consistency, realism, aesthetic_quality)
                    all_scores.append(wiscore)
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
    
    if total_objects < 400:
        print(f"Skipping file {file_path}: Has less than 400 objects ({total_objects} found).")
        return None
    
    total_score = sum(all_scores)
    avg_score = total_score / len(all_scores) if len(all_scores) > 0 else 0
    
    return {
        'total': total_score,
        'average': avg_score,
        'num_processed_samples': len(all_scores)
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate a single JSONL file for model performance metrics.")
    parser.add_argument('file_path', type=str, 
                        help="The path to the JSONL file to be evaluated (e.g., cultural_common_sense_ModelName_scores.jsonl)")
    
    args = parser.parse_args()
    
    file_path = args.file_path
    
    print(f"Processing file: {file_path}")
    scores = process_jsonl_file(file_path)
    
    if scores is not None:
        model_name = os.path.basename(file_path).replace('_scores.jsonl', '')
        if 'cultural_common_sense_' in model_name:
            model_name = model_name.split('cultural_common_sense_', 1)[1]

        print(f"\n--- Evaluation Results for {model_name} ---")
        print(f"  Total WiScore: {scores['total']:.2f}")
        print(f"  Average WiScore: {scores['average']:.2f}")
        print(f"  Number of valid samples processed: {scores['num_processed_samples']}")
    else:
        print(f"\nCould not generate a valid report for '{file_path}'. Please check previous warnings/errors.")

if __name__ == "__main__":
    main()
