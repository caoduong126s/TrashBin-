/**
 * Disposal Instructions Database
 * Detailed step-by-step instructions for each waste type
 */

export interface DisposalStep {
  icon: string;
  text: string;
}

export interface DisposalInfo {
  className: string;
  binType: 'recyclable' | 'hazardous' | 'general' | 'organic';
  steps: DisposalStep[];
  tips?: string[];
  warnings?: string[];
}

export const DISPOSAL_INSTRUCTIONS: Record<string, DisposalInfo> = {
  'Nhựa': {
    className: 'Nhựa',
    binType: 'recyclable',
    steps: [
      { icon: '🚿', text: 'Rửa sạch chai/hộp nhựa' },
      { icon: '🏷️', text: 'Gỡ nhãn và nắp đậy' },
      { icon: '💨', text: 'Bóp dẹp để tiết kiệm không gian' },
      { icon: '♻️', text: 'Bỏ vào thùng tái chế' }
    ],
    tips: [
      'Nhựa sạch có giá trị tái chế cao hơn',
      'Các loại nhựa PET (chai nước) dễ tái chế nhất'
    ]
  },

  'Giấy': {
    className: 'Giấy',
    binType: 'recyclable',
    steps: [
      { icon: '📄', text: 'Gỡ bỏ kẹp, ghim kim loại' },
      { icon: '✂️', text: 'Xé hoặc cắt nhỏ nếu cần' },
      { icon: '🚫', text: 'Tránh làm ướt giấy' },
      { icon: '♻️', text: 'Bỏ vào thùng tái chế' }
    ],
    tips: [
      'Giấy ướt hoặc dính dầu mỡ không tái chế được',
      'Giấy báo, sách vở đều có thể tái chế'
    ]
  },

  'Hộp giấy': {
    className: 'Hộp giấy',
    binType: 'recyclable',
    steps: [
      { icon: '📦', text: 'Gỡ băng keo, nhãn dán' },
      { icon: '🔨', text: 'Dẹp phẳng hộp' },
      { icon: '✂️', text: 'Cắt nhỏ nếu quá lớn' },
      { icon: '♻️', text: 'Bỏ vào thùng tái chế' }
    ],
    tips: [
      'Hộp giấy sạch có giá trị cao',
      'Carton sóng dùng làm bao bì rất tốt'
    ]
  },

  'Kim loại': {
    className: 'Kim loại',
    binType: 'recyclable',
    steps: [
      { icon: '🚿', text: 'Rửa sạch lon, hộp kim loại' },
      { icon: '💨', text: 'Bóp dẹp lon nhôm' },
      { icon: '🔍', text: 'Kiểm tra không có rỉ sét' },
      { icon: '♻️', text: 'Bỏ vào thùng tái chế' }
    ],
    tips: [
      'Kim loại có giá trị tái chế rất cao',
      'Lon nhôm có thể tái chế vô hạn lần'
    ]
  },

  'Thủy tinh': {
    className: 'Thủy tinh',
    binType: 'recyclable',
    steps: [
      { icon: '🚿', text: 'Rửa sạch chai/lọ thủy tinh' },
      { icon: '🏷️', text: 'Gỡ nhãn dán' },
      { icon: '⚠️', text: 'Cẩn thận với mảnh vỡ' },
      { icon: '♻️', text: 'Bỏ vào thùng tái chế' }
    ],
    tips: [
      'Thủy tinh có thể tái chế 100%',
      'Màu sắc khác nhau cần phân loại riêng'
    ],
    warnings: [
      'Cẩn thận khi xử lý thủy tinh vỡ'
    ]
  },

  'Pin': {
    className: 'Pin',
    binType: 'hazardous',
    steps: [
      { icon: '⚠️', text: 'KHÔNG vứt vào thùng rác thường' },
      { icon: '🔋', text: 'Bọc cách điện 2 đầu pin' },
      { icon: '📦', text: 'Đựng trong túi riêng' },
      { icon: '🏪', text: 'Đem đến điểm thu gom pin' }
    ],
    tips: [
      'Pin chứa hóa chất độc hại',
      'Nhiều cửa hàng điện tử thu gom pin miễn phí'
    ],
    warnings: [
      '⚠️ RÁC NGUY HẠI - Không vứt bừa bãi',
      '☠️ Pin có thể gây ô nhiễm môi trường nghiêm trọng',
      '🔥 Pin Lithium có nguy cơ cháy nổ'
    ]
  },

  'Hữu cơ': {
    className: 'Hữu cơ',
    binType: 'organic',
    steps: [
      { icon: '🍃', text: 'Gom rác thực phẩm vào túi' },
      { icon: '💧', text: 'Để ráo nước nếu có thể' },
      { icon: '🌱', text: 'Có thể làm phân compost' },
      { icon: '🗑️', text: 'Bỏ vào thùng rác thông thường' }
    ],
    tips: [
      'Rác hữu cơ có thể làm phân bón',
      'Tránh trộn với rác tái chế'
    ]
  },

  'Vải': {
    className: 'Vải',
    binType: 'recyclable',
    steps: [
      { icon: '👕', text: 'Kiểm tra còn sử dụng được không' },
      { icon: '🎁', text: 'Quần áo tốt → Quyên góp' },
      { icon: '♻️', text: 'Vải cũ → Tái chế làm giẻ lau' },
      { icon: '🗑️', text: 'Vải rách nát → Thùng thông thường' }
    ],
    tips: [
      'Quần áo cũ có thể quyên góp',
      'Vải cotton dễ phân hủy hơn vải tổng hợp'
    ]
  },

  'Rác thải': {
    className: 'Rác thải',
    binType: 'general',
    steps: [
      { icon: '🗑️', text: 'Gom vào túi rác' },
      { icon: '🔒', text: 'Buộc chặt túi' },
      { icon: '🚮', text: 'Bỏ vào thùng rác thông thường' },
      { icon: '🚛', text: 'Chờ xe thu gom' }
    ],
    tips: [
      'Phân loại trước khi vứt giúp môi trường',
      'Giảm thiểu rác thải bằng cách tái sử dụng'
    ]
  }
};

