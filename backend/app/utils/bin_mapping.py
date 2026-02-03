"""
Bin Mapping Logic: 9 classes → 3 bins

This module handles the mapping of predicted waste classes to recycling bins
with advanced strategies for composite materials and edge cases.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum


class BinType(str, Enum):
    """Bin types enum"""
    RECYCLABLE = "recyclable"
    GENERAL = "general"
    HAZARDOUS = "hazardous"
    ORGANIC = "organic"


# ============================================================================
# CORE MAPPING TABLE: 9 Classes → 4 Bins
# ============================================================================

BIN_MAPPING: Dict[str, BinType] = {
    #  RECYCLABLE (Tái chế) - Blue
    "cardboard": BinType.RECYCLABLE,
    "glass": BinType.RECYCLABLE,
    "metal": BinType.RECYCLABLE,
    "paper": BinType.RECYCLABLE,
    "plastic": BinType.RECYCLABLE,
    
    #  ORGANIC (Hữu cơ) - Orange
    "biological": BinType.ORGANIC,
    
    #  GENERAL (Rác thường) - Gray
    "textile": BinType.GENERAL,
    "trash": BinType.GENERAL,
    
    #  HAZARDOUS (Nguy hại) - Red
    "battery": BinType.HAZARDOUS,
}

# Vietnamese to English class name mapping (for model compatibility)
# The YOLO model returns Vietnamese names, so we need to map them to English
VN_TO_EN_CLASS_NAMES: Dict[str, str] = {
    "Pin": "battery",
    "Huu co": "biological",
    "Hop giay": "cardboard",
    "Thuy tinh": "glass",
    "Kim loai": "metal",
    "Giay": "paper",
    "Nhua": "plastic",
    "Vai": "textile",
    "Rac thai": "trash",
}

# English to Vietnamese (for display)
EN_TO_VN_CLASS_NAMES: Dict[str, str] = {
    "battery": "Pin",
    "biological": "Huu co",
    "cardboard": "Hop giay",
    "glass": "Thuy tinh",
    "metal": "Kim loai",
    "paper": "Giay",
    "plastic": "Nhua",
    "textile": "Vai",
    "trash": "Rac thai",
}


# ============================================================================
# VIETNAMESE BIN NAMES
# ============================================================================

BIN_NAMES_VN: Dict[BinType, str] = {
    BinType.RECYCLABLE: "Tái chế",
    BinType.GENERAL: "Rác thường",
    BinType.HAZARDOUS: "Nguy hại",
    BinType.ORGANIC: "Hữu cơ",
}


# ============================================================================
# BIN DISPOSAL INSTRUCTIONS (Vietnamese)
# ============================================================================

BIN_INSTRUCTIONS: Dict[BinType, str] = {
    BinType.RECYCLABLE: "Rửa sạch và bỏ vào thùng xanh tái chế",
    BinType.GENERAL: "Bỏ vào thùng rác màu xám",
    BinType.HAZARDOUS: "Cần xử lý đặc biệt. Đưa đến điểm thu gom rác nguy hại hoặc liên hệ cơ quan môi trường địa phương",
    BinType.ORGANIC: "Bỏ vào thùng rác hữu cơ (rau củ, thức ăn thừa) để ủ phân compost",
}


# ============================================================================
# BIN COLORS (for frontend)
# ============================================================================

BIN_COLORS: Dict[BinType, str] = {
    BinType.RECYCLABLE: "#3b82f6",  # Blue
    BinType.GENERAL: "#6b7280",      # Gray
    BinType.HAZARDOUS: "#ef4444",    # Red
    BinType.ORGANIC: "#f59e0b",      # Orange/Amber
}


# ============================================================================
# BIN ICONS (for frontend)
# ============================================================================

BIN_ICONS: Dict[BinType, str] = {
    BinType.RECYCLABLE: "",
    BinType.GENERAL: "",
    BinType.HAZARDOUS: "",
    BinType.ORGANIC: "",
}


# ============================================================================
# COMPOSITE MATERIAL PATTERNS
# ============================================================================

COMPOSITE_PATTERNS = {
    "milk_carton": {
        "possible_classes": ["cardboard", "plastic", "paper"],
        "min_classes": 2,  # Cần ít nhất 2 classes
        "combined_confidence_threshold": 0.85,  # ← Tăng từ 0.6 → 0.85
        "min_secondary_confidence": 0.15,  # ← THÊM MỚI: Confidence tối thiểu của class thứ 2
        "final_bin": BinType.RECYCLABLE,
        "class_name_vn": "Hộp đựng sữa/nước",
        "class_name_en": "beverage_carton",
        "special_instruction": "Hộp sữa Tetra Pak: Rửa sạch, làm phẳng và bỏ vào thùng tái chế. Nắp nhựa nên tháo riêng.",
    },
    "food_container": {
        "possible_classes": ["plastic", "cardboard"],
        "min_classes": 2,
        "combined_confidence_threshold": 0.75,  # ← Tăng từ 0.5 → 0.75
        "min_secondary_confidence": 0.15,  # ← THÊM MỚI
        "final_bin": BinType.RECYCLABLE,
        "class_name_vn": "Hộp đựng thức ăn",
        "class_name_en": "food_container",
        "special_instruction": "Hộp đựng thức ăn: Rửa sạch hoàn toàn trước khi bỏ vào thùng tái chế.",
    }
}


# ============================================================================
# ADVANCED MAPPING FUNCTIONS
# ============================================================================

def map_class_to_bin(predicted_class: str) -> BinType:
    """
    Simple 1-to-1 mapping from class to bin type
    Supports both English and Vietnamese class names
    
    Args:
        predicted_class: Class name (English like 'plastic' or Vietnamese like 'Nhựa')
        
    Returns:
        BinType enum value
    """
    # First, try direct English lookup
    if predicted_class in BIN_MAPPING:
        return BIN_MAPPING[predicted_class]
    
    # If not found, try Vietnamese to English conversion
    if predicted_class in VN_TO_EN_CLASS_NAMES:
        english_class = VN_TO_EN_CLASS_NAMES[predicted_class]
        return BIN_MAPPING.get(english_class, BinType.GENERAL)
    
    # Default to general if not found
    return BinType.GENERAL


def aggregate_bin_scores(
    top_predictions: List[Tuple[str, float]]
) -> Tuple[BinType, float]:
    """
    Strategy 1: Multi-class aggregation
    
    Args:
        top_predictions: List of (class_name, probability) tuples
        
    Returns:
        Tuple of (bin_type, aggregated_confidence)
    """
    bin_scores: Dict[BinType, float] = {
        BinType.RECYCLABLE: 0.0,
        BinType.GENERAL: 0.0,
        BinType.HAZARDOUS: 0.0,
        BinType.ORGANIC: 0.0,
    }
    
    for class_name, probability in top_predictions:
        bin_type = map_class_to_bin(class_name)
        bin_scores[bin_type] += probability
    
    best_bin = max(bin_scores.items(), key=lambda x: x[1])
    return best_bin[0], best_bin[1]


def check_composite_material(
    top_predictions: List[Tuple[str, float]]
) -> Optional[Dict]:
    """
    Strategy 3: Composite material detection
    
    Check if predictions match a composite material pattern
    with STRICT validation to avoid false positives
    
    Args:
        top_predictions: List of (class_name, probability) tuples
        
    Returns:
        Dict with composite material info if detected, None otherwise
    """
    if len(top_predictions) < 2:
        return None
    
    top_classes = [cls for cls, _ in top_predictions]
    
    for material_name, pattern in COMPOSITE_PATTERNS.items():
        # Count how many of the pattern classes are in top predictions
        matching_classes = [
            cls for cls in top_classes 
            if cls in pattern["possible_classes"]
        ]
        
        if len(matching_classes) < pattern["min_classes"]:
            continue
        
        # Calculate combined confidence for matching classes
        combined_confidence = sum(
            prob for cls, prob in top_predictions
            if cls in pattern["possible_classes"]
        )
        
        # Check combined confidence threshold
        if combined_confidence < pattern["combined_confidence_threshold"]:
            continue
        
       
        if "min_secondary_confidence" in pattern:
            # Get confidences of matching classes
            matching_probs = [
                prob for cls, prob in top_predictions
                if cls in pattern["possible_classes"]
            ]
            
            # Sort to get highest and second highest
            matching_probs.sort(reverse=True)
            
            # If we have at least 2 matching classes
            if len(matching_probs) >= 2:
                # Check if second class has meaningful confidence
                if matching_probs[1] < pattern["min_secondary_confidence"]:
                    # Secondary class too weak → Not a composite
                    continue
            else:
                # Only 1 matching class → Not a composite
                continue
        
        # All checks passed → It's a composite!
        return {
            "detected": True,
            "material_type": material_name,
            "class_name_vn": pattern["class_name_vn"],
            "class_name_en": pattern["class_name_en"],
            "bin_type": pattern["final_bin"],
            "special_instruction": pattern["special_instruction"],
            "combined_confidence": combined_confidence,
            "matching_classes": matching_classes,
        }
    
    return None


def get_bin_info(bin_type: BinType) -> Dict:
    """Get complete information about a bin type"""
    return {
        "bin_type": bin_type.value,
        "bin_type_vn": BIN_NAMES_VN[bin_type],
        "bin_instruction": BIN_INSTRUCTIONS[bin_type],
        "bin_color": BIN_COLORS[bin_type],
        "bin_icon": BIN_ICONS[bin_type],
    }


def smart_map(
    predicted_class: str,
    confidence: float,
    top_predictions: List[Tuple[str, float]],
    confidence_threshold_low: float = 0.4,
) -> Dict:
    """
    Advanced mapping with all strategies combined
    
    Args:
        predicted_class: Top predicted class
        confidence: Confidence of top prediction
        top_predictions: List of (class, prob) tuples for top N predictions
        confidence_threshold_low: Threshold for low confidence warning
        
    Returns:
        Dict with complete mapping result
    """
    result = {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "low_confidence": confidence < confidence_threshold_low,
    }
    
    # Check for composite materials first
    composite = check_composite_material(top_predictions)
    if composite:
        result.update({
            "composite_detected": True,
            "composite_info": composite,
            "bin_type": composite["bin_type"].value,
            "class_name_vn": composite["class_name_vn"],
            "class_name_en": composite["class_name_en"],
            "special_instruction": composite["special_instruction"],
        })
        result.update(get_bin_info(composite["bin_type"]))
        return result
    
    # Otherwise, use aggregated bin scores
    bin_type, aggregated_confidence = aggregate_bin_scores(top_predictions)
    
    result.update({
        "composite_detected": False,
        "bin_type": bin_type.value,
        "aggregated_confidence": aggregated_confidence,
    })
    result.update(get_bin_info(bin_type))
    
    return result


def get_all_bins_info() -> List[Dict]:
    """Get information about all bin types"""
    return [
        {
            **get_bin_info(bin_type),
            "recyclable_classes": [
                cls for cls, bt in BIN_MAPPING.items() 
                if bt == bin_type
            ]
        }
        for bin_type in BinType
    ]


def validate_class_name(class_name: str) -> bool:
    """Check if class name is valid"""
    return class_name in BIN_MAPPING