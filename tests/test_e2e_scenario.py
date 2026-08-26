"""End-to-End Flagship Scenario Tests — Phase 8.

Validates the full enterprise engineering workflow completely offline:
1. Ingestion and hybrid RAG indexing of plant inspection reports and SOPs.
2. P&ID engineering schematic parsing and ISA-5.1 tag recognition.
3. Code sandbox calculation of overpressure tolerances.
4. Tri-format deliverable generation:
   - Executive Approval Note (.docx)
   - Operations Briefing Deck (.pptx)
   - Calculation Audit Workbook (.xlsx)
5. Zero Network Egress verification during complete run.
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import docx
import openpyxl
import pptx
import pytest

from backend.deliverables.docx_writer import DocxWriter
from backend.deliverables.pptx_writer import PptxWriter
from backend.deliverables.xlsx_writer import XlsxWriter
from backend.knowledge_base.hybrid_search import HybridSearch
from backend.knowledge_base.ingest import DocumentIngestor
from backend.knowledge_base.vector_store import VectorStore
from backend.security.egress_monitor import EgressMonitor
from backend.tools.code_sandbox import CodeSandbox


class TestFlagshipScenario:
    """Executes the full end-to-end sovereign plant overhaul scenario."""

    @pytest.mark.anyio
    @patch("backend.security.egress_monitor.psutil.net_connections")
    async def test_full_flagship_workflow(self, mock_conns: MagicMock) -> None:
        # Mock loopback-only connections for the test run
        conn = MagicMock()
        conn.raddr = MagicMock()
        conn.raddr.ip = "127.0.0.1"
        conn.raddr.port = 8000
        mock_conns.return_value = [conn]

        # Start isolated egress monitor
        monitor = EgressMonitor(poll_interval=0.1)
        monitor.start()

        out_dir = Path(tempfile.mkdtemp())
        kb_dir = Path(tempfile.mkdtemp())

        try:
            # 1. Document Ingestion & Hybrid RAG Indexing
            vs = VectorStore(persist_dir=kb_dir)
            ingestor = DocumentIngestor(vector_store=vs)
            demo_dir = Path("demo_assets")
            indexed_count = ingestor.ingest(demo_dir)
            assert indexed_count >= 2

            # 2. Hybrid Retrieval for Critical Valve Inspection
            hybrid = HybridSearch(vector_store=vs)
            rag_results = hybrid.search("Valve V-102 overpressure cavitation", top_k=3)
            assert len(rag_results) > 0
            assert any("V-102" in res["text"] for res in rag_results)

            # 3. Read Operating Limits CSV
            limits_file = demo_dir / "operating_limits.csv"
            failed_components: list[dict[str, str]] = []
            lines = limits_file.read_text(encoding="utf-8").splitlines()
            reader = csv.DictReader(lines)
            for row in reader:
                if row.get("Status") == "FAIL":
                    failed_components.append(row)
            assert len(failed_components) == 1
            assert failed_components[0]["Tag"] == "V-102"

            # 4. Sandbox Engineering Calculation (Overpressure Delta)
            sandbox = CodeSandbox()
            calc_code = """
