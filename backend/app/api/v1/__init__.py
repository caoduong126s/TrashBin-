"""
API v1 Routes
"""

from . import health
from . import classify
from . import statistics
from . import realtime

__all__ = ["health", "classify", "statistics", "realtime"]