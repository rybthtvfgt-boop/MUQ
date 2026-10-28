"""
Exam Monitoring System - Evaluation Script
Evaluate trained model on test dataset
"""

import yaml
import torch
from ultralytics import YOLO
from pathlib import Path
import numpy as np
import cv2
import argparse


def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def evaluate_model(config, model_path=None):
    """Evaluate model on test dataset"""

    # Load model
    if model_path:
        model = YOLO(model_path)
    else:
        # Use pre-trained model
        variant = config['model']['variant']
        model_variants = {
            'yolov8n': 'yolov8n.pt',
            'yolov8s': 'yolov8s.pt',
            'yolov8m': 'yolov8m.pt',
            'yolov8l': 'yolov8l.pt',
            'yolov8x': 'yolov8x.pt',
        }
        model_path = model_variants.get(variant, 'yolov8n.pt')
        model = YOLO(model_path)

    # Dataset path
    dataset_path = Path(config['dataset']['path'])
    test_path = dataset_path / config['dataset']['test']

    print(f"\n{'='*50}")
    print("Model Evaluation")
    print(f"{'='*50}")
    print(f"Model: {model_path}")
    print(f"Test Dataset: {test_path}")
    print(f"{'='*50}\n")

    # Validate on test set
    device = config['training']['device']
    if device == 'cuda' and not torch.cuda.is_available():
        device = 'cpu'

    results = model.val(
        data='data.yaml',  # Use data.yaml from exam_monitoring directory
        split='test',
        batch=config['training']['batch_size'],
        imgsz=config['training']['img_size'],
        device=device,
        conf=config['model']['confidence'],
        iou=config['model']['iou']
    )

    # Print results
    print("\nEvaluation Results:")
    print(f"mAP50: {results.box.map50:.4f}")
    print(f"mAP50-95: {results.box.map:.4f}")
    print(f"Precision: {results.box.mp:.4f}")
    print(f"Recall: {results.box.mr:.4f}")

    # Detailed class-wise metrics
    print("\nClass-wise Detection Statistics:")
    class_names = model.names
    for class_id in range(len(class_names)):
        class_name = class_names[class_id]
        print(f"{class_name}: AP50={results.box.maps[class_id]:.4f}")

    return results


def run_inference_on_samples(config, model_path=None, num_samples=10):
    """Run inference on sample images from test set"""

    # Load model
    if model_path:
        model = YOLO(model_path)
    else:
        variant = config['model']['variant']
        model_variants = {
            'yolov8n': 'yolov8n.pt',
            'yolov8s': 'yolov8s.pt',
            'yolov8m': 'yolov8m.pt',
            'yolov8l': 'yolov8l.pt',
            'yolov8x': 'yolov8x.pt',
        }
        model_path = model_variants.get(variant, 'yolov8n.pt')
        model = YOLO(model_path)

    # Get sample images
    dataset_path = Path(config['dataset']['path'])
    test_path = dataset_path / config['dataset']['test']

    image_files = list(test_path.glob('*.jpg'))[:num_samples]

    print(f"\nRunning inference on {len(image_files)} sample images...")

    for img_path in image_files:
        # Run inference
        results = model(str(img_path), conf=config['model']['confidence'])

        # Count detections
        detections = results[0].boxes
        print(f"\n{img_path.name}:")
        print(f"  Total detections: {len(detections)}")

        # Count by class
        class_counts = {}
        for det in detections:
            class_id = int(det.cls[0])
            class_name = model.names[class_id]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        for class_name, count in class_counts.items():
            print(f"  {class_name}: {count}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate Exam Monitoring Model')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to trained model weights')
    parser.add_argument('--samples', type=int, default=10,
                        help='Number of sample images to test')
    args = parser.parse_args()

    config = load_config(args.config)

    # Run evaluation
    results = evaluate_model(config, args.model)

    # Run inference on samples
    run_inference_on_samples(config, args.model, args.samples)

    return results


if __name__ == '__main__':
    main()
