"""중복 제거 로직 테스트"""

from ref_finder_mcp.models.paper import Paper
from ref_finder_mcp.utils.dedup import deduplicate_papers, _normalize_title


def _make_paper(**kwargs) -> Paper:
    defaults = {
        "id": "test:1",
        "title": "Test Paper",
        "authors": ["Author A"],
        "year": 2022,
        "source": "arxiv",
    }
    defaults.update(kwargs)
    return Paper(**defaults)


class TestNormalizeTitle:
    def test_basic(self):
        assert _normalize_title("Hello World") == "helloworld"

    def test_special_chars(self):
        assert _normalize_title("ReAct: Synergizing Reasoning & Acting") == (
            "reactsynergizingreasoningacting"
        )

    def test_unicode(self):
        assert _normalize_title("Résumé of Naïve Approach") == "resumeofnaiveapproach"

    def test_whitespace_variations(self):
        assert _normalize_title("  multiple   spaces  ") == "multiplespaces"


class TestDeduplicateByArxivId:
    def test_same_arxiv_id(self):
        p1 = _make_paper(id="arxiv:2210.03629", source="arxiv", arxiv_id="2210.03629")
        p2 = _make_paper(
            id="s2:abc123", source="semantic_scholar", arxiv_id="2210.03629",
            citation_count=500,
        )

        result = deduplicate_papers([p1, p2])

        assert len(result) == 1
        assert result[0].citation_count == 500

    def test_different_arxiv_id(self):
        p1 = _make_paper(id="arxiv:2210.03629", arxiv_id="2210.03629")
        p2 = _make_paper(id="arxiv:2301.00001", arxiv_id="2301.00001", title="Other Paper")

        result = deduplicate_papers([p1, p2])

        assert len(result) == 2


class TestDeduplicateByDoi:
    def test_same_doi(self):
        p1 = _make_paper(id="arxiv:111", source="arxiv", doi="10.1234/test")
        p2 = _make_paper(
            id="s2:222", source="semantic_scholar", doi="10.1234/test",
            venue="NeurIPS 2022",
        )

        result = deduplicate_papers([p1, p2])

        assert len(result) == 1
        assert result[0].venue == "NeurIPS 2022"

    def test_doi_case_insensitive(self):
        p1 = _make_paper(id="a:1", doi="10.1234/ABC")
        p2 = _make_paper(id="b:2", doi="10.1234/abc", abstract="some abstract")

        result = deduplicate_papers([p1, p2])

        assert len(result) == 1
        assert result[0].abstract == "some abstract"


class TestDeduplicateByTitle:
    def test_same_title_same_year(self):
        p1 = _make_paper(
            id="arxiv:111", source="arxiv",
            title="ReAct: Synergizing Reasoning and Acting in Language Models",
            year=2022,
        )
        p2 = _make_paper(
            id="scholar:222", source="google_scholar",
            title="ReAct: Synergizing Reasoning and Acting in Language Models",
            year=2022, citation_count=1000,
        )

        result = deduplicate_papers([p1, p2])

        assert len(result) == 1
        assert result[0].citation_count == 1000

    def test_title_with_minor_differences(self):
        p1 = _make_paper(id="a:1", title="Attention Is All You Need", year=2017)
        p2 = _make_paper(id="b:2", title="Attention is All You Need", year=2017)

        result = deduplicate_papers([p1, p2])

        assert len(result) == 1

    def test_same_title_different_year(self):
        p1 = _make_paper(id="a:1", title="Survey of Machine Learning", year=2020)
        p2 = _make_paper(id="b:2", title="Survey of Machine Learning", year=2023)

        result = deduplicate_papers([p1, p2])

        assert len(result) == 2


class TestMergeBehavior:
    def test_fills_missing_fields(self):
        p1 = _make_paper(
            id="arxiv:111", source="arxiv", arxiv_id="2210.03629",
            abstract="Full abstract here", doi=None, citation_count=None,
        )
        p2 = _make_paper(
            id="s2:222", source="semantic_scholar", arxiv_id="2210.03629",
            abstract=None, doi="10.1234/test", citation_count=500,
            venue="NeurIPS", pdf_url="https://example.com/paper.pdf",
        )

        result = deduplicate_papers([p1, p2])

        assert len(result) == 1
        merged = result[0]
        assert merged.abstract == "Full abstract here"
        assert merged.doi == "10.1234/test"
        assert merged.citation_count == 500
        assert merged.venue == "NeurIPS"
        assert merged.pdf_url == "https://example.com/paper.pdf"

    def test_no_papers(self):
        assert deduplicate_papers([]) == []

    def test_single_paper(self):
        p = _make_paper(id="a:1")
        assert len(deduplicate_papers([p])) == 1

    def test_three_duplicates(self):
        p1 = _make_paper(id="arxiv:111", source="arxiv", arxiv_id="2210.03629")
        p2 = _make_paper(
            id="s2:222", source="semantic_scholar", arxiv_id="2210.03629",
            citation_count=500,
        )
        p3 = _make_paper(
            id="scholar:333", source="google_scholar", arxiv_id="2210.03629",
            venue="NeurIPS",
        )

        result = deduplicate_papers([p1, p2, p3])

        assert len(result) == 1
        assert result[0].citation_count == 500
        assert result[0].venue == "NeurIPS"
