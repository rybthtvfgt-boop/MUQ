"""
Dangerous Activity Detection System - Prediction Script
Real-time detection of dangerous activities using YOLOv8
"""

import yaml
import torch
from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np
from collections import defaultdict
import argparse
from datetime import datetime


class DangerDetector:
    """Dangerous activity detection system"""

    def __init__(self, config_path, model_path=None):
        """Initialize danger detector"""
        self.config = self.load_config(config_path)
        self.model = self.load_model(model_path)
        self.device = self.get_device()

        # Detection thresholds
        self.confidence = self.config['model']['confidence']
        self.iou = self.config['model']['iou']

        # Dangerous activities configuration
        self.danger_levels = self.config['danger_detection']['danger_levels']

        # Activity categorization
        self.activities = self.config['activities']

        # Relevant COCO classes for danger detection
        self.relevant_classes = {
            'person': 0,
            'knife': 49,
            'scissors': 76,
            'cell_phone': 67,
            'bottle': 39,
            'chair': 56,
            'fire hydrant': 10,
            'traffic light': 9
        }

        # Alert system
        self.alerts = []
        self.last_alert_time = None

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

    def detect_dangerous_objects(self, image):
        """Detect dangerous objects in image"""
        results = self.model(image, conf=self.confidence, iou=self.iou, device=self.device)
        return results[0]

    def analyze_detections(self, results):
        """Analyze detections for dangerous indicators"""
        detections = results.boxes
        analysis = {
            'persons': 0,
            'weapons': 0,
            'dangerous_objects': [],
            'total_detections': len(detections),
            'danger_level': 'low'
        }

        for det in detections:
            class_id = int(det.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(det.conf[0])

            if class_name == 'person':
                analysis['persons'] += 1
            elif class_name in ['knife', 'scissors']:
                analysis['weapons'] += 1
                analysis['dangerous_objects'].append({
                    'type': 'weapon',
                    'name': class_name,
                    'confidence': confidence,
                    'bbox': det.xyxy[0].tolist()
                })
            elif class_name in ['cell_phone', 'bottle']:
                analysis['dangerous_objects'].append({
                    'type': 'suspicious',
                    'name': class_name,
                    'confidence': confidence,
                    'bbox': det.xyxy[0].tolist()
                })

        # Determine danger level
        if analysis['weapons'] > 0:
            analysis['danger_level'] = 'high'
        elif analysis['persons'] > self.config['danger_detection']['person_count_threshold']:
            analysis['danger_level'] = 'medium'
        elif len(analysis['dangerous_objects']) > 2:
            analysis['danger_level'] = 'medium'

        return analysis

    def assess_danger(self, analysis):
        """Assess overall danger level"""
        danger_assessment = {
            'level': analysis['danger_level'],
            'threats': [],
            'recommendation': 'continue_monitoring'
        }

        # Weapon detection
        if analysis['weapons'] > 0:
            danger_assessment['threats'].append({
                'type': 'weapon_detected',
                'severity': 'critical',
                'count': analysis['weapons']
            })
            danger_assessment['recommendation'] = 'emergency_response'

        # Too many persons
        if analysis['persons'] > self.config['danger_detection']['person_count_threshold']:
            danger_assessment['threats'].append({
                'type': 'crowd_gathering',
                'severity': 'medium',
                'count': analysis['persons']
            })
            if danger_assessment['recommendation'] == 'continue_monitoring':
                danger_assessment['recommendation'] = 'increase_monitoring'

        # Suspicious objects
        if len(analysis['dangerous_objects']) > 2:
            danger_assessment['threats'].append({
                'type': 'suspicious_objects',
                'severity': 'low',
                'count': len(analysis['dangerous_objects'])
            })

        return danger_assessment

    def trigger_alert(self, assessment, frame_info=None):
        """Trigger alert if danger detected"""
        if assessment['level'] != 'low':
            alert = {
                'timestamp': datetime.now().isoformat(),
                'level': assessment['level'],
                'threats': assessment['threats'],
                'recommendation': assessment['recommendation'],
                'frame_info': frame_info
            }

            self.alerts.append(alert)

            # Print alert
            print(f"\n{'='*50}")
            print(f"⚠️  DANGER ALERT - {assessment['level'].upper()}")
            print(f"{'='*50}")
            print(f"Time: {alert['timestamp']}")
            print(f"Recommendation: {assessment['recommendation']}")
            print(f"Threats:")
            for threat in assessment['threats']:
                print(f"  - {threat['type']} (severity: {threat['severity']})")
            print(f"{'='*50}\n")

            return alert
        return None

    def annotate_image(self, image, results, analysis, assessment):
        """Annotate image with detection results"""
        annotated = results.plot()

        # Add danger level indicator
        danger_colors = {
            'low': (0, 255, 0),      # Green
            'medium': (0, 165, 255),  # Orange
            'high': (0, 0, 255)       # Red
        }

        color = danger_colors.get(assessment['level'], (0, 255, 0))

        # Add status text
        status = f"DANGER LEVEL: {assessment['level'].upper()}"
        cv2.putText(annotated, status, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Add statistics
        stats = f"Persons: {analysis['persons']} | Weapons: {analysis['weapons']} | Objects: {len(analysis['dangerous_objects'])}"
        cv2.putText(annotated, stats, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Add recommendation
        rec = f"Action: {assessment['recommendation']}"
        cv2.putText(annotated, rec, (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return annotated

    def process_image(self, image_path, save_output=True):
        """Process a single image"""
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Error: Could not read image {image_path}")
            return None

        # Detect
        results = self.detect_dangerous_objects(image)

        # Analyze
        analysis = self.analyze_detections(results)

        # Assess danger
        assessment = self.assess_danger(analysis)

        # Trigger alert if needed
        self.trigger_alert(assessment, {'image': str(image_path)})

        # Print results
        print(f"\n{'='*50}")
        print(f"Image: {image_path.name}")
        print(f"{'='*50}")
        print(f"Persons detected: {analysis['persons']}")
        print(f"Weapons detected: {analysis['weapons']}")
        print(f"Suspicious objects: {len(analysis['dangerous_objects'])}")
        print(f"Total detections: {analysis['total_detections']}")
        print(f"Danger level: {assessment['level']}")
        print(f"Recommendation: {assessment['recommendation']}")

        # Annotate and save
        if save_output:
            annotated = self.annotate_image(image, results, analysis, assessment)
            output_dir = Path(self.config['output']['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"danger_detected_{image_path.name}"
            cv2.imwrite(str(output_path), annotated)
            print(f"Annotated image saved to: {output_path}")

        return {
            'analysis': analysis,
            'assessment': assessment,
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
        sample_rate = self.config['video']['frame_sample_rate']

        print(f"\nProcessing video: {video_path}")
        print(f"FPS: {fps}, Resolution: {width}x{height}")
        print(f"Sampling every {sample_rate} frames")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every nth frame for efficiency
            if frame_count % sample_rate == 0:
                results = self.detect_dangerous_objects(frame)
                analysis = self.analyze_detections(results)
                assessment = self.assess_danger(analysis)

                # Trigger alert if dangerous
                if assessment['level'] != 'low':
                    self.trigger_alert(assessment, {
                        'video': str(video_path),
                        'frame': frame_count
                    })

                # Annotate
                frame = self.annotate_image(frame, results, analysis, assessment)

            # Write frame
            if out:
                out.write(frame)

            # Display frame
            cv2.imshow('Danger Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()

        print(f"\nVideo processing complete. Total frames: {frame_count}")
        print(f"Total alerts triggered: {len(self.alerts)}")


def main():
    parser = argparse.ArgumentParser(description='Dangerous Activity Detection')
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
    detector = DangerDetector(args.config, args.model)

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
