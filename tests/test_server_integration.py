"""서버 통합 테스트 (실제 API 호출 - 네트워크 필요)

실행: uv run pytest tests/test_server_integration.py -m integration
"""

import pytest
from ref_finder_mcp.server import (
    search_papers,
    get_paper_details,
    generate_citation,
    save_paper,
    list_saved_papers,
    remove_paper,
    export_bibliography,
    saved_papers,
)

pytestmark = pytest.mark.integration

REACT_PAPER_ID = "arxiv:2210.03629"


@pytest.fixture(autouse=True)
def _clear_saved_papers():
    """각 테스트 전후로 saved_papers 초기화"""
    saved_papers.clear()
    yield
    saved_papers.clear()


class TestSearchPapers:
    async def test_search_arxiv(self):
        result = await search_papers(query="ReAct reasoning acting", max_results=3)

        assert result["total"] > 0
        assert result["sources_queried"] == ["arxiv"]
        assert len(result["papers"]) <= 3

        paper = result["papers"][0]
        assert "title" in paper
        assert "authors" in paper
        assert "year" in paper

    async def test_search_with_categories(self):
        result = await search_papers(
            query="ReAct Synergizing Reasoning Acting Language Models",
            max_results=5,
            categories=["cs.AI", "cs.CL", "cs.LG"],
        )

        assert result["total"] > 0
        assert any("ReAct" in p["title"] for p in result["papers"])


class TestPaperDetails:
    async def test_get_paper_by_arxiv_id(self):
        details = await get_paper_details(REACT_PAPER_ID)

        assert "error" not in details
        assert "ReAct" in details["title"]
        assert details["year"] == 2022
        assert len(details["authors"]) > 0
        assert details["arxiv_id"] == "2210.03629"

    async def test_get_paper_invalid_id(self):
        result = await get_paper_details("unsupported:12345")
        assert "error" in result

    async def test_get_paper_nonexistent(self):
        result = await get_paper_details("arxiv:0000.00000")
        assert "error" in result


class TestCitation:
    async def test_generate_bibtex(self):
        result = await generate_citation(REACT_PAPER_ID, format="bibtex")

        assert "error" not in result
        assert result["format"] == "bibtex"
        assert "@article{" in result["citation"]
        assert "ReAct" in result["citation"]

    async def test_generate_apa(self):
        result = await generate_citation(REACT_PAPER_ID, format="apa")

        assert "error" not in result
        assert result["format"] == "apa"
        assert "(2022)" in result["citation"]
        assert "ReAct" in result["citation"]


class TestPaperManagement:
    async def test_save_and_list(self):
        save_result = await save_paper(REACT_PAPER_ID)

        assert save_result["status"] == "success"
        assert save_result["total_saved"] == 1
        assert "ReAct" in save_result["title"]

        list_result = await list_saved_papers()
        assert list_result["total"] == 1
        assert list_result["papers"][0]["id"] == REACT_PAPER_ID

    async def test_remove_paper(self):
        await save_paper(REACT_PAPER_ID)
        result = await remove_paper(REACT_PAPER_ID)

        assert result["status"] == "success"
        assert result["total_saved"] == 0

    async def test_remove_nonexistent(self):
        result = await remove_paper("arxiv:nonexistent")
        assert "error" in result


class TestExportBibliography:
    async def test_export_bibtex(self):
        await save_paper(REACT_PAPER_ID)
        result = await export_bibliography(format="bibtex")

        assert result["total_papers"] == 1
        assert "@article{" in result["bibliography"]

    async def test_export_apa(self):
        await save_paper(REACT_PAPER_ID)
        result = await export_bibliography(format="apa")

        assert result["total_papers"] == 1
        assert "(2022)" in result["bibliography"]

    async def test_export_empty(self):
        result = await export_bibliography(format="bibtex")
        assert "error" in result
