"""논문 데이터 모델"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Paper:
    """표준화된 논문 데이터 모델"""

    # 필수 필드
    id: str  # "arxiv:2210.03629" | "doi:10.1234/..."
    title: str
    authors: list[str]
    year: int
    source: str  # "arxiv" | "semantic_scholar" | "crossref"

    # 선택 필드
    abstract: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    citation_count: Optional[int] = None
    venue: Optional[str] = None  # 저널/컨퍼런스
    pdf_url: Optional[str] = None

    # 메타데이터
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_bibtex(self) -> str:
        """BibTeX 포맷으로 변환"""
        # 첫 번째 저자의 성 추출 (간단 버전)
        first_author_last = self.authors[0].split()[-1].lower() if self.authors else "unknown"

        # BibTeX key 생성: firstauthor{year}{title_first_word}
        title_first = self.title.split()[0].lower() if self.title else "paper"
        key = f"{first_author_last}{self.year}{title_first}"

        # 저자 포맷: "Last1, First1 and Last2, First2"
        authors_formatted = " and ".join(self.authors)

        # Entry type 결정
        if self.arxiv_id:
            entry_type = "article"
            journal = f"arXiv preprint arXiv:{self.arxiv_id}"
        elif self.venue:
            entry_type = "article"
            journal = self.venue
        else:
            entry_type = "misc"
            journal = ""

        # BibTeX 생성
        bibtex = f"@{entry_type}{{{key},\n"
        bibtex += f"  title={{{self.title}}},\n"
        bibtex += f"  author={{{authors_formatted}}},\n"
        bibtex += f"  year={{{self.year}}},\n"

        if journal:
            bibtex += f"  journal={{{journal}}},\n"

        if self.doi:
            bibtex += f"  doi={{{self.doi}}},\n"

        if self.url:
            bibtex += f"  url={{{self.url}}},\n"

        bibtex += "}"

        return bibtex

    def to_apa(self) -> str:
        """APA 포맷으로 변환"""
        # 저자 포맷
        if len(self.authors) == 1:
            authors_str = self.authors[0]
        elif len(self.authors) == 2:
            authors_str = f"{self.authors[0]} & {self.authors[1]}"
        else:
            # 3명 이상: First, Second, & Third
            authors_str = ", ".join(self.authors[:-1]) + f", & {self.authors[-1]}"

        # APA 기본 포맷
        apa = f"{authors_str} ({self.year}). {self.title}. "

        if self.venue:
            apa += f"{self.venue}. "
        elif self.arxiv_id:
            apa += f"arXiv preprint arXiv:{self.arxiv_id}. "

        if self.doi:
            apa += f"https://doi.org/{self.doi}"
        elif self.url:
            apa += self.url

        return apa

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "source": self.source,
            "abstract": self.abstract,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "url": self.url,
            "citation_count": self.citation_count,
            "venue": self.venue,
            "pdf_url": self.pdf_url,
            "fetched_at": self.fetched_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Paper":
        """딕셔너리로부터 생성"""
        # fetched_at을 datetime으로 변환
        if isinstance(data.get("fetched_at"), str):
            data["fetched_at"] = datetime.fromisoformat(data["fetched_at"])

        return cls(**data)
