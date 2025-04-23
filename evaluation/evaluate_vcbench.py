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



class VCBenchEvaluator:
    """Main evaluation pipeline for VCBench dataset."""
    
    QUESTION_TYPES = [
        'angle', 'calendar', 'clock', 'cube', 'direction',
        'location', 'move', 'observe', 'organize', 'pattern',
        'place', 'quad', 'reasoning', 'rectangular', 'shape',
        'triangle', 'weight'
    ]

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
            for line in f:
                try:
                    record = json.loads(line)
                    idx = record['id'] - 1  # Convert to 0-based index
                        
                    q_type = question_types[idx]
                    metrics['type_counts'][q_type] += 1
                    metrics['total'] += 1
                    
                    if record['pred_answer'] == answers[idx]:
                        metrics['correct'] += 1
                        metrics['type_correct'][q_type] += 1
                                            
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