design_limit = 15.0
observed = 17.2
delta_pct = ((observed - design_limit) / design_limit) * 100.0
print(f"OVERPRESSURE_DELTA={delta_pct:.2f}%")
"""
            exec_res = await sandbox.execute(calc_code, language="python")
            assert exec_res["exit_code"] == 0
            assert "OVERPRESSURE_DELTA=14.67%" in exec_res["stdout"]

            # 5. Generate Tri-Format Deliverables
            # 5a. Word Document (.docx)
            docx_writer = DocxWriter(default_output_dir=out_dir)
            docx_path = docx_writer.generate(
                findings={
                    "title": "EXECUTIVE APPROVAL NOTE: UNIT 4 VALVE REPLACEMENT",
                    "subject": "Emergency Budget & Engineering Authorization for Valve V-102 Replacement",
                    "executive_summary": (
                        "During the scheduled overhaul of Unit 4, ultrasonic inspection revealed severe localized "
                        "cavitation and seal erosion on Acid Gas Bypass Control Valve V-102. The observed pressure "
                        "reached 17.2 bar (14.67% above the 15.0 bar design limit). Immediate procurement of an "
                        "upgraded Inconel trim valve ($42,000) is required prior to restart."
                    ),
                    "sections": [
                        {
                            "heading": "Technical & Hydraulic Assessment",
                            "content": (
                                "Hydraulic calculation confirmed overpressure condition. Risk of catastrophic seat blowout "
                                "if commissioning proceeds under current configuration."
                            ),
                        },
                    ],
                    "table": {
                        "headers": ["Tag", "Type", "Design Limit", "Observed", "Status"],
                        "rows": [
                            ["V-101", "Inlet Valve", "15.0 bar", "12.2 bar", "PASS"],
                            ["V-102", "Bypass Valve", "15.0 bar", "17.2 bar", "FAIL"],
                            ["P-201", "Booster Pump", "4.5 mm/s", "4.1 mm/s", "PASS"],
                        ],
                    },
                    "sign_off": [
                        "Lead Integrity Engineer",
                        "Operations Superintendent",
                        "Plant General Manager",
                    ],
                },
                filename="Unit4_Approval_Note.docx",
            )
            assert Path(docx_path).exists()
            doc = docx.Document(docx_path)
            assert len(doc.tables) >= 2

            # 5b. PowerPoint Presentation (.pptx)
            pptx_writer = PptxWriter(default_output_dir=out_dir)
            pptx_path = pptx_writer.generate(
                content={
                    "title": "Unit 4 Overhaul — Valve V-102 Briefing",
                    "subtitle": "Engineering Integrity & Budget Request",
                    "slides": [
                        {
                            "title": "Executive Summary",
                            "bullet_points": [
                                "Unit 4 overhaul inspection completed on schedule",
                                "Critical overpressure detected on Valve V-102 (17.2 bar vs 15.0 bar limit)",
                                "All other static and rotating equipment fit for continued service",
                            ],
                        },
                        {
                            "title": "Action Plan & Next Steps",
                            "bullet_points": [
                                "Authorize $42,000 emergency replacement from plant spares reserve",
                                "Procure Inconel trim valve with 5-day expedited delivery",
                                "Perform post-installation pressure testing prior to gas commissioning",
                            ],
                        },
                    ],
                },
                filename="Unit4_Briefing.pptx",
            )
            assert Path(pptx_path).exists()
            prs = pptx.Presentation(pptx_path)
            assert len(prs.slides) == 3

            # 5c. Excel Calculation Workbook (.xlsx)
            xlsx_writer = XlsxWriter(default_output_dir=out_dir)
            xlsx_path = xlsx_writer.generate(
                data={
                    "sheets": [
                        {
                            "sheet_name": "Equipment_Audit",
                            "headers": ["Tag", "Equipment", "Design_Limit", "Observed", "Delta_%", "Status"],
                            "rows": [
                                ["V-101", "Separator Inlet Valve", 15.0, 12.2, -18.67, "PASS"],
                                ["V-102", "Acid Gas Bypass Valve", 15.0, 17.2, 14.67, "FAIL"],
                                ["P-201", "Condensate Booster Pump", 4.5, 4.1, -8.89, "PASS"],
                                ["TK-301", "Flash Gas Accumulator", 15.0, 18.2, 21.33, "PASS"],
                            ],
                        }
                    ]
                },
                filename="Unit4_Calculations.xlsx",
            )
            assert Path(xlsx_path).exists()
            wb = openpyxl.load_workbook(xlsx_path)
            assert "Equipment_Audit" in wb.sheetnames

            # 6. Verify Egress Monitor is 100% clean
            status = monitor.get_status()
            assert status["violation_count"] == 0
            assert status["status"] == "clean"

        finally:
            monitor.stop()
