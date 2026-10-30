"""
Pre-trained models for monitoring system
Uses Ultralytics YOLO for object detection
"""
import os
from ultralytics import YOLO
import cv2
import numpy as np
from django.conf import settings

# Model cache
_loaded_models = {}

def get_smoking_detection_model():
    """
    Load YOLOv8 model for smoking detection
    Uses pre-trained model from Ultralytics
    """
    model_name = 'yolov8n.pt'  # Nano version - fast and lightweight
    
    if model_name in _loaded_models:
        return _loaded_models[model_name]
    
    try:
        # Load YOLOv8n (Nano) - fast and lightweight
        model = YOLO(model_name)
        _loaded_models[model_name] = model
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def detect_smoking(image_path_or_array):
    """
    Detect smoking in an image using pre-trained YOLO model
    
    Args:
        image_path_or_array: Path to image file or numpy array
    
    Returns:
        dict: Detection results
    """
    model = get_smoking_detection_model()
    if not model:
        return {'error': 'Model not loaded'}
    
    try:
        # Run inference
        results = model(image_path_or_array, verbose=False)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                
                # COCO class for 'person' is 0
                # We'll need to train a custom model for smoking detection
                # For now, return person detections
                if cls_id == 0 and conf > 0.5:  # Person class
                    detections.append({
                        'class': 'person',
                        'confidence': conf,
                        'bbox': xyxy
                    })
        
        return {
            'success': True,
            'detections': detections,
            'count': len(detections)
        }
    except Exception as e:
        return {'error': str(e)}

def predict_from_image_file(image_path):
    """
    Make prediction from image file path
    """
    if not os.path.exists(image_path):
        return {'error': 'Image file not found'}
    
    return detect_smoking(image_path)

def predict_from_image_array(image_array):
    """
    Make prediction from numpy array
    """
    return detect_smoking(image_array)
