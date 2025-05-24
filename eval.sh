python ./WISE/gpt_eval.py \
    --json_path ./WISE/data/cultural_common_sense.json \ 
    --image_dir ./WISE/Model_name\ 
    --output_dir ./WISE/Results/ \
    --api_key "" \
    --model "gpt-4o-2024-05-13" \
    --result_full full_results.json \
    --result_scores scores_results.jsonl \
    --max_workers 48
