"""
Monitoring System Views - AI Training and Inference
"""
import os
import json
import subprocess
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingSession, TrainedModel

# Configuration
DATASET_PATH = os.environ.get('DATASET_PATH', '/app/dataset')
TRAINING_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'train_monitoring_model.py')
LOG_FILE = os.path.join(DATASET_PATH, 'training_log.json')
MODEL_SAVE_PATH = os.path.join(DATASET_PATH, 'trained_model')

# Ensure dataset directory exists
os.makedirs(DATASET_PATH, exist_ok=True)
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)

# Global training state
training_status = {
    'is_training': False,
    'progress': 0,
    'current_stage': '',
    'logs': [],
    'error': None,
    'session_id': None
}

def get_training_status():
    """Get current training status from log file"""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                logs = log_data.get('logs', [])
                if logs:
                    last_log = logs[-1]
                    return {
                        'is_training': training_status['is_training'],
                        'progress': training_status['progress'],
                        'current_stage': last_log.get('message', ''),
                        'logs': logs[-10:],  # Last 10 logs
                        'error': training_status['error']
                    }
        except Exception as e:
            print(f"Error reading log file: {e}")

    return training_status

def run_training(session_id, dataset_path, model_save_path):
    """Run training in background thread"""
    global training_status
    training_status['is_training'] = True
    training_status['progress'] = 0
    training_status['current_stage'] = 'Starting training...'
    training_status['error'] = None

    try:
        # Update session status
        session = TrainingSession.objects.get(id=session_id)
        session.status = 'running'
        session.current_stage = 'Starting training...'
        session.save()

        # Check if dataset has images
        def count_images(directory):
            if not os.path.exists(directory):
                return 0
            count = 0
            for root, dirs, files in os.walk(directory):
                count += len([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            return count

        total_images = count_images(dataset_path)
        if total_images == 0:
            training_status['error'] = 'Dataset is empty. No training images found.'
            training_status['current_stage'] = 'Training failed (empty dataset)'
            session.status = 'failed'
            session.error_message = 'Dataset is empty. Please upload training images first.'
            session.save()
            return

        # Create model save directory if it doesn't exist
        os.makedirs(model_save_path, exist_ok=True)

        # Run the training script with custom dataset path
        result = subprocess.run(
            ['python', TRAINING_SCRIPT, '--dataset', dataset_path, '--output', model_save_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=3600  # 1 hour timeout
        )

        if result.returncode == 0:
            training_status['progress'] = 100
            training_status['current_stage'] = 'Training completed successfully'
            session.progress = 100
            session.status = 'completed'
            session.current_stage = 'Training completed successfully'
            session.save()
        else:
            training_status['error'] = result.stderr
            training_status['current_stage'] = 'Training failed'
            session.status = 'failed'
            session.error_message = result.stderr
            session.save()

    except subprocess.TimeoutExpired:
        training_status['error'] = 'Training timed out'
        training_status['current_stage'] = 'Training failed (timeout)'
        session.status = 'failed'
        session.error_message = 'Training timed out'
        session.save()
    except Exception as e:
        training_status['error'] = str(e)
        training_status['current_stage'] = 'Training failed (error)'
        session.status = 'failed'
        session.error_message = str(e)
        session.save()
    finally:
        training_status['is_training'] = False

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_training(request):
    """Start AI model training"""
    global training_status

    # Check if there's a running session in the database
    running_session = TrainingSession.objects.filter(status='running').first()
    if running_session:
        return Response({
            'error': 'Training is already in progress'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get model name and dataset path from request
    model_name = request.data.get('model_name', 'Smoking Detection Model')
    custom_dataset_path = request.data.get('dataset_path')

    # Use custom dataset path if provided, otherwise use default
    dataset_path = custom_dataset_path if custom_dataset_path else DATASET_PATH

    # Check if dataset exists
    if not os.path.exists(dataset_path):
        return Response({
            'error': f'Dataset path not found: {dataset_path}'
        }, status=status.HTTP_404_NOT_FOUND)

    # Create model save path based on model name
    model_save_path = os.path.join(os.path.dirname(DATASET_PATH), f'trained_models/{model_name.replace(" ", "_")}')

    # Create trained model record
    trained_model = TrainedModel.objects.create(
        name=model_name,
        version='1.0',
        accuracy=0.0,
        model_path=model_save_path
    )

    # Create training session
    session = TrainingSession.objects.create(
        model=trained_model,
        status='running',
        progress=0,
        current_stage='Starting training...'
    )

    training_status['session_id'] = session.id
    training_status['is_training'] = True

    # Start training in background thread with custom dataset path
    thread = threading.Thread(target=run_training, args=(session.id, dataset_path, model_save_path))
    thread.daemon = True
    thread.start()

    return Response({
        'message': 'Training started',
        'dataset_path': dataset_path,
        'model_save_path': model_save_path,
        'session_id': session.id,
        'model_name': model_name
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_training_progress(request):
    """Get training progress"""
    status_data = get_training_status()
    return Response(status_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_training_session(request, session_id):
    """Get specific training session details"""
    try:
        session = TrainingSession.objects.get(id=session_id)
        return Response({
            'id': session.id,
            'status': session.status,
            'progress': session.progress,
            'current_step': session.current_stage,
            'error_message': session.error_message,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        })
    except TrainingSession.DoesNotExist:
        return Response({
            'error': 'Training session not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_training(request):
    """Stop training (note: this is a graceful stop request)"""
    global training_status

    # Stop any running session in database
    running_session = TrainingSession.objects.filter(status='running').first()
    if running_session:
        running_session.status = 'stopped'
        running_session.current_stage = 'Training stopped by user'
        running_session.save()

    training_status['is_training'] = False
    training_status['current_stage'] = 'Training stopped by user'

    return Response({
        'message': 'Training stop requested'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_training(request):
    """Reset stuck training sessions (admin only)"""
    global training_status

    # Reset all running sessions to stopped
    TrainingSession.objects.filter(status='running').update(status='stopped')

    training_status['is_training'] = False
    training_status['progress'] = 0
    training_status['current_stage'] = ''
    training_status['error'] = None
    training_status['session_id'] = None

    return Response({
        'message': 'Training status reset'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dataset_info(request):
    """Get dataset information"""
    try:
        info = {
            'dataset_path': DATASET_PATH,
            'exists': os.path.exists(DATASET_PATH),
            'folders': {}
        }

        if info['exists']:
            for folder in ['training_data', 'validation_data', 'testing_data']:
                folder_path = os.path.join(DATASET_PATH, folder)
                if os.path.exists(folder_path):
                    subfolders = {}
                    for subfolder in os.listdir(folder_path):
                        subfolder_path = os.path.join(folder_path, subfolder)
                        if os.path.isdir(subfolder_path):
                            image_count = len([f for f in os.listdir(subfolder_path)
                                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                            subfolders[subfolder] = image_count
                    info['folders'][folder] = subfolders

        return Response(info)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_image(request):
    """Predict using pre-trained YOLO model"""
    from .pretrained_models import predict_from_image_file
    from django.core.files.uploadedfile import InMemoryUploadedFile

    if 'image' not in request.FILES:
        return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']
    model_type = request.data.get('model_type', 'exam')  # 'exam', 'smoking', 'danger', or 'critical'

    # Save temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        for chunk in image_file.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name

    try:
        result = predict_from_image_file(temp_path, model_type)
        return Response(result)
    finally:
        os.unlink(temp_path)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_training_image(request):
    """Upload a single training image to the dataset"""
    from django.core.files.storage import default_storage
    import shutil

    if 'image' not in request.FILES:
        return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']
    category = request.data.get('category', 'training_data')
    label = request.data.get('label', 'unknown')

    # Create category and label directories
    target_dir = os.path.join(DATASET_PATH, category, label)
    os.makedirs(target_dir, exist_ok=True)

    # Save the image
    file_path = os.path.join(target_dir, image_file.name)
    with open(file_path, 'wb') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    return Response({
        'message': 'Image uploaded successfully',
        'path': file_path,
        'category': category,
        'label': label
    })
