#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

: "${IMAGE_DIR:?Please set IMAGE_DIR to the directory containing 1.png ... 1000.png}"

VLLM_API_BASE="${VLLM_API_BASE:-http://127.0.0.1:8000/v1}"
VLLM_API_KEY="${VLLM_API_KEY:-EMPTY}"
JUDGE_MODEL="${JUDGE_MODEL:-Qwen3.5-35B-A3B}"
MAX_WORKERS="${MAX_WORKERS:-96}"

python vllm_eval.py \
    --json_path data_verified/cultural_common_sense_verified.json \
    --output_dir "${IMAGE_DIR}/Results-qwen35/cultural_common_sense" \
    --image_dir "${IMAGE_DIR}" \
    --api_key "${VLLM_API_KEY}" \
    --api_base "${VLLM_API_BASE}" \
    --model "${JUDGE_MODEL}" \
    --result_full "${IMAGE_DIR}/Results-qwen35/cultural_common_sense_full_results.json" \
    --result_scores "${IMAGE_DIR}/Results-qwen35/cultural_common_sense_scores_results.jsonl" \
    --max_workers "${MAX_WORKERS}"

python vllm_eval.py \
    --json_path data_verified/spatio-temporal_reasoning_verified.json \
    --output_dir "${IMAGE_DIR}/Results-qwen35/spatio-temporal_reasoning" \
    --image_dir "${IMAGE_DIR}" \
    --api_key "${VLLM_API_KEY}" \
    --api_base "${VLLM_API_BASE}" \
    --model "${JUDGE_MODEL}" \
    --result_full "${IMAGE_DIR}/Results-qwen35/spatio-temporal_reasoning_full_results.json" \
    --result_scores "${IMAGE_DIR}/Results-qwen35/spatio-temporal_reasoning_scores_results.jsonl" \
    --max_workers "${MAX_WORKERS}"

python vllm_eval.py \
    --json_path data_verified/natural_science_verified.json \
    --output_dir "${IMAGE_DIR}/Results-qwen35/natural_science" \
    --image_dir "${IMAGE_DIR}" \
    --api_key "${VLLM_API_KEY}" \
    --api_base "${VLLM_API_BASE}" \
    --model "${JUDGE_MODEL}" \
    --result_full "${IMAGE_DIR}/Results-qwen35/natural_science_full_results.json" \
    --result_scores "${IMAGE_DIR}/Results-qwen35/natural_science_scores_results.jsonl" \
    --max_workers "${MAX_WORKERS}"

python calculate_verified.py \
    "${IMAGE_DIR}/Results-qwen35/cultural_common_sense_scores_results.jsonl" \
    "${IMAGE_DIR}/Results-qwen35/natural_science_scores_results.jsonl" \
    "${IMAGE_DIR}/Results-qwen35/spatio-temporal_reasoning_scores_results.jsonl" \
    --category all
