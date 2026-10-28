"""
Smoking Detection System - Prediction Script
Real-time smoking detection using YOLOv8
"""

import yaml
import torch
from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np
import argparse


class SmokingDetector:
    """Smoking detection system"""

    def __init__(self, config_path, model_path=None):
        """Initialize smoking detector"""
        self.config = self.load_config(config_path)
        self.model = self.load_model(model_path)
        self.device = self.get_device()

        # Detection thresholds
        self.confidence = self.config['model']['confidence']
        self.iou = self.config['model']['iou']

    def load_config(self, config_path):
        """Load configuration from YAML file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def load_model(self, model_path=None):
        """Load YOLO model"""
        if model_path and Path(model_path).exists():
            print(f"Loading custom model: {model_path}")
            return YOLO(model_path)
        else:
            # Use pre-trained model
            variant = self.config['model']['variant']
            model_variants = {
                'yolov8n': 'yolov8n.pt',
                'yolov8s': 'yolov8s.pt',
                'yolov8m': 'yolov8m.pt',
                'yolov8l': 'yolov8l.pt',
                'yolov8x': 'yolov8x.pt',
            }
            model_path = model_variants.get(variant, 'yolov8n.pt')
            print(f"Loading pre-trained model: {model_path}")
            return YOLO(model_path)

    def get_device(self):
        """Get computation device"""
        device = self.config['training']['device']
        if device == 'cuda' and not torch.cuda.is_available():
            print("CUDA not available, using CPU")
            return 'cpu'
        return device

    def detect_smoking(self, image):
        """Detect smoking in image"""
        results = self.model(image, conf=self.confidence, iou=self.iou, device=self.device)
        return results[0]

    def analyze_detections(self, results):
        """Analyze detections for smoking"""
        detections = results.boxes
        analysis = {
            'smoking': 0,
            'notsmoking': 0,
            'total_detections': len(detections),
            'is_smoking': False
        }

        for det in detections:
            class_id = int(det.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(det.conf[0])

            if class_name == 'smoking':
                analysis['smoking'] += 1
                analysis['is_smoking'] = True
            elif class_name == 'notsmoking':
                analysis['notsmoking'] += 1

        return analysis

    def annotate_image(self, image, results, analysis):
        """Annotate image with detection results"""
        annotated = results.plot()

        # Add status text
        if analysis['is_smoking']:
            status = "⚠️ SMOKING DETECTED"
            color = (0, 0, 255)  # Red
        else:
            status = "✅ NO SMOKING"
            color = (0, 255, 0)  # Green

        cv2.putText(annotated, status, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Add statistics
        stats = f"Smoking: {analysis['smoking']} | Not Smoking: {analysis['notsmoking']}"
        cv2.putText(annotated, stats, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return annotated

    def process_image(self, image_path, save_output=True):
        """Process a single image"""
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Error: Could not read image {image_path}")
            return None

        # Detect
        results = self.detect_smoking(image)

        # Analyze
        analysis = self.analyze_detections(results)

        # Print results
        print(f"\n{'='*50}")
        print(f"Image: {image_path.name}")
        print(f"{'='*50}")
        print(f"Smoking detected: {analysis['smoking']}")
        print(f"Not smoking: {analysis['notsmoking']}")
        print(f"Total detections: {analysis['total_detections']}")
        print(f"Is smoking: {'YES' if analysis['is_smoking'] else 'NO'}")

        # Annotate and save
        if save_output:
            annotated = self.annotate_image(image, results, analysis)
            output_dir = Path(self.config['output']['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"smoking_detected_{image_path.name}"
            cv2.imwrite(str(output_path), annotated)
            print(f"Annotated image saved to: {output_path}")

        return {
            'analysis': analysis,
            'results': results
        }

    def process_video(self, video_path, output_path=None):
        """Process video file for real-time monitoring"""
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Setup video writer
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        else:
            out = None

        frame_count = 0
        smoking_count = 0

        print(f"\nProcessing video: {video_path}")
        print(f"FPS: {fps}, Resolution: {width}x{height}")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every 5th frame for efficiency
            if frame_count % 5 == 0:
                results = self.detect_smoking(frame)
                analysis = self.analyze_detections(results)

                if analysis['is_smoking']:
                    smoking_count += 1
                    print(f"Frame {frame_count}: Smoking detected!")

                # Annotate
                frame = self.annotate_image(frame, results, analysis)

            # Write frame
            if out:
                out.write(frame)

            # Display frame
            cv2.imshow('Smoking Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()

        print(f"\nVideo processing complete. Total frames: {frame_count}")
        print(f"Smoking detected in: {smoking_count} frames")


def main():
    parser = argparse.ArgumentParser(description='Smoking Detection')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to trained model weights')
    parser.add_argument('--image', type=str, default=None,
                        help='Path to image file')
    parser.add_argument('--video', type=str, default=None,
                        help='Path to video file')
    parser.add_argument('--output', type=str, default=None,
                        help='Output path for annotated results')
    args = parser.parse_args()

    # Initialize detector
    detector = SmokingDetector(args.config, args.model)

    # Process image
    if args.image:
        detector.process_image(Path(args.image))

    # Process video
    elif args.video:
        output_path = Path(args.output) if args.output else None
        detector.process_video(Path(args.video), output_path)

    else:
        print("Please provide --image or --video argument")


if __name__ == '__main__':
    main()
