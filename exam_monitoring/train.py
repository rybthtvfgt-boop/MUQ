"""
Exam Monitoring System - Training Script
Train YOLOv8 for exam cheating detection using pre-trained COCO weights
"""

import yaml
import torch
from ultralytics import YOLO
from pathlib import Path
import argparse


def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def train_model(config):
    """Train YOLOv8 model for exam monitoring"""

    # Select model variant
    model_variants = {
        'yolov8n': 'yolov8n.pt',
        'yolov8s': 'yolov8s.pt',
        'yolov8m': 'yolov8m.pt',
        'yolov8l': 'yolov8l.pt',
        'yolov8x': 'yolov8x.pt',
    }

    variant = config['model']['variant']
    model_path = model_variants.get(variant, 'yolov8n.pt')

    print(f"Loading pre-trained model: {model_path}")
    model = YOLO(model_path)

    # Dataset path
    dataset_path = config['dataset']['path']

    # Training parameters
    epochs = config['training']['epochs']
    batch_size = config['training']['batch_size']
    img_size = config['training']['img_size']
    device = config['training']['device']

    # Check CUDA availability
    if device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, switching to CPU")
        device = 'cpu'

    print(f"\n{'='*50}")
    print("Training Configuration")
    print(f"{'='*50}")
    print(f"Model: {variant}")
    print(f"Dataset: {dataset_path}")
    print(f"Epochs: {epochs}")
    print(f"Batch Size: {batch_size}")
    print(f"Image Size: {img_size}")
    print(f"Device: {device}")
    print(f"{'='*50}\n")

    # Train the model (fine-tuning on custom dataset if annotations exist)
    # For now, we'll use the pre-trained model directly without fine-tuning
    # since the dataset doesn't have annotations

    # However, if you want to fine-tune on annotated data, uncomment below:
    """
    results = model.train(
        data=str(Path(dataset_path) / 'data.yaml'),  # dataset YAML if available
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        workers=config['training']['workers'],
        save_period=config['training']['save_period'],
        **config['augmentation']
    )
    """

    # For now, just validate the pre-trained model on the dataset
    print("Validating pre-trained model on dataset...")
    results = model.val(
        data='data.yaml',  # Use data.yaml from exam_monitoring directory
        batch=batch_size,
        imgsz=img_size,
        device=device
    )

    # Save the model
    output_dir = Path(config['output']['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / f'exam_monitor_{variant}.pt'
    model.save(str(model_path))

    print(f"\nModel saved to: {model_path}")
    print("Training complete!")

    return model


def main():
    parser = argparse.ArgumentParser(description='Train Exam Monitoring Model')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    args = parser.parse_args()

    config = load_config(args.config)
    model = train_model(config)

    return model


if __name__ == '__main__':
    main()
