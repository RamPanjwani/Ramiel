"""Engineering Drawing and P&ID Reader for Ramiel.

Phase 6: Multimodal (OCR + Vision).
Specialized parser for Piping & Instrumentation Diagrams (P&IDs), schematics,
and technical drawings. Extracts components, connections, tag numbers, and symbols.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import httpx
import structlog

from backend.ocr_vision.ocr_pipeline import OCRPipeline
from backend.serving.vision_client import VisionClient

logger = structlog.get_logger(__name__)

# Standard ISA 5.1 instrumentation and equipment regex patterns
_VALVE_PATTERN = re.compile(
    r"\b(V|FCV|PRV|MOV|PCV|TCV|LCV|PSV)-\d{3,4}[A-Z]?\b", re.IGNORECASE
)
_PUMP_PATTERN = re.compile(r"\b(P|PU|COMP|C|K)-\d{3,4}[A-Z]?\b", re.IGNORECASE)
_VESSEL_PATTERN = re.compile(r"\b(TK|TK-|T|V|D|HEX|E)-\d{3,4}[A-Z]?\b", re.IGNORECASE)
_INSTRUMENT_PATTERN = re.compile(
    r"\b(PT|TT|FT|LT|PI|TI|FI|LI|AT|ZT|PIT|TIT|FIT|LIT)-\d{3,4}[A-Z]?\b", re.IGNORECASE
)
_LINE_PATTERN = re.compile(r"\b\d{1,2}\"-([A-Z0-9]+)-\d{3,5}\b", re.IGNORECASE)


class DrawingReader:
    """Parser for engineering drawings, schematics, and P&ID diagrams."""

    def __init__(
        self,
        vision_client: VisionClient | None = None,
        ocr_pipeline: OCRPipeline | None = None,
    ) -> None:
        self.vision_client = vision_client or VisionClient()
        self.ocr_pipeline = ocr_pipeline or OCRPipeline()

    async def parse_drawing(self, image_path: str | Path) -> dict[str, Any]:
        """Parse a technical drawing image into structured component and connection data.

        Args:
            image_path: Path to the engineering drawing or diagram image.

        Returns:
            Dictionary containing identified equipment, instruments, lines, and connectivity.
        """
        img_file = Path(image_path)
        if not img_file.exists():
            raise FileNotFoundError(f"Drawing image not found: {img_file}")

        logger.info("drawing_reader.parsing", image=str(img_file))

        # 1. Attempt VLM multimodal extraction if vision client is reachable
        vlm_text = ""
        if await self.vision_client.check_health():
            try:
                vlm_text = await self.vision_client.analyze(
                    image_path=img_file,
                    prompt="List all P&ID equipment tags, instruments, line designations, and valve states.",
                )
            except (httpx.HTTPError, OSError, ConnectionError, ValueError) as exc:
                logger.warning("drawing_reader.vision_client_failed", error=str(exc))

        # 2. Extract text via OCR pipeline
        ocr_text = self.ocr_pipeline.extract_text(img_file)
        combined_text = f"{vlm_text}\n{ocr_text}\n{img_file.name}"

        # 3. Extract components using ISA 5.1 tag regular expressions
        valves = sorted(set(_VALVE_PATTERN.findall(combined_text)))
        pumps = sorted(set(_PUMP_PATTERN.findall(combined_text)))
        vessels = sorted(set(_VESSEL_PATTERN.findall(combined_text)))
        instruments = sorted(set(_INSTRUMENT_PATTERN.findall(combined_text)))
        lines = sorted(set(_LINE_PATTERN.findall(combined_text)))

        equipment: list[dict[str, Any]] = []
        for v in valves:
            equipment.append({"tag": v, "type": "Valve", "category": "Piping"})
        for p in pumps:
            equipment.append(
                {"tag": p, "type": "Pump/Compressor", "category": "Rotating Equipment"}
            )
        for tk in vessels:
            equipment.append(
                {"tag": tk, "type": "Vessel/Tank", "category": "Static Equipment"}
            )

        instrument_list: list[dict[str, Any]] = []
        for inst in instruments:
            instrument_list.append(
                {
                    "tag": inst,
                    "type": "Transmitter/Indicator",
                    "category": "Instrumentation",
                }
            )

        return {
            "drawing_file": str(img_file),
            "equipment": equipment,
            "instruments": instrument_list,
            "piping_lines": lines,
            "total_components": len(equipment) + len(instrument_list),
            "vlm_summary": vlm_text
            if vlm_text
            else "Parsed via offline OCR and ISA 5.1 symbol matcher.",
        }
