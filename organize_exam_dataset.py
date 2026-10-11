import os
import shutil
import sys
from pathlib import Path

# Dataset paths
SOURCE_DIR = r"C:\Users\moktata\Desktop\MUQ\archive\CCTV-Exam -Monitor -Dataset"
TARGET_DIR = r"C:\Users\moktata\Desktop\MUQ\exam_monitoring_dataset"

# Classes
CLASSES = ["cheating", "normal", "suspicious", "phone", "looking_at_others"]

# Configure UTF-8 output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def organize_images(split="train"):
    """
    Display images from the source directory and ask user to classify them.
    """
    source_path = os.path.join(SOURCE_DIR, split)
    
    if not os.path.exists(source_path):
        print(f"❌ Error: {source_path} does not exist")
        return
    
    # Get all image files
    image_files = [f for f in os.listdir(source_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        print(f"❌ No images found in {source_path}")
        return
    
    print(f"\n📁 Found {len(image_files)} images in {split}/")
    print(f"🎯 Classes: {', '.join(CLASSES)}")
    print(f"📂 Target: {TARGET_DIR}")
    print(f"\n⌨️  Controls:")
    print(f"   1 = cheating (غش)")
    print(f"   2 = normal (عادي)")
    print(f"   3 = suspicious (مشبوه)")
    print(f"   4 = phone (استخدام هاتف)")
    print(f"   5 = looking_at_others (النظر للآخرين)")
    print(f"   s = skip image")
    print(f"   q = quit")
    print(f"\n{'='*60}")
    
    classified_count = 0
    skipped_count = 0
    
    for i, image_file in enumerate(image_files):
        source_file = os.path.join(source_path, image_file)
        
        print(f"\n📷 Image {i+1}/{len(image_files)}: {image_file}")
        print(f"   {'='*60}")
        
        while True:
            choice = input(f"   Class (1-5, s=skip, q=quit): ").strip().lower()
            
            if choice == 'q':
                print(f"\n✅ Quitting...")
                print(f"   Classified: {classified_count}")
                print(f"   Skipped: {skipped_count}")
                return
            
            elif choice == 's':
                skipped_count += 1
                print(f"   ⏭️  Skipped")
                break
            
            elif choice in ['1', '2', '3', '4', '5']:
                class_name = CLASSES[int(choice) - 1]
                target_path = os.path.join(TARGET_DIR, split, class_name, image_file)
                
                # Copy image to target directory
                shutil.copy2(source_file, target_path)
                classified_count += 1
                print(f"   ✅ Classified as: {class_name}")
                break
            
            else:
                print(f"   ❌ Invalid choice. Try again.")
    
    print(f"\n{'='*60}")
    print(f"✅ Done!")
    print(f"   Total images: {len(image_files)}")
    print(f"   Classified: {classified_count}")
    print(f"   Skipped: {skipped_count}")

def show_statistics():
    """Show statistics of organized dataset."""
    print(f"\n📊 Dataset Statistics:")
    print(f"{'='*60}")
    
    for split in ["train", "valid", "test"]:
        print(f"\n📁 {split.upper()}:")
        total = 0
        for class_name in CLASSES:
            class_path = os.path.join(TARGET_DIR, split, class_name)
            if os.path.exists(class_path):
                count = len([f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                total += count
                print(f"   {class_name:20s}: {count:4d} images")
            else:
                print(f"   {class_name:20s}: {0:4d} images")
        print(f"   {'-'*40}")
        print(f"   {'TOTAL':20s}: {total:4d} images")

def main():
    print("="*60)
    print("🎓 MUQ - Exam Monitoring Dataset Organizer")
    print("="*60)
    
    while True:
        print(f"\n📋 Menu:")
        print(f"   1. Organize TRAIN images")
        print(f"   2. Organize VALID images")
        print(f"   3. Organize TEST images")
        print(f"   4. Show statistics")
        print(f"   5. Exit")
        
        choice = input(f"\nSelect option (1-5): ").strip()
        
        if choice == '1':
            organize_images("train")
        elif choice == '2':
            organize_images("valid")
        elif choice == '3':
            organize_images("test")
        elif choice == '4':
            show_statistics()
        elif choice == '5':
            print(f"\n👋 Goodbye!")
            break
        else:
            print(f"❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
