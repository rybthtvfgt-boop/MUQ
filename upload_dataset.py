#!/usr/bin/env python3
"""
Upload training images to Railway dataset
"""
import os
import requests
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "https://muqai.up.railway.app/api"
USERNAME = "muq"
PASSWORD = "12345"

def get_access_token():
    """Get JWT access token"""
    response = requests.post(f"{API_BASE_URL}/auth/login/", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    return None

def upload_image(file_path, category, label, token, max_retries=5):
    """Upload a single image with exponential backoff retry"""
    url = f"{API_BASE_URL}/monitoring/dataset/upload/"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    for attempt in range(max_retries):
        try:
            with open(file_path, 'rb') as f:
                files = {'image': (os.path.basename(file_path), f, 'image/jpeg')}
                data = {
                    'category': category,
                    'label': label
                }
                response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8, 16, 32 seconds
                print(f"[RETRY] Attempt {attempt + 1} failed, waiting {wait_time}s...")
                import time
                time.sleep(wait_time)
            else:
                raise

def upload_dataset(local_dataset_path, token):
    """Upload all images from local dataset"""
    local_path = Path(local_dataset_path)

    if not local_path.exists():
        print(f"[ERROR] Dataset path not found: {local_dataset_path}")
        return

    # Define folder structure
    categories = ['training_data', 'validation_data', 'testing_data']
    labels = ['smoking', 'non_smoking', 'exam', 'non_exam', 'danger', 'non_danger']

    total_uploaded = 0
    total_failed = 0

    for category in categories:
        for label in labels:
            category_path = local_path / category / label
            if not category_path.exists():
                continue

            print(f"\n[INFO] Processing {category}/{label}...")
            image_files = list(category_path.glob('*.jpg')) + list(category_path.glob('*.jpeg')) + list(category_path.glob('*.png'))

            print(f"   Found {len(image_files)} images")

            for i, image_file in enumerate(image_files):
                print(f"   Uploading {image_file.name} ({i+1}/{len(image_files)})...", end=' ')
                try:
                    response = upload_image(str(image_file), category, label, token)

                    if response.status_code == 200:
                        print("[OK]")
                        total_uploaded += 1
                    elif response.status_code == 429:
                        print("[RATE LIMIT]")
                        import time
                        print("   Waiting 60 seconds...")
                        time.sleep(60)
                        # Retry once after rate limit
                        response = upload_image(str(image_file), category, label, token)
                        if response.status_code == 200:
                            print("[OK - RETRY]")
                            total_uploaded += 1
                        else:
                            print(f"[FAIL] ({response.status_code})")
                            total_failed += 1
                    else:
                        print(f"[FAIL] ({response.status_code})")
                        total_failed += 1

                    # Very long delay between uploads to avoid rate limiting
                    import time
                    time.sleep(3.0)  # Increased to 3.0 seconds
                except Exception as e:
                    print(f"[ERROR] {str(e)[:50]}")
                    total_failed += 1
                    import time
                    time.sleep(15)  # Increased to 15 seconds

    print(f"\n[SUMMARY]")
    print(f"   Uploaded: {total_uploaded}")
    print(f"   Failed: {total_failed}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_dataset.py <local_dataset_path>")
        print("Example: python upload_dataset.py F:/MUQ/dataset")
        sys.exit(1)

    local_dataset = sys.argv[1]

    print("[INFO] Logging in...")
    token = get_access_token()
    if not token:
        print("[ERROR] Failed to get access token")
        sys.exit(1)

    print("[OK] Login successful")
    print(f"[INFO] Uploading dataset from: {local_dataset}")

    upload_dataset(local_dataset, token)