// Aliases for unaccented names from YOLO model
DISPOSAL_INSTRUCTIONS['Pin'] = DISPOSAL_INSTRUCTIONS['Pin'];
DISPOSAL_INSTRUCTIONS['Huu co'] = DISPOSAL_INSTRUCTIONS['Hữu cơ'];
DISPOSAL_INSTRUCTIONS['Hop giay'] = DISPOSAL_INSTRUCTIONS['Hộp giấy'];
DISPOSAL_INSTRUCTIONS['Thuy tinh'] = DISPOSAL_INSTRUCTIONS['Thủy tinh'];
DISPOSAL_INSTRUCTIONS['Kim loai'] = DISPOSAL_INSTRUCTIONS['Kim loại'];
DISPOSAL_INSTRUCTIONS['Giay'] = DISPOSAL_INSTRUCTIONS['Giấy'];
DISPOSAL_INSTRUCTIONS['Nhua'] = DISPOSAL_INSTRUCTIONS['Nhựa'];
DISPOSAL_INSTRUCTIONS['Vai'] = DISPOSAL_INSTRUCTIONS['Vải'];
DISPOSAL_INSTRUCTIONS['Rac thai'] = DISPOSAL_INSTRUCTIONS['Rác thải'];

/**
 * Get disposal instructions for a class
 */
export function getDisposalInstructions(className: string): DisposalInfo | null {
  return DISPOSAL_INSTRUCTIONS[className] || null;
}

/**
 * Get hazard level for a class
 */
export function getHazardLevel(binType: string): 'high' | 'medium' | 'low' {
  switch (binType) {
    case 'hazardous':
      return 'high';
    case 'recyclable':
      return 'low';
    case 'organic':
      return 'medium';
    default:
      return 'medium';
  }
}
