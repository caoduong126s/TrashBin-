"""
Utils package
"""

from app.utils.bin_mapping import (
    BinType,
    BIN_MAPPING,
    map_class_to_bin,
    smart_map,
    aggregate_bin_scores,
    check_composite_material,
    get_bin_info,
    get_all_bins_info,
)

from app.utils.recycling_tips import (
    get_recycling_tips,
    get_simple_tips,
    get_tips_with_icons,
    get_special_instruction,
)

__all__ = [
    'BinType',
    'BIN_MAPPING',
    'map_class_to_bin',
    'smart_map',
    'aggregate_bin_scores',
    'check_composite_material',
    'get_bin_info',
    'get_all_bins_info',
    'get_recycling_tips',
    'get_simple_tips',
    'get_tips_with_icons',
    'get_special_instruction',
]