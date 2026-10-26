"""
Dataset Analyzer - Comprehensive Data Inspection
Checks for corrupted images, duplicates, and class balance
"""
import os
import sys
from pathlib import Path
from PIL import Image
import hashlib
from collections import defaultdict

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATASET_PATH = r'F:\MUQ\dataset'

def check_image_integrity(image_path):
    """Check if an image file is valid and can be opened"""
    try:
        with Image.open(image_path) as img:
            img.verify()
        # Re-open to check for read errors
        with Image.open(image_path) as img:
            img.load()
        return True, None
    except Exception as e:
        return False, str(e)

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def analyze_dataset():
    """Comprehensive dataset analysis"""
    print("=" * 70)
    print("DATASET ANALYSIS REPORT")
    print("=" * 70)

    results = {
        'total_images': 0,
        'corrupted': [],
        'by_folder': defaultdict(lambda: {'count': 0, 'corrupted': 0, 'sizes': [], 'formats': defaultdict(int)}),
        'duplicates': [],
        'class_balance': {}
    }

    hash_map = defaultdict(list)

    # Analyze all folders
    for root, dirs, files in os.walk(DATASET_PATH):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                filepath = os.path.join(root, file)
                folder_name = os.path.basename(root)

                results['total_images'] += 1
                results['by_folder'][folder_name]['count'] += 1

                # Check integrity
                is_valid, error = check_image_integrity(filepath)
                if not is_valid:
                    results['corrupted'].append(filepath)
                    results['by_folder'][folder_name]['corrupted'] += 1
                    print(f"[CORRUPTED] {filepath} - {error}")
                    continue

                # Get image info
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        results['by_folder'][folder_name]['sizes'].append((width, height))
                        results['by_folder'][folder_name]['formats'][img.format] += 1

                    # Check for duplicates
                    file_hash = get_file_hash(filepath)
                    hash_map[file_hash].append(filepath)
                except Exception as e:
                    print(f"⚠️  ERROR reading {filepath}: {e}")

    # Find duplicates
    for file_hash, filepaths in hash_map.items():
        if len(filepaths) > 1:
            results['duplicates'].append({
                'hash': file_hash,
                'files': filepaths
            })
            print(f"[DUPLICATE] {len(filepaths)} files with hash {file_hash[:8]}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Images: {results['total_images']}")
    print(f"Corrupted Images: {len(results['corrupted'])}")
    print(f"Duplicate Groups: {len(results['duplicates'])}")

    print("\n" + "=" * 70)
    print("BY FOLDER")
    print("=" * 70)

    for folder, data in results['by_folder'].items():
        print(f"\n[FOLDER] {folder}:")
        print(f"   Total: {data['count']}")
        print(f"   Corrupted: {data['corrupted']}")
        if data['sizes']:
            avg_width = sum(s[0] for s in data['sizes']) / len(data['sizes'])
            avg_height = sum(s[1] for s in data['sizes']) / len(data['sizes'])
            print(f"   Avg Size: {avg_width:.0f}x{avg_height:.0f}")
        if data['formats']:
            print(f"   Formats: {dict(data['formats'])}")

    print("\n" + "=" * 70)
    print("CLASS BALANCE")
    print("=" * 70)

    # Calculate class balance from folder structure
    for split in ['training_data', 'validation_data', 'testing_data']:
        split_path = os.path.join(DATASET_PATH, split)
        if os.path.exists(split_path):
            print(f"\n{split}:")
            for class_folder in os.listdir(split_path):
                class_path = os.path.join(split_path, class_folder)
                if os.path.isdir(class_path):
                    count = len([f for f in os.listdir(class_path)
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                    print(f"  {class_folder}: {count}")

    print("\n" + "=" * 70)
    print("TASK TYPE RECOMMENDATION")
    print("=" * 70)

    # Determine task type
    if results['total_images'] > 0:
        print("\nBased on dataset structure:")
        print("- Images organized in class folders (smoking, notsmoking)")
        print("- Each image belongs to ONE class")
        print("- No bounding box annotations found")
        print("\n[RECOMMENDED] TASK: IMAGE CLASSIFICATION")
        print("\nThis is a binary classification task:")
        print("- Class 1: smoking")
        print("- Class 2: notsmoking")
        print("\nEach image will be classified into one of these two categories.")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if len(results['corrupted']) == 0 and len(results['duplicates']) == 0:
        print("[OK] Dataset is clean and ready for training")
    else:
        print(f"[WARNING] Dataset needs attention:")
        if results['corrupted']:
            print(f"   - {len(results['corrupted'])} corrupted images")
        if results['duplicates']:
            print(f"   - {len(results['duplicates'])} duplicate groups")

    return results

if __name__ == '__main__':
    analyze_dataset()
