"""Review alternative text when repository images change."""

from .models import Finding, ImageChange, ImageReference, Report
from .scanner import scan_repository

__all__ = ["Finding", "ImageChange", "ImageReference", "Report", "scan_repository"]
__version__ = "0.1.0"
