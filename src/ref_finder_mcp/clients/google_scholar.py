"""Google Scholar API 클라이언트"""

import asyncio
from typing import Optional
from scholarly import scholarly, ProxyGenerator
from ..models.paper import Paper


class GoogleScholarClient:
    """Google Scholar 클라이언트"""

    def __init__(self, use_proxy: bool = False):
        """
        Args:
            use_proxy: 프록시 사용 여부 (rate limit 회피용)
        """
        self.use_proxy = use_proxy
        if use_proxy:
            pg = ProxyGenerator()
            pg.FreeProxies()
            scholarly.use_proxy(pg)

    async def search(
        self,
        query: str,
        max_results: int = 10,
        year_low: Optional[int] = None,
        year_high: Optional[int] = None,
        author: Optional[str] = None,
    ) -> list[Paper]:
        """
        Google Scholar에서 논문 검색

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            year_low: 시작 연도
            year_high: 종료 연도
            author: 저자 이름 필터

        Returns:
            Paper 객체 리스트
        """
        # scholarly는 동기 라이브러리이므로 executor에서 실행
        loop = asyncio.get_event_loop()
        papers = await loop.run_in_executor(
            None,
            self._search_sync,
            query,
            max_results,
            year_low,
            year_high,
            author,
        )
        return papers

    def _search_sync(
        self,
        query: str,
        max_results: int,
        year_low: Optional[int],
        year_high: Optional[int],
        author: Optional[str],
    ) -> list[Paper]:
        """동기 검색 (executor에서 실행)"""
        papers = []

        # 검색 실행
        search_query = scholarly.search_pubs(query)

        count = 0
        for pub in search_query:
            if count >= max_results:
                break

            # 연도 필터
            pub_year = pub.get("bib", {}).get("pub_year")
            if pub_year:
                try:
                    pub_year_int = int(pub_year)
                    if year_low and pub_year_int < year_low:
                        continue
                    if year_high and pub_year_int > year_high:
                        continue
                except (ValueError, TypeError):
                    pass

            # 저자 필터
            if author:
                pub_authors = pub.get("bib", {}).get("author", [])
                author_match = any(
                    author.lower() in pub_author.lower() for pub_author in pub_authors
                )
                if not author_match:
                    continue

            paper = self._convert_to_paper(pub)
            if paper:
                papers.append(paper)
                count += 1

        return papers

    def _convert_to_paper(self, pub: dict) -> Optional[Paper]:
        """Google Scholar 결과를 Paper 객체로 변환"""
        try:
            bib = pub.get("bib", {})

            # 필수 필드 확인
            title = bib.get("title")
            if not title:
                return None

            # ID 생성 (Google Scholar에는 고유 ID가 없으므로 title 기반)
            pub_id = pub.get("pub_id") or pub.get("scholar_id") or title[:50]
            paper_id = f"scholar:{pub_id}"

            # 저자 리스트
            authors = bib.get("author", [])
            if isinstance(authors, str):
                authors = [authors]

            # 연도
            year_str = bib.get("pub_year", "")
            try:
                year = int(year_str) if year_str else 0
            except (ValueError, TypeError):
                year = 0

            # Abstract
            abstract = bib.get("abstract")

            # URL
            pub_url = pub.get("pub_url") or pub.get("eprint_url")

            # Citation count
            citation_count = pub.get("num_citations")

            # Venue
            venue = bib.get("venue") or bib.get("journal") or bib.get("conference")

            return Paper(
                id=paper_id,
                title=title,
                authors=authors,
                year=year,
                source="google_scholar",
                abstract=abstract,
                url=pub_url,
                citation_count=citation_count,
                venue=venue,
            )
        except Exception as e:
            # 변환 실패 시 None 반환
            return None

    async def get_author_info(self, author_name: str) -> Optional[dict]:
        """
        저자 정보 조회

        Args:
            author_name: 저자 이름

        Returns:
            저자 정보 딕셔너리
        """
        loop = asyncio.get_event_loop()
        author_info = await loop.run_in_executor(
            None, self._get_author_info_sync, author_name
        )
        return author_info

    def _get_author_info_sync(self, author_name: str) -> Optional[dict]:
        """동기 저자 정보 조회"""
        try:
            # 저자 검색
            search_query = scholarly.search_author(author_name)
            author = next(search_query, None)

            if not author:
                return None

            # 상세 정보 가져오기
            author_filled = scholarly.fill(author)

            # 정보 추출
            info = {
                "name": author_filled.get("name"),
                "affiliation": author_filled.get("affiliation"),
                "email": author_filled.get("email"),
                "interests": author_filled.get("interests", []),
                "citedby": author_filled.get("citedby"),
                "citedby5y": author_filled.get("citedby5y"),
                "hindex": author_filled.get("hindex"),
                "hindex5y": author_filled.get("hindex5y"),
                "i10index": author_filled.get("i10index"),
                "i10index5y": author_filled.get("i10index5y"),
                "scholar_id": author_filled.get("scholar_id"),
                "url": author_filled.get("url_picture"),
                "publications_count": len(author_filled.get("publications", [])),
            }

            # 주요 논문 (최대 5개)
            publications = author_filled.get("publications", [])[:5]
            info["top_publications"] = [
                {
                    "title": pub.get("bib", {}).get("title"),
                    "year": pub.get("bib", {}).get("pub_year"),
                    "citations": pub.get("num_citations"),
                }
                for pub in publications
            ]

            return info

        except Exception as e:
            return None
