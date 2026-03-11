"""arXiv 논문 HTML 본문 파싱 클라이언트 (ar5iv.labs.arxiv.org)"""

import re
from dataclasses import dataclass
from typing import Optional

import httpx
from bs4 import BeautifulSoup, Tag

AR5IV_BASE_URL = "https://ar5iv.labs.arxiv.org/html"


@dataclass
class PaperSection:
    id: str
    title: str
    level: int
    content: str = ""


class ArxivHtmlClient:
    """ar5iv HTML을 파싱하여 arXiv 논문 본문을 섹션 단위로 제공"""

    def __init__(self):
        self._cache: dict[str, dict] = {}

    async def _fetch_html(self, arxiv_id: str) -> Optional[str]:
        url = f"{AR5IV_BASE_URL}/{arxiv_id}"
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.text
            return None

    async def _get_parsed(self, arxiv_id: str) -> Optional[dict]:
        if arxiv_id in self._cache:
            return self._cache[arxiv_id]

        html = await self._fetch_html(arxiv_id)
        if html is None:
            return None

        parsed = self._parse_document(html)
        if parsed:
            self._cache[arxiv_id] = parsed
        return parsed

    def _parse_document(self, html: str) -> Optional[dict]:
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article", class_="ltx_document")
        if not article:
            return None

        title_el = article.find("h1", class_="ltx_title_document")
        title = title_el.get_text(strip=True) if title_el else ""

        sections: list[PaperSection] = []

        abstract_div = article.find("div", class_="ltx_abstract")
        if abstract_div:
            sections.append(PaperSection(
                id="abstract",
                title="Abstract",
                level=0,
                content=self._extract_text(abstract_div, skip_title=True),
            ))

        for section_el in article.find_all("section", class_="ltx_section", recursive=False):
            self._parse_section(section_el, sections, level=1)

        bib = article.find("section", class_="ltx_bibliography")
        if bib:
            sections.append(PaperSection(
                id="bibliography",
                title="References",
                level=1,
                content=self._extract_bibliography(bib),
            ))

        return {"title": title, "sections": sections}

    def _parse_section(
        self, el: Tag, sections: list[PaperSection], level: int
    ) -> None:
        section_id = el.get("id", "")
        title_tag = el.find(
            re.compile(r"^h[2-6]$"),
            class_=re.compile(r"ltx_title_section|ltx_title_subsection|ltx_title_subsubsection"),
            recursive=False,
        )
        title = title_tag.get_text(strip=True) if title_tag else ""

        subsection_class = {
            1: "ltx_subsection",
            2: "ltx_subsubsection",
        }.get(level, None)
        child_sections = (
            el.find_all("section", class_=subsection_class, recursive=False)
            if subsection_class
            else []
        )

        content = self._extract_section_content(el, exclude_subsections=bool(child_sections))

        sections.append(PaperSection(
            id=str(section_id),
            title=title,
            level=level,
            content=content,
        ))

        for child in child_sections:
            self._parse_section(child, sections, level=level + 1)

    def _extract_section_content(self, section_el: Tag, exclude_subsections: bool) -> str:
        """섹션의 직속 텍스트만 추출 (하위 섹션 제외 가능)"""
        parts: list[str] = []
        for child in section_el.children:
            if not isinstance(child, Tag):
                continue
            if child.name and re.match(r"^h[1-6]$", child.name):
                continue
            if exclude_subsections and child.name == "section":
                continue
            if "ltx_bibliography" in child.get("class", []):
                continue
            classes = child.get("class", [])
            if child.name == "figure" and "ltx_figure" in classes:
                parts.append(self._figure_placeholder(child, "Figure", "ltx_tag_figure"))
                continue
            if child.name == "figure" and "ltx_table" in classes:
                parts.append(self._figure_placeholder(child, "Table", "ltx_tag_table"))
                continue
            parts.append(self._extract_text(child))
        return "\n\n".join(p for p in parts if p.strip())

    @staticmethod
    def _figure_placeholder(el: Tag, default_label: str, tag_class: str) -> str:
        caption = el.find("figcaption")
        tag = el.find("span", class_=tag_class)
        if caption:
            tag_text = tag.get_text(strip=True) if tag else default_label
            caption_text = caption.get_text(strip=True)
            if tag_text and caption_text.startswith(tag_text):
                caption_text = caption_text[len(tag_text):].strip()
            return f"[{tag_text} {caption_text}]"
        return f"[{default_label}]"

    def _extract_text(self, el: Tag, skip_title: bool = False) -> str:
        """HTML 요소에서 텍스트 추출 (수식은 LaTeX, 그림/표는 캡션 플레이스홀더)"""
        el = self._clone_tag(el)

        if skip_title:
            for t in el.find_all(class_=re.compile(r"ltx_title")):
                t.decompose()

        for math_el in el.find_all("math", class_="ltx_Math"):
            annotation = math_el.find("annotation", attrs={"encoding": "application/x-tex"})
            if annotation:
                latex = annotation.get_text()
                display = math_el.get("display", "inline")
                replacement = f"$${latex}$$" if display == "block" else f"${latex}$"
                math_el.replace_with(replacement)
            else:
                math_el.replace_with(math_el.get_text())

        for fig in el.find_all("figure", class_="ltx_figure"):
            caption = fig.find("figcaption")
            tag = fig.find("span", class_="ltx_tag_figure")
            if caption:
                tag_text = tag.get_text(strip=True) if tag else "Figure"
                caption_text = caption.get_text(strip=True)
                if tag_text and caption_text.startswith(tag_text):
                    caption_text = caption_text[len(tag_text):].strip()
                fig.replace_with(f"[{tag_text}: {caption_text}]")
            else:
                fig.replace_with("[Figure]")

        for tbl in el.find_all("figure", class_="ltx_table"):
            caption = tbl.find("figcaption")
            tag = tbl.find("span", class_="ltx_tag_table")
            if caption:
                tag_text = tag.get_text(strip=True) if tag else "Table"
                caption_text = caption.get_text(strip=True)
                if tag_text and caption_text.startswith(tag_text):
                    caption_text = caption_text[len(tag_text):].strip()
                tbl.replace_with(f"[{tag_text}: {caption_text}]")
            else:
                tbl.replace_with("[Table]")

        for note in el.find_all("span", class_="ltx_note"):
            mark = note.find("sup", class_="ltx_note_mark")
            if mark:
                mark.decompose()
            content = note.get_text(strip=True)
            note.replace_with(f" ({content})")

        text = el.get_text()
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _extract_bibliography(self, bib_el: Tag) -> str:
        items = bib_el.find_all("li", class_="ltx_bibitem")
        refs: list[str] = []
        for item in items:
            tag = item.find("span", class_="ltx_tag")
            tag_text = tag.get_text(strip=True) if tag else ""
            bib_block = item.find("span", class_="ltx_bibblock")
            bib_text = bib_block.get_text(strip=True) if bib_block else item.get_text(strip=True)
            refs.append(f"{tag_text} {bib_text}" if tag_text else bib_text)
        return "\n".join(refs)

    @staticmethod
    def _clone_tag(el: Tag) -> Tag:
        """원본 트리를 변경하지 않도록 deep copy"""
        from copy import deepcopy
        return deepcopy(el)

    async def get_sections(self, arxiv_id: str) -> Optional[list[dict]]:
        parsed = await self._get_parsed(arxiv_id)
        if not parsed:
            return None

        return [
            {
                "id": s.id,
                "title": s.title,
                "level": s.level,
            }
            for s in parsed["sections"]
        ]

    async def get_section_content(
        self, arxiv_id: str, section_id: str
    ) -> Optional[dict]:
        parsed = await self._get_parsed(arxiv_id)
        if not parsed:
            return None

        for s in parsed["sections"]:
            if s.id == section_id:
                return {
                    "id": s.id,
                    "title": s.title,
                    "level": s.level,
                    "content": s.content,
                }
        return None

    async def get_document_title(self, arxiv_id: str) -> Optional[str]:
        parsed = await self._get_parsed(arxiv_id)
        if not parsed:
            return None
        return parsed["title"]

    def get_available_section_ids(self, arxiv_id: str) -> list[str]:
        if arxiv_id not in self._cache:
            return []
        return [s.id for s in self._cache[arxiv_id]["sections"]]
