"""arXiv API 클라이언트"""

import arxiv
from typing import Optional
from ..models.paper import Paper


class ArxivClient:
    """arXiv API 클라이언트"""

    def __init__(self):
        self.client = arxiv.Client()

    async def search(
        self,
        query: str,
        max_results: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        categories: Optional[list[str]] = None,
    ) -> list[Paper]:
        """
        arXiv에서 논문 검색

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            categories: arXiv 카테고리 (e.g., ["cs.AI", "cs.LG"])

        Returns:
            Paper 객체 리스트
        """
        # 쿼리 구성
        search_query = query

        # 카테고리 필터 추가
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({query}) AND ({cat_query})"

        # 검색 실행
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers = []
        for result in self.client.results(search):
            # 날짜 필터 (arXiv API는 날짜 필터를 지원하지 않으므로 후처리)
            published_year = result.published.year
            if date_from and published_year < int(date_from[:4]):
                continue
            if date_to and published_year > int(date_to[:4]):
                continue

            paper = self._convert_to_paper(result)
            papers.append(paper)

        return papers

    def _convert_to_paper(self, result: arxiv.Result) -> Paper:
        """arXiv Result를 Paper 객체로 변환"""
        # arXiv ID 추출 (URL에서)
        arxiv_id = result.entry_id.split("/")[-1]

        # 저자 리스트
        authors = [author.name for author in result.authors]

        return Paper(
            id=f"arxiv:{arxiv_id}",
            title=result.title,
            authors=authors,
            year=result.published.year,
            source="arxiv",
            abstract=result.summary,
            arxiv_id=arxiv_id,
            doi=result.doi,
            url=result.entry_id,
            pdf_url=result.pdf_url,
            venue=result.journal_ref,
        )

    async def get_paper(self, arxiv_id: str) -> Optional[Paper]:
        """
        arXiv ID로 특정 논문 조회

        Args:
            arxiv_id: arXiv ID (e.g., "2210.03629")

        Returns:
            Paper 객체 또는 None
        """
        search = arxiv.Search(id_list=[arxiv_id])

        try:
            result = next(self.client.results(search))
            return self._convert_to_paper(result)
        except StopIteration:
            return None
