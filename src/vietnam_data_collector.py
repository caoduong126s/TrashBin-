# src/vietnam_data_collector.py

import cv2
import os
from datetime import datetime
from pathlib import Path
import json

class VietnameseWasteCollector:
    """
    Tool để chụp và organize Vietnam waste photos
    """
    
    def __init__(self, save_root='data/vietnam/raw'):
        self.save_root = Path(save_root)
        
        # Import categories
        from vietnam_categories import VIETNAM_WASTE_CATEGORIES
        self.categories = VIETNAM_WASTE_CATEGORIES
        
        # Create directories
        for category_id in self.categories.keys():
            category_dir = self.save_root / category_id
            category_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file
        self.metadata_file = self.save_root / 'metadata.json'
        self.load_metadata()
    
    def load_metadata(self):
        """Load existing metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {cat: {'count': 0, 'images': []} 
                           for cat in self.categories.keys()}
    
    def save_metadata(self):
        """Save metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def print_status(self):
        """Print collection status"""
        print("\n" + "="*60)
        print("📊 COLLECTION STATUS")
        print("="*60)
        
        for category_id, info in self.categories.items():
            current_count = len(list((self.save_root / category_id).glob('*.jpg')))
            target = info['target_count']
            percentage = (current_count / target * 100) if target > 0 else 0
            
            # Progress bar
            bar_length = 30
            filled = int(bar_length * current_count / target) if target > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"\n{info['name_vi']} ({category_id})")
            print(f"[{bar}] {current_count}/{target} ({percentage:.1f}%)")
        
        print("\n" + "="*60)
    
    def capture_images(self, category_id):
        """
        Open webcam to capture images
        
        Controls:
        - SPACE: Capture image
        - Q: Quit
        - S: Show status
        """
        if category_id not in self.categories:
            print(f"❌ Invalid category: {category_id}")
            return
        
        category_info = self.categories[category_id]
        save_dir = self.save_root / category_id
        
        # Get current count
        current_images = list(save_dir.glob('*.jpg'))
        count = len(current_images)
        
        print("\n" + "="*60)
        print(f"📸 CAPTURING: {category_info['name_vi']}")
        print("="*60)
        print(f"Current: {count}/{category_info['target_count']}")
        print("\nControls:")
        print("  SPACE - Capture image")
        print("  Q     - Quit")
        print("  S     - Show status")
        print("="*60 + "\n")
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to grab frame")
                break
            
            # Display info on frame
            display_frame = frame.copy()
            
            # Header
            cv2.rectangle(display_frame, (0, 0), (1280, 80), (0, 0, 0), -1)
            cv2.putText(display_frame, f"{category_info['name_vi']}", 
                       (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Count: {count}/{category_info['target_count']}", 
                       (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Instructions
            cv2.rectangle(display_frame, (0, 640), (1280, 720), (0, 0, 0), -1)
            cv2.putText(display_frame, "SPACE: Capture | Q: Quit | S: Status", 
                       (350, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Center guideline
            center_x = display_frame.shape[1] // 2
            center_y = display_frame.shape[0] // 2
            cv2.circle(display_frame, (center_x, center_y), 150, (0, 255, 0), 2)
            cv2.putText(display_frame, "Place object here", 
                       (center_x - 100, center_y + 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Vietnam Waste Collector', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            # SPACE - Capture
            if key == ord(' '):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{category_id}_{timestamp}_{count:04d}.jpg"
                filepath = save_dir / filename
                
                # Save image
                cv2.imwrite(str(filepath), frame)
                count += 1
                
                # Flash effect
                white_frame = frame.copy()
                white_frame.fill(255)
                cv2.imshow('Vietnam Waste Collector', white_frame)
                cv2.waitKey(100)
                
                print(f"✅ Captured: {filename} ({count}/{category_info['target_count']})")
                
                # Update metadata
                self.metadata[category_id]['count'] = count
                self.metadata[category_id]['images'].append({
                    'filename': filename,
                    'timestamp': timestamp,
                    'path': str(filepath)
                })
                self.save_metadata()
            
            # Q - Quit
            elif key == ord('q'):
                print(f"\n👋 Quitting. Total captured: {count}")
                break
            
            # S - Status
            elif key == ord('s'):
                self.print_status()
        
        cap.release()
        cv2.destroyAllWindows()
    
    def batch_capture_workflow(self):
        """
        Interactive workflow to capture all categories
        """
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║       VIETNAM WASTE DATASET COLLECTION WORKFLOW          ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        
        self.print_status()
        
        # Sort categories by completion percentage
        categories_sorted = sorted(
            self.categories.items(),
            key=lambda x: len(list((self.save_root / x[0]).glob('*.jpg'))) / x[1]['target_count']
        )
        
        for category_id, info in categories_sorted:
            current = len(list((self.save_root / category_id).glob('*.jpg')))
            target = info['target_count']
            
            if current >= target:
                print(f"\n✅ {info['name_vi']} - COMPLETED ({current}/{target})")
                continue
            
            print(f"\n📸 Next: {info['name_vi']} ({current}/{target})")
            print(f"   Examples: {', '.join(info['examples'][:2])}")
            
            response = input("   Start capturing? (y/n/s=skip): ").lower()
            
            if response == 'y':
                self.capture_images(category_id)
            elif response == 's':
                continue
            else:
                print("   Skipped.")
        
        print("\n" + "="*60)
        print("🎉 COLLECTION WORKFLOW COMPLETED!")
        print("="*60)
        self.print_status()

# ============ MAIN EXECUTION ============

def main():
    """
    Main function
    """
    import sys
    
    collector = VietnameseWasteCollector()
    
    if len(sys.argv) > 1:
        # Single category mode
        category = sys.argv[1]
        collector.capture_images(category)
    else:
        # Interactive workflow
        print("\n🇻🇳 VIETNAMESE WASTE DATASET COLLECTOR")
        print("\nOptions:")
        print("  1. Batch workflow (recommended)")
        print("  2. Single category")
        print("  3. Show status only")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == '1':
            collector.batch_capture_workflow()
        
        elif choice == '2':
            print("\nAvailable categories:")
            for i, (cat_id, info) in enumerate(collector.categories.items(), 1):
                print(f"  {i}. {info['name_vi']} ({cat_id})")
            
            cat_choice = input("\nEnter category number or ID: ").strip()
            
            # Try as number first
            try:
                cat_index = int(cat_choice) - 1
                category_id = list(collector.categories.keys())[cat_index]
            except:
                category_id = cat_choice
            
            collector.capture_images(category_id)
        
        elif choice == '3':
            collector.print_status()
        
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()