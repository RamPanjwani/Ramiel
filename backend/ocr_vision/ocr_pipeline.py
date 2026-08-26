"""Offline OCR Pipeline for Ramiel.

Phase 6: Multimodal (OCR + Vision).
Extracts text and layout from scanned PDFs, inspection reports, and image files
using an offline PaddleOCR engine per Rules.md §2.1.
"""

from __future__ import annotations


class OCRPipeline:
    """Offline OCR extraction pipeline using local models."""

    def __init__(self, use_gpu: bool = False) -> None:
        self.use_gpu = use_gpu

    def extract_text(self, image_path: str) -> str:
        """Extract text content from an image or scanned document page.

        Args:
            image_path: Path to the image file on local disk.

        Returns:
            Extracted text content with normalized whitespace and line breaks.

        Raises:
            FileNotFoundError: If the image file cannot be located.
            ValueError: If the file format is unsupported or corrupted.
            NotImplementedError: Implementation pending Phase 6.
        """
        raise NotImplementedError("OCRPipeline.extract_text is not yet implemented.")
