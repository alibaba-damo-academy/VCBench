#!/usr/bin/env python3
"""
Answer evaluation script for VCBench dataset.
Compares model predictions against ground truth answers and calculates accuracy metrics.
"""

import json
import os
from http import HTTPStatus
from tqdm import tqdm
from pprint import pprint
import argparse
import dashscope


class AnswerEvaluator:
    """Handles evaluation of model answers against ground truth."""
    
    def __init__(self):
        self.dashscope_key = os.environ.get('DASHSCOPE_KEY')
        if not self.dashscope_key:
            raise ValueError("DASHSCOPE_KEY environment variable not set")

    def clean_response(self, model_response: str, correct_answer: str) -> tuple:
        """
        Evaluates whether a model response matches the correct answer.
        
        Args:
            model_response: The model's prediction
            correct_answer: The ground truth answer
            
        Returns:
            tuple: (success_flag, evaluation_result)
        """
        messages = [{
            "role": "user",
            "content": f"""
                You are an answer evaluator. I will give you a response and an answer.
                Please tell me whether this response is correct or wrong. Just answer yes or no.
                
                Examples:
                Response: The figure that cannot be folded into a cube is: C. <image>
                Correct Answer: B
                Evaluation: no
                
                Response: The unfolded shape of the cube is: B. <image>
                Correct Answer: B
                Evaluation: yes
                
                Now evaluate:
                Response: {model_response}
                Correct Answer: {correct_answer}"""
        }]

        try:
            response = dashscope.Generation.call(
                api_key=self.dashscope_key,
                model="qwen-plus",
                messages=messages,
                result_format="message",
                temperature=0.0
            )
            
            if response.status_code == HTTPStatus.OK:
                return True, response.output.choices[0].message.content.lower()
            return False, response.message
            
        except Exception as e:
            return False, str(e)

    def is_correct(self, evaluation: str) -> bool:
        """Determines if evaluation response indicates correct answer."""
        return evaluation in {'yes', 'yes.', 'y', 'correct', 'correct.', 'YES', 'YES.', 'Yes.', 'Yes'}


class VCBenchEvaluator:
    """Main evaluation pipeline for VCBench dataset."""
    
    QUESTION_TYPES = [
        'angle', 'calendar', 'clock', 'cube', 'direction',
        'location', 'move', 'observe', 'organize', 'pattern',
        'place', 'quad', 'reasoning', 'rectangular', 'shape',
        'triangle', 'weight'
    ]

    def __init__(self):
        self.evaluator = AnswerEvaluator()

    def load_ground_truth(self, file_path: str) -> tuple:
        """Loads ground truth answers and question types."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            answers = [item["answer"] for item in data]
            question_types = [item["question_type"] for item in data]
        return answers, question_types

    def evaluate_predictions(self, pred_file: str, gt_file: str) -> dict:
        """
        Evaluates predictions against ground truth.
        
        Args:
            pred_file: Path to predictions JSONL file
            gt_file: Path to ground truth JSON file
            
        Returns:
            dict: Evaluation metrics
        """
        answers, question_types = self.load_ground_truth(gt_file)
        
        metrics = {
            'total': 0,
            'correct': 0,
            'type_counts': {qt: 0 for qt in self.QUESTION_TYPES},
            'type_correct': {qt: 0 for qt in self.QUESTION_TYPES}
        }

        with open(pred_file, 'r') as f:
            for line in tqdm(f, desc="Evaluating predictions"):
                try:
                    record = json.loads(line)
                    idx = record['id'] - 1  # Convert to 0-based index
                    
                    result = self.evaluator.clean_response(
                        record['pred_answer'],
                        answers[idx]
                    )
                    
                    if not result[0]:
                        print(f"Evaluation failed for ID {idx+1}: {result[1]}")
                        continue
                        
                    q_type = question_types[idx]
                    metrics['type_counts'][q_type] += 1
                    metrics['total'] += 1
                    
                    if self.evaluator.is_correct(result[1]):
                        metrics['correct'] += 1
                        metrics['type_correct'][q_type] += 1
                        
                    print(f"Current accuracy: {metrics['correct']/metrics['total']:.2f}")
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Skipping malformed record: {e}")

        return metrics

    def calculate_metrics(self, metrics: dict) -> dict:
        """Calculates final evaluation metrics."""
        return {
            'overall_accuracy': metrics['correct'] / metrics['total'],
            'type_accuracy': {
                qt: metrics['type_correct'][qt] / count
                for qt, count in metrics['type_counts'].items()
                if count > 0
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate VCBench model predictions',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-p', '--pred_file',
        type=str,
        default='predictions.jsonl',
        help='Path to predictions JSONL file'
    )
    parser.add_argument(
        '-g', '--gt_file',
        type=str,
        default='data/VCBench_with_answer.json',
        help='Path to ground truth JSON file'
    )
    args = parser.parse_args()

    print(f"Evaluating predictions from: {args.pred_file}")
    print(f"Using ground truth from: {args.gt_file}")

    evaluator = VCBenchEvaluator()
    metrics = evaluator.evaluate_predictions(args.pred_file, args.gt_file)
    results = evaluator.calculate_metrics(metrics)

    print("\nFinal Results:")
    print(f"Overall Accuracy: {results['overall_accuracy']:.2%}")
    print("\nPer-Type Accuracy:")
    pprint(results['type_accuracy'])


if __name__ == '__main__':
    main()