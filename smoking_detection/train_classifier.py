"""
Smoking Detection System - Classification Training
Train image classifier for smoking detection (no annotations needed)
"""

import yaml
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from pathlib import Path
from PIL import Image
import argparse
import numpy as np


class SmokingDataset(Dataset):
    """Custom dataset for smoking classification"""

    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.classes = ['notsmoking', 'smoking']
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.samples = []

        # Load all images
        for class_name in self.classes:
            class_dir = self.root_dir / class_name
            if class_dir.exists():
                for img_path in class_dir.glob('*.jpg'):
                    self.samples.append((img_path, self.class_to_idx[class_name]))
                for img_path in class_dir.glob('*.JPG'):
                    self.samples.append((img_path, self.class_to_idx[class_name]))

        print(f"Loaded {len(self.samples)} images from {root_dir}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, label


def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def train_classifier(config):
    """Train image classifier for smoking detection"""

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Load datasets
    train_dataset = SmokingDataset(
        config['dataset']['path'] / config['dataset']['train'],
        transform=train_transform
    )

    val_dataset = SmokingDataset(
        config['dataset']['path'] / config['dataset']['val'],
        transform=val_transform
    )

    # Data loaders
    batch_size = config['training']['batch_size']
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    # Load pre-trained model (ResNet18)
    print("Loading pre-trained ResNet18 model...")
    model = models.resnet18(pretrained=True)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)  # 2 classes: smoking, notsmoking

    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    print(f"\n{'='*50}")
    print("Training Configuration")
    print(f"{'='*50}")
    print(f"Model: ResNet18")
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    print(f"Batch Size: {batch_size}")
    print(f"Device: {device}")
    print(f"{'='*50}\n")

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    # Training
    epochs = config['training']['epochs']
    best_acc = 0.0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total

        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_loss = val_loss / len(val_loader)
        val_acc = 100 * correct / total

        scheduler.step()

        print(f"Epoch [{epoch+1}/{epochs}]")
        print(f"  Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")

        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            output_dir = Path(config['output']['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            model_path = output_dir / 'smoking_classifier.pth'
            torch.save(model.state_dict(), str(model_path))
            print(f"  ✅ Best model saved! Accuracy: {best_acc:.2f}%")

    print(f"\nTraining complete! Best validation accuracy: {best_acc:.2f}%")
    return model


def main():
    parser = argparse.ArgumentParser(description='Train Smoking Classifier')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    args = parser.parse_args()

    config = load_config(args.config)
    model = train_classifier(config)

    return model


if __name__ == '__main__':
    main()
