"""ArxivHtmlClient HTML 파싱 유닛 테스트 (네트워크 불필요)"""

import pytest
from ref_finder_mcp.clients.arxiv_html import ArxivHtmlClient, PaperSection

SAMPLE_HTML = """<!DOCTYPE html><html lang="en">
<head><title>[2401.00001] Test Paper</title></head>
<body>
<div class="ltx_page_main">
<div class="ltx_page_content">
<article class="ltx_document ltx_authors_1line">

<h1 class="ltx_title ltx_title_document">Test Paper Title</h1>

<div class="ltx_authors">
<span class="ltx_creator ltx_role_author">
<span class="ltx_personname">Alice Smith, Bob Jones</span>
</span>
</div>

<div class="ltx_abstract">
<h6 class="ltx_title ltx_title_abstract">Abstract</h6>
<p class="ltx_p">This is the abstract of the test paper.</p>
</div>

<section id="S1" class="ltx_section">
<h2 class="ltx_title ltx_title_section">
<span class="ltx_tag ltx_tag_section">1 </span>Introduction</h2>
<div class="ltx_para">
<p class="ltx_p">This is the introduction paragraph.</p>
</div>
<div class="ltx_para">
<p class="ltx_p">Second paragraph with inline math
<math class="ltx_Math" display="inline">
<semantics><mi>x</mi>
<annotation encoding="application/x-tex">x^2 + y^2 = z^2</annotation>
</semantics></math> in it.</p>
</div>
</section>

<section id="S2" class="ltx_section">
<h2 class="ltx_title ltx_title_section">
<span class="ltx_tag ltx_tag_section">2 </span>Methods</h2>
<div class="ltx_para">
<p class="ltx_p">Methods overview paragraph.</p>
</div>

<section id="S2.SS1" class="ltx_subsection">
<h3 class="ltx_title ltx_title_subsection">
<span class="ltx_tag ltx_tag_subsection">2.1 </span>Data Collection</h3>
<div class="ltx_para">
<p class="ltx_p">We collected data from various sources.</p>
</div>
</section>

<section id="S2.SS2" class="ltx_subsection">
<h3 class="ltx_title ltx_title_subsection">
<span class="ltx_tag ltx_tag_subsection">2.2 </span>Analysis</h3>
<div class="ltx_para">
<p class="ltx_p">We analyzed the data using
<math class="ltx_Math" display="block">
<semantics><mi>E</mi>
<annotation encoding="application/x-tex">E = mc^2</annotation>
</semantics></math>.</p>
</div>
</section>
</section>

<section id="S3" class="ltx_section">
<h2 class="ltx_title ltx_title_section">
<span class="ltx_tag ltx_tag_section">3 </span>Results</h2>
<div class="ltx_para">
<p class="ltx_p">Our results show improvement.</p>
</div>
<figure class="ltx_figure">
<figcaption class="ltx_caption">
<span class="ltx_tag ltx_tag_figure">Figure 1: </span>Performance comparison chart.
</figcaption>
</figure>
<figure class="ltx_table">
<figcaption class="ltx_caption">
<span class="ltx_tag ltx_tag_table">Table 1: </span>Benchmark results summary.
</figcaption>
</figure>
</section>

<section class="ltx_bibliography">
<h2 class="ltx_title ltx_title_bibliography">References</h2>
<ul class="ltx_biblist">
<li class="ltx_bibitem">
<span class="ltx_tag">[1]</span>
<span class="ltx_bibblock">Smith et al. A great paper. 2023.</span>
</li>
<li class="ltx_bibitem">
<span class="ltx_tag">[2]</span>
<span class="ltx_bibblock">Jones et al. Another great paper. 2024.</span>
</li>
</ul>
</section>

</article>
</div>
</div>
</body>
</html>"""


@pytest.fixture
def client():
    return ArxivHtmlClient()


@pytest.fixture
def parsed(client):
    return client._parse_document(SAMPLE_HTML)


class TestParseDocument:
    def test_extracts_title(self, parsed):
        assert parsed["title"] == "Test Paper Title"

    def test_extracts_all_sections(self, parsed):
        ids = [s.id for s in parsed["sections"]]
        assert "abstract" in ids
        assert "S1" in ids
        assert "S2" in ids
        assert "S2.SS1" in ids
        assert "S2.SS2" in ids
        assert "S3" in ids
        assert "bibliography" in ids

    def test_section_count(self, parsed):
        assert len(parsed["sections"]) == 7

    def test_section_levels(self, parsed):
        level_map = {s.id: s.level for s in parsed["sections"]}
        assert level_map["abstract"] == 0
        assert level_map["S1"] == 1
        assert level_map["S2"] == 1
        assert level_map["S2.SS1"] == 2
        assert level_map["S2.SS2"] == 2
        assert level_map["S3"] == 1
        assert level_map["bibliography"] == 1

    def test_returns_none_for_invalid_html(self, client):
        assert client._parse_document("<html><body>No article here</body></html>") is None


class TestAbstract:
    def test_abstract_content(self, parsed):
        abstract = next(s for s in parsed["sections"] if s.id == "abstract")
        assert "abstract of the test paper" in abstract.content

    def test_abstract_title_excluded(self, parsed):
        abstract = next(s for s in parsed["sections"] if s.id == "abstract")
        assert not abstract.content.startswith("Abstract")


class TestMathExtraction:
    def test_inline_math(self, parsed):
        s1 = next(s for s in parsed["sections"] if s.id == "S1")
        assert "$x^2 + y^2 = z^2$" in s1.content

    def test_block_math(self, parsed):
        s2ss2 = next(s for s in parsed["sections"] if s.id == "S2.SS2")
        assert "$$E = mc^2$$" in s2ss2.content


class TestFigureTablePlaceholders:
    def test_figure_placeholder(self, parsed):
        s3 = next(s for s in parsed["sections"] if s.id == "S3")
        assert "[Figure 1:" in s3.content or "[Figure 1 " in s3.content
        assert "Performance comparison" in s3.content

    def test_table_placeholder(self, parsed):
        s3 = next(s for s in parsed["sections"] if s.id == "S3")
        assert "[Table 1:" in s3.content or "[Table 1 " in s3.content
        assert "Benchmark results" in s3.content


class TestBibliography:
    def test_bibliography_entries(self, parsed):
        bib = next(s for s in parsed["sections"] if s.id == "bibliography")
        assert "[1]" in bib.content
        assert "Smith et al." in bib.content
        assert "[2]" in bib.content
        assert "Jones et al." in bib.content


class TestSubsectionHandling:
    def test_parent_excludes_child_content(self, parsed):
        s2 = next(s for s in parsed["sections"] if s.id == "S2")
        assert "Methods overview" in s2.content
        assert "Data Collection" not in s2.content
        assert "collected data" not in s2.content

    def test_subsection_has_own_content(self, parsed):
        s2ss1 = next(s for s in parsed["sections"] if s.id == "S2.SS1")
        assert "collected data" in s2ss1.content


class TestClientMethods:
    def test_get_available_section_ids_empty(self, client):
        assert client.get_available_section_ids("nonexistent") == []

    def test_get_available_section_ids_after_parse(self, client):
        client._cache["test"] = client._parse_document(SAMPLE_HTML)
        ids = client.get_available_section_ids("test")
        assert "abstract" in ids
        assert "S1" in ids
        assert "S2.SS1" in ids
