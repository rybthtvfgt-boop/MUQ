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

# COCO class names
COCO_CLASSES = {
    0: 'person',
    67: 'cell phone',
    73: 'book',
    63: 'laptop'
}

# Construction hazard class names (from Construction-Hazard-Detection model)
HAZARD_CLASSES = {
    0: 'person_without_helmet',
    1: 'person_without_vest',
    2: 'worker_near_machinery',
    3: 'worker_in_restricted_area',
    4: 'machinery_near_pole',
    5: 'forklift',
    6: 'safety_cone'
}

def get_exam_monitoring_model():
    """
    Load YOLOv5 model for exam cheating detection
    Uses pre-trained YOLOv5n for detecting:
    - person, cell phone, book, laptop
    """
    model_name = 'yolov5n.pt'  # Nano version - fast and lightweight
    
    if model_name in _loaded_models:
        return _loaded_models[model_name]
    
    try:
        # Load YOLOv5n (Nano) - fast and lightweight
        model = YOLO(model_name)
        _loaded_models[model_name] = model
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

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

def get_danger_detection_model():
    """
    Load YOLO model for danger/hazard detection
    Uses YOLO26 or YOLO11 from HuggingFace for detecting:
    - Workers without helmets
    - Workers without safety vests
    - Workers near machinery
    - Workers in restricted areas
    - Machinery near utility poles
    - Forklifts
    """
    model_name = 'yolov11n.pt'  # Use YOLO11n as base (lightweight)
    
    if model_name in _loaded_models:
        return _loaded_models[model_name]
    
    try:
        # Load YOLO11n (Nano) - fast and lightweight
        # Note: For production, download the trained Construction-Hazard-Detection model
        # from HuggingFace: architchitte/Construction-Hazard-Detection
        model = YOLO(model_name)
        _loaded_models[model_name] = model
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def detect_exam_cheating(image_path_or_array):
    """
    Detect cheating objects in exam using pre-trained YOLO model
    
    Args:
        image_path_or_array: Path to image file or numpy array
    
    Returns:
        dict: Detection results including cheating objects
    """
    model = get_exam_monitoring_model()
    if not model:
        return {'error': 'Model not loaded'}
    
    try:
        # Run inference
        results = model(image_path_or_array, verbose=False)
        
        # Parse results
        detections = []
        cheating_objects = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                
                class_name = COCO_CLASSES.get(cls_id, f'unknown_{cls_id}')
                
                # Detect potential cheating objects
                if cls_id in [67, 73, 63]:  # cell phone, book, laptop
                    cheating_objects.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': xyxy,
                        'is_cheating_risk': True
                    })
                elif cls_id == 0 and conf > 0.5:  # Person
                    detections.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': xyxy,
                        'is_cheating_risk': False
                    })
        
        return {
            'success': True,
            'detections': detections,
            'cheating_objects': cheating_objects,
            'person_count': len(detections),
            'cheating_risk_count': len(cheating_objects),
            'has_cheating': len(cheating_objects) > 0
        }
    except Exception as e:
        return {'error': str(e)}

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

def detect_danger(image_path_or_array):
    """
    Detect hazards and dangers in an image using pre-trained YOLO model

    Args:
        image_path_or_array: Path to image file or numpy array

    Returns:
        dict: Detection results including hazard objects
    """
    model = get_danger_detection_model()
    if not model:
        return {'error': 'Model not loaded'}

    try:
        # Run inference
        results = model(image_path_or_array, verbose=False)

        # Parse results
        detections = []
        hazard_objects = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()

                # Map to hazard classes
                class_name = HAZARD_CLASSES.get(cls_id, f'unknown_{cls_id}')

                # Detect potential hazards
                # For now, we use COCO classes - person, truck, car, bus (near machinery)
                if cls_id in [0, 2, 3, 5, 7] and conf > 0.5:  # person, car, motorcycle, bus, truck
                    is_hazard = cls_id != 0  # Vehicles are hazards
                    hazard_info = {
                        'class': class_name,
                        'confidence': conf,
                        'bbox': xyxy,
                        'is_hazard': is_hazard
                    }
                    detections.append(hazard_info)
                    if is_hazard:
                        hazard_objects.append(hazard_info)

        return {
            'success': True,
            'detections': detections,
            'hazard_objects': hazard_objects,
            'hazard_count': len(hazard_objects),
            'has_danger': len(hazard_objects) > 0
        }
    except Exception as e:
        return {'error': str(e)}

def predict_from_image_file(image_path, model_type='exam'):
    """
    Make prediction from image file path

    Args:
        image_path: Path to image file
        model_type: 'exam' for cheating detection, 'smoking' for smoking detection, 'danger' for hazard detection
    """
    if not os.path.exists(image_path):
        return {'error': 'Image file not found'}

    if model_type == 'exam':
        return detect_exam_cheating(image_path)
    elif model_type == 'danger':
        return detect_danger(image_path)
    else:
        return detect_smoking(image_path)

def predict_from_image_array(image_array, model_type='exam'):
    """
    Make prediction from numpy array

    Args:
        image_array: numpy array of image
        model_type: 'exam' for cheating detection, 'smoking' for smoking detection, 'danger' for hazard detection
    """
    if model_type == 'exam':
        return detect_exam_cheating(image_array)
    elif model_type == 'danger':
        return detect_danger(image_array)
    else:
        return detect_smoking(image_array)
