"""
Recycling Tips Database (Vietnamese)

Provides detailed recycling instructions and tips for each waste class
"""

from typing import List, Dict


# ============================================================================
# RECYCLING TIPS BY CLASS (Vietnamese)
# ============================================================================

RECYCLING_TIPS: Dict[str, List[Dict[str, str]]] = {
    "plastic": [
        {
            "step": "Rửa sạch chai/hộp nhựa trước khi bỏ",
            "icon": "",
            "detail": "Rửa sạch để tránh ô nhiễm đợt tái chế"
        },
        {
            "step": "Tháo nắp và nhãn nếu có thể",
            "icon": "",
            "detail": "Nắp và chai thường là loại nhựa khác nhau"
        },
        {
            "step": "Ép dẹp để tiết kiệm không gian",
            "icon": "↕",
            "detail": "Giúp tiết kiệm không gian trong thùng rác"
        },
        {
            "step": "Bỏ vào thùng xanh tái chế",
            "icon": "",
            "detail": "Nhựa có thể tái chế thành nhiều sản phẩm mới"
        }
    ],
    
    "paper": [
        {
            "step": "Giữ giấy khô ráo và sạch sẽ",
            "icon": "",
            "detail": "Giấy ướt hoặc dính bẩn khó tái chế"
        },
        {
            "step": "Tháo bỏ kẹp giấy, ghim, băng dính",
            "icon": "",
            "detail": "Kim loại và nhựa cần tách riêng"
        },
        {
            "step": "Làm phẳng hộp giấy và thùng carton",
            "icon": "",
            "detail": "Tiết kiệm không gian vận chuyển"
        },
        {
            "step": "Bỏ vào thùng xanh tái chế",
            "icon": "",
            "detail": "Giấy có thể tái chế 5-7 lần"
        }
    ],
    
    "cardboard": [
        {
            "step": "Loại bỏ băng dính và nhãn",
            "icon": "",
            "detail": "Băng dính nhựa cần tách ra"
        },
        {
            "step": "Làm phẳng hộp carton",
            "icon": "",
            "detail": "Dễ dàng xếp chồng và vận chuyển"
        },
        {
            "step": "Đảm bảo hộp sạch, không dính mỡ",
            "icon": "",
            "detail": "Hộp dính mỡ/thức ăn → bỏ rác thường"
        },
        {
            "step": "Bỏ vào thùng xanh tái chế",
            "icon": "",
            "detail": "Carton có thể làm thành giấy mới"
        }
    ],
    
    "glass": [
        {
            "step": "Rửa sạch chai/lọ thủy tinh",
            "icon": "",
            "detail": "Loại bỏ thức ăn và chất lỏng"
        },
        {
            "step": "Tháo nắp kim loại hoặc nhựa",
            "icon": "",
            "detail": "Nắp cần tái chế riêng"
        },
        {
            "step": "Không cần bỏ nhãn giấy",
            "icon": "",
            "detail": "Nhãn sẽ được tách trong quá trình tái chế"
        },
        {
            "step": "Cẩn thận với thủy tinh vỡ",
            "icon": "",
            "detail": "Bọc cẩn thận nếu bị vỡ"
        },
        {
            "step": "Bỏ vào thùng xanh tái chế",
            "icon": "",
            "detail": "Thủy tinh có thể tái chế vô hạn lần"
        }
    ],
    
    "metal": [
        {
            "step": "Rửa sạch lon, hộp kim loại",
            "icon": "",
            "detail": "Loại bỏ thức ăn còn sót lại"
        },
        {
            "step": "Ép dẹp lon nhôm",
            "icon": "↕",
            "detail": "Tiết kiệm không gian"
        },
        {
            "step": "Không cần tháo nhãn giấy",
            "icon": "",
            "detail": "Nhãn sẽ bị đốt cháy khi nấu chảy kim loại"
        },
        {
            "step": "Bỏ vào thùng xanh tái chế",
            "icon": "",
            "detail": "Kim loại tiết kiệm 95% năng lượng khi tái chế"
        }
    ],
    
    "battery": [
        {
            "step": "KHÔNG bỏ vào thùng rác thường",
            "icon": "",
            "detail": "Pin chứa chất độc hại nguy hiểm"
        },
        {
            "step": "Bọc đầu cực pin bằng băng dính",
            "icon": "",
            "detail": "Tránh chập điện và cháy nổ"
        },
        {
            "step": "Thu gom riêng trong hộp/túi",
            "icon": "",
            "detail": "Tách biệt với rác thải khác"
        },
        {
            "step": "Đưa đến điểm thu gom pin",
            "icon": "",
            "detail": "Siêu thị, cửa hàng điện tử, hoặc cơ quan môi trường"
        }
    ],
    
    "biological": [
        {
            "step": "Tách riêng rác hữu cơ",
            "icon": "",
            "detail": "Tách biệt với rác khô"
        },
        {
            "step": "Xem xét làm phân compost",
            "icon": "",
            "detail": "Rác hữu cơ có thể làm phân bón"
        },
        {
            "step": "Đựng trong túi/hộp kín",
            "icon": "",
            "detail": "Tránh mùi hôi và côn trùng"
        },
        {
            "step": "Bỏ vào thùng rác màu xám",
            "icon": "",
            "detail": "Rác hữu cơ không tái chế được"
        }
    ],
    
    "textile": [
        {
            "step": "Quần áo còn tốt → Quyên góp",
            "icon": "",
            "detail": "Cho người khác, tổ chức từ thiện"
        },
        {
            "step": "Vải vụn → Dùng làm giẻ lau",
            "icon": "",
            "detail": "Tái sử dụng trước khi vứt"
        },
        {
            "step": "Kiểm tra điểm thu gom vải",
            "icon": "",
            "detail": "Một số nơi nhận tái chế vải"
        },
        {
            "step": "Bỏ vào thùng rác màu xám nếu không còn dùng được",
            "icon": "",
            "detail": "Vải rách hoàn toàn khó tái chế"
        }
    ],
    
    "trash": [
        {
            "step": "Kiểm tra kỹ trước khi vứt",
            "icon": "",
            "detail": "Có thể còn phân loại được một số thứ"
        },
        {
            "step": "Đựng trong túi kín",
            "icon": "",
            "detail": "Giữ vệ sinh chung"
        },
        {
            "step": "Bỏ vào thùng rác màu xám",
            "icon": "",
            "detail": "Rác không thể tái chế"
        },
        {
            "step": "Cân nhắc giảm thiểu rác thải",
            "icon": "",
            "detail": "Mua sắm có ý thức, tái sử dụng"
        }
    ]
}


