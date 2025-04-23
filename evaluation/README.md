

# VCBench Model Evaluation Guide

## Overview
VCBench provides a standardized framework for evaluating vision-language models. This document outlines the procedures for both standard evaluation and GPT-assisted evaluation of your model's outputs.

## 1. Standard Evaluation

### 1.1 Output Format Requirements
Models must produce outputs in JSONL format with the following structure:
```json
{"id": <int>, "pred_answer": "<answer_letter>"}
{"id": <int>, "pred_answer": "<answer_letter>"}
...
```

**Example File (`submit.jsonl`):**
```json
{"id": 1, "pred_answer": "A"}
{"id": 2, "pred_answer": "B"}
{"id": 3, "pred_answer": "C"}
```

### 1.2 Evaluation Procedure
1. Ensure your predictions file follows the specified format
2. Run the evaluation script:
   ```bash
   python evaluate_vcbench.py -p ./path/to/predictions.jsonl -g ./path/to/VCBench_with_answer.json
   ```
`VCBench_with_answer.json` is the ground truth file which can be downloaded from [here](https://huggingface.co/datasets/cloudcatcher2/VCBench/resolve/main/VCBench_with_answer.json).

## 2. GPT-Assisted Evaluation

### 2.1 Output Format Requirements
For natural language responses, use this JSONL format:
```json
{"id": <int>, "pred_answer": "<natural_language_response>"}
{"id": <int>, "pred_answer": "<natural_language_response>"}
...
```

**Example File (`nl_predictions.jsonl`):**
```json
{"id": 1, "pred_answer": "The correct answer is A"}
{"id": 2, "pred_answer": "After careful analysis, option B appears correct"}
{"id": 3, "pred_answer": "C is the right choice"}
```

### 2.2 Environment Setup
Set your Dashscope API key:
   ```bash
   export DASHSCOPE_KEY="your_api_key_here"
   ```

### 2.3 Evaluation Procedure
```bash
python evaluate_vcbench_by_gpt.py -p ./path/to/nl_predictions.jsonl -g ./path/to/VCBench_with_answer.json
```

## 3. Expected Output
Both evaluation scripts will provide:
- Overall accuracy percentage
- Per-question-type accuracy breakdown
- Progress updates during evaluation

