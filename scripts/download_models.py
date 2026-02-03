import os
import sys
import requests
from pathlib import Path

# Cấu hình URL model (BẠN CẦN CẬP NHẬT LINK NÀY SAU KHI UPLOAD LÊN DRIVE/HUGGINGFACE)
# Ví dụ: Link Google Drive public hoặc direct link
MODEL_URLS = {
    "yolov8s_best.pt": "LINK_DOWNLOAD_MODEL_YOLO_CUA_BAN_O_DAY",
    # "efficientnet_b0.pth": "LINK_KHAC_NEU_CO"
}

DEST_DIR = Path(__file__).parent.parent / "models"

def download_file(url, text, dest_path):
    print(f"Downloading {text}...")
    try:
        if url.startswith("LINK_"):
            print(f"❌ CHƯA CÓ LINK DOWNLOAD CHO {text}!")
            print(f"👉 Vui lòng tải thủ công file '{dest_path.name}' và bỏ vào thư mục 'models/'")
            return False
            
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Đã tải xong: {dest_path}")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi tải {text}: {e}")
        return False

def main():
    if not DEST_DIR.exists():
        DEST_DIR.mkdir(parents=True)
        print(f"Created directory: {DEST_DIR}")

    print("=== STARTING MODEL DOWNLOAD ===")
    print("Lưu ý: Bạn cần cập nhật link download trong scripts/download_models.py trước khi chạy.")
    
    success_count = 0
    for filename, url in MODEL_URLS.items():
        dest = DEST_DIR / filename
        if dest.exists():
            print(f"⚠️  File {filename} đã tồn tại, bỏ qua.")
            success_count += 1
            continue
            
        if download_file(url, filename, dest):
            success_count += 1

    if success_count == len(MODEL_URLS):
        print("\n✅ TẤT CẢ MODEL ĐÃ SẴN SÀNG!")
    else:
        print("\n⚠️  CÒN THIẾU MODEL. Vui lòng kiểm tra lại hướng dẫn.")

if __name__ == "__main__":
    main()
