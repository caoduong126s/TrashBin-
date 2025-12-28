# src/vietnam_categories.py

"""
Define Vietnam-specific waste categories
"""

VIETNAM_WASTE_CATEGORIES = {
    'nylon_bag': {
        'name_vi': 'Túi nilon chợ',
        'description': 'Túi nilon mua hàng chợ, siêu thị (có chữ Việt, nhiều màu)',
        'examples': [
            'Túi nilon đựng hàng chợ',
            'Túi siêu thị (Co.opmart, Lotte, Big C)',
            'Túi xách có chữ Việt'
        ],
        'target_count': 100,
        'recyclable': False,
        'disposal': 'Thùng rác không tái chế (đen/xám)'
    },
    
    'foam_box': {
        'name_vi': 'Hộp xốp',
        'description': 'Hộp xốp đựng cơm, đồ ăn mang về',
        'examples': [
            'Hộp cơm xốp',
            'Khay xốp đựng thực phẩm',
            'Hộp xốp đựng trái cây'
        ],
        'target_count': 100,
        'recyclable': False,
        'disposal': 'Thùng rác không tái chế'
    },
    
    'vn_packaging': {
        'name_vi': 'Bao bì Việt Nam',
        'description': 'Bao bì snack, sản phẩm thương hiệu VN',
        'examples': [
            'Gói Oishi (snack)',
            'Bao bì mì gói (Hảo Hảo, Omachi)',
            'Hộp sữa (Vinamilk, TH True Milk)',
            'Bao thuốc lá (Vinataba)'
        ],
        'target_count': 100,
        'recyclable': True,
        'disposal': 'Thùng tái chế (xanh)'
    },
    
    'tropical_organic': {
        'name_vi': 'Vỏ trái cây nhiệt đới',
        'description': 'Vỏ trái cây đặc trưng VN',
        'examples': [
            'Vỏ sầu riêng',
            'Vỏ dừa',
            'Bã mía',
            'Vỏ chôm chôm, nhãn, vải'
        ],
        'target_count': 80,
        'recyclable': False,
        'disposal': 'Compost / Rác hữu cơ'
    },
    
    'beverage_vn': {
        'name_vi': 'Chai/lon nước Việt Nam',
        'description': 'Chai nước, lon có thương hiệu VN',
        'examples': [
            'Chai Number 1',
            'Chai Revive',
            'Lon Sting',
            'Hộp sữa Vinamilk'
        ],
        'target_count': 60,
        'recyclable': True,
        'disposal': 'Thùng tái chế'
    },
    
    'medical_waste': {
        'name_vi': 'Rác y tế sinh hoạt',
        'description': 'Khẩu trang, băng vệ sinh (phổ biến sau COVID)',
        'examples': [
            'Khẩu trang y tế',
            'Khẩu trang vải',
            'Túi đựng thuốc'
        ],
        'target_count': 40,
        'recyclable': False,
        'disposal': 'Rác nguy hại (đỏ) hoặc rác thường'
    }
}

def print_collection_guide():
    """
    Print guide for collecting Vietnam dataset
    """
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     HƯỚNG DẪN THU THẬP DATASET VIỆT NAM                   ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    total_target = 0
    
    for category_id, info in VIETNAM_WASTE_CATEGORIES.items():
        total_target += info['target_count']
        
        print(f"📦 {info['name_vi']} ({category_id})")
        print(f"   Mục tiêu: {info['target_count']} ảnh")
        print(f"   Tái chế: {'✅ Có' if info['recyclable'] else '❌ Không'}")
        print(f"   Ví dụ:")
        for example in info['examples']:
            print(f"      - {example}")
        print()
    
    print(f"📊 TỔNG MỤC TIÊU: {total_target} ảnh")
    print(f"📸 Sau augmentation (×5): {total_target * 5} ảnh\n")
    
    print("💡 LƯU Ý KHI CHỤP:")
    print("   ✅ 1 ảnh = 1 loại rác (không chụp nhiều loại cùng lúc)")
    print("   ✅ Rửa sạch trước khi chụp")
    print("   ✅ Ánh sáng tốt, không mờ")
    print("   ✅ Chụp nhiều góc độ (trên, nghiêng, cận)")
    print("   ✅ Thay đổi background (bàn trắng, sàn, ngoài trời)")
    print()

if __name__ == '__main__':
    print_collection_guide()