"""멀티소스 논문 중복 제거"""

import re
import unicodedata
from ..models.paper import Paper


def _normalize_title(title: str) -> str:
    """비교용 제목 정규화: 소문자, 특수문자/공백 제거, 유니코드 정규화"""
    title = unicodedata.normalize("NFKD", title)
    title = title.lower()
    title = re.sub(r"[^a-z0-9]", "", title)
    return title


def _merge_papers(existing: Paper, incoming: Paper) -> Paper:
    """두 Paper 객체를 병합. 기존 객체에 빈 필드가 있으면 incoming에서 채움."""
    optional_fields = [
        "abstract", "doi", "arxiv_id", "url", "citation_count", "venue", "pdf_url",
    ]
    for field in optional_fields:
        existing_val = getattr(existing, field)
        incoming_val = getattr(incoming, field)
        if existing_val is None and incoming_val is not None:
            setattr(existing, field, incoming_val)

    if existing.year == 0 and incoming.year != 0:
        existing.year = incoming.year

    return existing


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """
    여러 소스에서 수집된 논문 리스트에서 중복을 제거합니다.

    매칭 우선순위:
    1. arXiv ID 일치
    2. DOI 일치
    3. 정규화된 제목 일치 (+ 연도 동일)

    중복 발견 시 두 Paper의 메타데이터를 병합하여 더 풍부한 결과를 반환합니다.
    """
    unique: list[Paper] = []
    seen_arxiv: dict[str, int] = {}
    seen_doi: dict[str, int] = {}
    seen_title: dict[str, int] = {}

    for paper in papers:
        merged = False

        if paper.arxiv_id:
            key = paper.arxiv_id.strip()
            if key in seen_arxiv:
                _merge_papers(unique[seen_arxiv[key]], paper)
                merged = True

        if not merged and paper.doi:
            key = paper.doi.strip().lower()
            if key in seen_doi:
                _merge_papers(unique[seen_doi[key]], paper)
                merged = True

        if not merged:
            norm_title = _normalize_title(paper.title)
            title_key = f"{norm_title}:{paper.year}" if paper.year else norm_title
            if title_key in seen_title:
                _merge_papers(unique[seen_title[title_key]], paper)
                merged = True

        if not merged:
            idx = len(unique)
            unique.append(paper)

            if paper.arxiv_id:
                seen_arxiv[paper.arxiv_id.strip()] = idx
            if paper.doi:
                seen_doi[paper.doi.strip().lower()] = idx
            norm_title = _normalize_title(paper.title)
            title_key = f"{norm_title}:{paper.year}" if paper.year else norm_title
            seen_title[title_key] = idx

    return unique