# ============================================================================
# SPECIAL CASE INSTRUCTIONS
# ============================================================================

SPECIAL_INSTRUCTIONS: Dict[str, Dict] = {
    "milk_carton": {
        "name_vn": "Hộp sữa Tetra Pak",
        "tips": [
            {
                "step": "Rửa sạch hộp",
                "icon": "",
                "detail": "Đổ hết sữa, rửa nước sạch"
            },
            {
                "step": "Làm phẳng hộp",
                "icon": "↕",
                "detail": "Ép dẹp để tiết kiệm không gian"
            },
            {
                "step": "Tháo nắp nhựa (nếu có)",
                "icon": "",
                "detail": "Nắp tái chế riêng"
            },
            {
                "step": "Bỏ vào thùng xanh tái chế",
                "icon": "",
                "detail": "Một số địa phương có quy trình riêng"
            }
        ],
        "note": "Hộp sữa Tetra Pak có thể tái chế nhưng cần quy trình đặc biệt"
    },
    
    "pizza_box": {
        "name_vn": "Hộp pizza",
        "tips": [
            {
                "step": "Kiểm tra hộp có dính mỡ không",
                "icon": "",
                "detail": "Quan trọng để phân loại đúng"
            },
            {
                "step": "Nếu hộp SẠCH → Tái chế",
                "icon": "",
                "detail": "Bỏ vào thùng xanh"
            },
            {
                "step": "Nếu DÍNH MỠ → Rác thường",
                "icon": "",
                "detail": "Bỏ vào thùng xám"
            },
            {
                "step": "Có thể cắt phần sạch ra",
                "icon": "",
                "detail": "Phần sạch tái chế, phần dính mỡ vứt"
            }
        ],
        "note": "Giấy dính mỡ không thể tái chế do ô nhiễm"
    }
}


# ============================================================================
# GENERAL RECYCLING GUIDELINES
# ============================================================================

GENERAL_GUIDELINES = [
    {
        "title": "Nguyên tắc 3R",
        "items": [
            "Reduce (Giảm thiểu): Mua ít hơn, chọn sản phẩm bền",
            "Reuse (Tái sử dụng): Dùng lại trước khi vứt",
            "Recycle (Tái chế): Phân loại đúng để tái chế"
        ]
    },
    {
        "title": "Quy tắc chung khi tái chế",
        "items": [
            "Rửa sạch: Loại bỏ thức ăn và chất lỏng",
            "Làm khô: Đồ ướt khó tái chế",
            "Làm phẳng: Tiết kiệm không gian",
            "Tách riêng: Các vật liệu khác nhau"
        ]
    },
    {
        "title": "Không tái chế được",
        "items": [
            "Giấy dính mỡ, thức ăn",
            "Nhựa loại 3, 6, 7 (một số nơi)",
            "Thủy tinh vỡ nhỏ",
            "Quần áo rách nát",
            "Pin bỏ lẫn rác thường"
        ]
    }
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_recycling_tips(class_name: str) -> List[Dict[str, str]]:
    """
    Get recycling tips for a specific waste class
    
    Args:
        class_name: One of 9 waste classes
        
    Returns:
        List of tip dictionaries with step, icon, and detail
    """
    return RECYCLING_TIPS.get(class_name, RECYCLING_TIPS["trash"])


def get_special_instruction(material_type: str) -> Dict:
    """
    Get special instructions for composite materials
    
    Args:
        material_type: Type of special material (e.g., 'milk_carton')
        
    Returns:
        Dict with special instructions
    """
    return SPECIAL_INSTRUCTIONS.get(material_type, {})


def get_simple_tips(class_name: str) -> List[str]:
    """
    Get simple list of tips (just the steps, no icons/details)
    
    Args:
        class_name: One of 9 waste classes
        
    Returns:
        List of tip strings
    """
    tips = get_recycling_tips(class_name)
    return [tip["step"] for tip in tips]


def get_tips_with_icons(class_name: str) -> List[str]:
    """
    Get tips formatted with icons
    
    Args:
        class_name: One of 9 waste classes
        
    Returns:
        List of formatted tip strings
    """
    tips = get_recycling_tips(class_name)
    return [f"{tip['icon']} {tip['step']}" for tip in tips]