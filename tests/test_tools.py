"""Tool Layer Tests — Phase 3.

Validates:
1. ScopedFileIO directory boundaries and path traversal protection.
2. CodeSandbox execution, timeout handling, and network isolation policy.
3. SpreadsheetTool Excel read/write and summary calculations.
4. ToolRegistry tool registration, schema formatting, and invocation.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backend.tools.code_sandbox import CodeSandbox
from backend.tools.file_io import ScopedFileIO
from backend.tools.spreadsheet import SpreadsheetTool
from backend.tools.tool_registry import ToolRegistry


class TestScopedFileIO:
    """Test filesystem permissions and scoping."""

    @pytest.fixture
    def file_io(self) -> ScopedFileIO:
        return ScopedFileIO(config_path="config/tool_permissions.yaml")

    def test_write_and_read_within_allowed_root(self, file_io: ScopedFileIO) -> None:
        """Writing and reading within allowed roots (data/uploads) must succeed."""
        test_rel_path = "data/uploads/test_file_io.txt"
        test_content = "Confidential PSU Report Data"

        file_io.write(test_rel_path, test_content)
        read_back = file_io.read(test_rel_path)
        assert read_back == test_content
        assert file_io.exists(test_rel_path) is True

    def test_read_outside_allowed_root_blocked(self, file_io: ScopedFileIO) -> None:
        """Reading from paths outside permitted roots must raise PermissionError."""
        with pytest.raises(PermissionError, match="outside allowed root boundaries"):
            file_io.read("../../some_external_secret.txt")

    def test_write_outside_allowed_root_blocked(self, file_io: ScopedFileIO) -> None:
        """Writing outside allowed write roots must raise PermissionError."""
        with pytest.raises(PermissionError, match="outside allowed root boundaries"):
            file_io.write("config/model_registry.yaml", "malicious_overwrite: true")

    def test_list_dir(self, file_io: ScopedFileIO) -> None:
        """Listing directories inside allowed roots succeeds."""
        items = file_io.list_dir("data/uploads")
        assert isinstance(items, list)


class TestCodeSandbox:
    """Test sandbox execution and isolation."""

    @pytest.fixture
    def sandbox(self) -> CodeSandbox:
        return CodeSandbox(config_path="config/tool_permissions.yaml")

    @pytest.mark.anyio
    async def test_sandbox_execute_python(self, sandbox: CodeSandbox) -> None:
        """Execute simple Python code in sandbox."""
        code = "print(21 * 2)"
        res = await sandbox.execute(code=code, language="python")
        assert res["exit_code"] == 0
        assert res["stdout"].strip() == "42"
        assert res["timed_out"] is False

    @pytest.mark.anyio
    async def test_sandbox_timeout(self, sandbox: CodeSandbox) -> None:
        """Code exceeding timeout should be killed."""
        code = "import time\ntime.sleep(5)\nprint('done')"
        res = await sandbox.execute(code=code, language="python", timeout=1)
        assert res["timed_out"] is True
        assert res["exit_code"] == -1
        assert "timed out" in res["stderr"]

    def test_sandbox_policy_network_none(self, sandbox: CodeSandbox) -> None:
        """Sandbox policy must enforce network_mode == 'none'."""
        assert sandbox.policy.network_mode == "none"


class TestSpreadsheet:
    """Test spreadsheet inspection and generation."""

    @pytest.fixture
    def spreadsheet(self) -> SpreadsheetTool:
        return SpreadsheetTool()

    def test_write_and_read_excel(self, spreadsheet: SpreadsheetTool) -> None:
        """Write tabular data to Excel and read back structured rows."""
        tmp_dir = tempfile.mkdtemp()
        xlsx_path = Path(tmp_dir) / "valve_calculations.xlsx"

        data = {
            "Valve_ID": ["V-101", "V-102", "V-103"],
            "Pressure_Bar": [12.5, 14.2, 11.8],
            "Flow_Rate_m3h": [150.0, 185.5, 142.0],
        }

        saved_path = spreadsheet.write_excel(xlsx_path, data, sheet_name="Calculations")
        assert Path(saved_path).exists()

        result = spreadsheet.read_excel(saved_path)
        assert "Calculations" in result["sheet_names"]
        sheet = result["sheets"]["Calculations"]
        assert "Valve_ID" in sheet["headers"]
        assert "Pressure_Bar" in sheet["headers"]
        assert sheet["total_rows"] == 3

    def test_summary_stats(self, spreadsheet: SpreadsheetTool) -> None:
        """Compute statistical metrics across numeric columns."""
        tmp_dir = tempfile.mkdtemp()
        xlsx_path = Path(tmp_dir) / "stats_test.xlsx"

        data = {
            "Reading": [10.0, 20.0, 30.0, 40.0],
            "Tag": ["A", "B", "C", "D"],
        }
        spreadsheet.write_excel(xlsx_path, data)

        summary = spreadsheet.summary_stats(xlsx_path)
        assert "Reading" in summary["numeric_columns"]
        assert summary["stats"]["Reading"]["mean"] == 25.0
        assert summary["stats"]["Reading"]["max"] == 40.0


class TestToolRegistry:
    """Test tool discovery and schema serialization."""

    @pytest.fixture
    def registry(self) -> ToolRegistry:
        return ToolRegistry()

    def test_default_tools_registered(self, registry: ToolRegistry) -> None:
        """All Phase 3 tools must be present in registry."""
        tools = registry.list_tools()
        assert "file_read" in tools
        assert "file_write" in tools
        assert "code_exec" in tools
        assert "spreadsheet_read" in tools
        assert "spreadsheet_write" in tools

    def test_get_schemas(self, registry: ToolRegistry) -> None:
        """Tool schemas must be properly formatted dictionaries."""
        schemas = registry.get_schemas()
        assert len(schemas) >= 5
        names = [s["name"] for s in schemas]
        assert "code_exec" in names

    @pytest.mark.anyio
    async def test_tool_execution(self, registry: ToolRegistry) -> None:
        """Execute tool via registry interface."""
        test_path = "data/uploads/registry_test.txt"
        test_content = "Tool Registry Verified"

        await registry.execute("file_write", path=test_path, content=test_content)
        read_back = await registry.execute("file_read", path=test_path)
        assert read_back == test_content
