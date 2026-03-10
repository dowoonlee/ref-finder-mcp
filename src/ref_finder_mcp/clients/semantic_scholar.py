"""Semantic Scholar API 클라이언트"""

from typing import Optional
from semanticscholar import AsyncSemanticScholar
from ..models.paper import Paper


class SemanticScholarClient:
    """Semantic Scholar API 클라이언트 (비동기)"""

    FIELDS = [
        "title",
        "authors",
        "year",
        "abstract",
        "externalIds",
        "url",
        "citationCount",
        "venue",
        "openAccessPdf",
        "publicationDate",
        "fieldsOfStudy",
        "tldr",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncSemanticScholar(api_key=api_key) if api_key else AsyncSemanticScholar()

    async def search(
        self,
        query: str,
        max_results: int = 10,
        year: Optional[str] = None,
        fields_of_study: Optional[list[str]] = None,
        min_citation_count: Optional[int] = None,
    ) -> list[Paper]:
        """
        Semantic Scholar에서 논문 검색

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            year: 연도 필터 ("2022", "2020-2023", "2020-", "-2023")
            fields_of_study: 분야 필터 (e.g., ["Computer Science"])
            min_citation_count: 최소 인용 수 필터

        Returns:
            Paper 객체 리스트
        """
        kwargs = {
            "query": query,
            "limit": max_results,
            "fields": self.FIELDS,
        }
        if year:
            kwargs["year"] = year
        if fields_of_study:
            kwargs["fields_of_study"] = fields_of_study
        if min_citation_count is not None:
            kwargs["min_citation_count"] = min_citation_count

        results = await self.client.search_paper(**kwargs)

        papers = []
        for item in results.items[:max_results]:
            paper = self._convert_to_paper(item)
            if paper:
                papers.append(paper)

        return papers

    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        """
        논문 ID로 상세 정보 조회

        지원 ID 형식: Semantic Scholar paperId, CorpusId, DOI, arXiv ID, URL 등
        예: "649def34f8be52c8b66281af98ae884c09aef38b", "CorpusId:215416146",
            "10.1093/mind/lix.236.433", "arXiv:2210.03629"

        Args:
            paper_id: 논문 식별자

        Returns:
            Paper 객체 또는 None
        """
        try:
            result = await self.client.get_paper(paper_id, fields=self.FIELDS)
            return self._convert_to_paper(result)
        except Exception:
            return None

    async def get_author(self, author_id: str) -> Optional[dict]:
        """
        저자 정보 조회

        Args:
            author_id: Semantic Scholar 저자 ID

        Returns:
            저자 정보 딕셔너리
        """
        try:
            author = await self.client.get_author(
                author_id,
                fields=["name", "affiliations", "citationCount", "hIndex", "paperCount", "papers"],
            )
            papers = []
            for p in (author.papers or [])[:5]:
                papers.append({
                    "title": p.get("title"),
                    "year": p.get("year"),
                    "citations": p.get("citationCount"),
                })

            return {
                "name": author.name,
                "affiliations": author.affiliations,
                "citationCount": author.citationCount,
                "hIndex": author.hIndex,
                "paperCount": author.paperCount,
                "top_publications": papers,
            }
        except Exception:
            return None

    async def get_recommended_papers(self, paper_id: str, max_results: int = 5) -> list[Paper]:
        """
        특정 논문 기반 추천 논문 조회

        Args:
            paper_id: 기준 논문 ID
            max_results: 최대 결과 수

        Returns:
            추천 Paper 리스트
        """
        try:
            results = await self.client.get_recommended_papers(
                paper_id, limit=max_results, fields=self.FIELDS
            )
            papers = []
            for item in results[:max_results]:
                paper = self._convert_to_paper(item)
                if paper:
                    papers.append(paper)
            return papers
        except Exception:
            return []

    def _convert_to_paper(self, result) -> Optional[Paper]:
        """Semantic Scholar 결과를 Paper 객체로 변환"""
        try:
            title = result.title
            if not title:
                return None

            authors = [a.get("name", "") for a in (result.authors or [])] if result.authors else []

            external_ids = result.externalIds or {}
            arxiv_id = external_ids.get("ArXiv")
            doi = external_ids.get("DOI")
            corpus_id = external_ids.get("CorpusId")

            paper_id = f"s2:{result.paperId}" if result.paperId else f"s2:corpus:{corpus_id}"

            pdf_url = None
            if result.openAccessPdf:
                pdf_url = result.openAccessPdf.get("url")

            return Paper(
                id=paper_id,
                title=title,
                authors=authors,
                year=result.year or 0,
                source="semantic_scholar",
                abstract=result.abstract,
                doi=doi,
                arxiv_id=arxiv_id,
                url=result.url,
                citation_count=result.citationCount,
                venue=result.venue or None,
                pdf_url=pdf_url,
            )
        except Exception:
            return None
