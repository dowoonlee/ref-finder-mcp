"""Paper 모델 테스트"""

import pytest
from ref_finder_mcp.models.paper import Paper


def test_paper_creation():
    """Paper 객체 생성 테스트"""
    paper = Paper(
        id="arxiv:2210.03629",
        title="ReAct: Synergizing Reasoning and Acting in Language Models",
        authors=["Shunyu Yao", "Jeffrey Zhao", "Dian Yu"],
        year=2022,
        source="arxiv",
        arxiv_id="2210.03629",
    )

    assert paper.id == "arxiv:2210.03629"
    assert paper.title == "ReAct: Synergizing Reasoning and Acting in Language Models"
    assert len(paper.authors) == 3
    assert paper.year == 2022


def test_paper_to_bibtex():
    """BibTeX 변환 테스트"""
    paper = Paper(
        id="arxiv:2210.03629",
        title="ReAct: Synergizing Reasoning and Acting in Language Models",
        authors=["Shunyu Yao", "Jeffrey Zhao", "Dian Yu"],
        year=2022,
        source="arxiv",
        arxiv_id="2210.03629",
    )

    bibtex = paper.to_bibtex()

    assert "@article{" in bibtex
    assert "title={ReAct" in bibtex
    assert "author={Shunyu Yao and Jeffrey Zhao and Dian Yu}" in bibtex
    assert "year={2022}" in bibtex
    assert "arXiv:2210.03629" in bibtex


def test_paper_to_apa():
    """APA 변환 테스트"""
    paper = Paper(
        id="arxiv:2210.03629",
        title="ReAct: Synergizing Reasoning and Acting in Language Models",
        authors=["Shunyu Yao", "Jeffrey Zhao", "Dian Yu"],
        year=2022,
        source="arxiv",
        arxiv_id="2210.03629",
    )

    apa = paper.to_apa()

    assert "Shunyu Yao" in apa
    assert "Jeffrey Zhao" in apa
    assert "Dian Yu" in apa
    assert "(2022)" in apa
    assert "ReAct" in apa


def test_paper_to_dict():
    """딕셔너리 변환 테스트"""
    paper = Paper(
        id="arxiv:2210.03629",
        title="ReAct: Synergizing Reasoning and Acting in Language Models",
        authors=["Shunyu Yao", "Jeffrey Zhao"],
        year=2022,
        source="arxiv",
    )

    data = paper.to_dict()

    assert data["id"] == "arxiv:2210.03629"
    assert data["title"] == "ReAct: Synergizing Reasoning and Acting in Language Models"
    assert len(data["authors"]) == 2
    assert data["year"] == 2022


def test_paper_from_dict():
    """딕셔너리로부터 생성 테스트"""
    data = {
        "id": "arxiv:2210.03629",
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "authors": ["Shunyu Yao", "Jeffrey Zhao"],
        "year": 2022,
        "source": "arxiv",
        "abstract": None,
        "doi": None,
        "arxiv_id": "2210.03629",
        "url": None,
        "citation_count": None,
        "venue": None,
        "pdf_url": None,
        "fetched_at": "2026-03-06T12:00:00",
    }

    paper = Paper.from_dict(data)

    assert paper.id == "arxiv:2210.03629"
    assert paper.title == "ReAct: Synergizing Reasoning and Acting in Language Models"
    assert len(paper.authors) == 2
