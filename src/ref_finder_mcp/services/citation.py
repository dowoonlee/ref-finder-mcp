"""Citation 생성 서비스"""

from typing import Literal
from ..models.paper import Paper


CitationFormat = Literal["bibtex", "apa", "mla", "chicago"]


class CitationGenerator:
    """Citation 포맷 생성기"""

    def generate(self, paper: Paper, format: CitationFormat = "bibtex") -> str:
        """
        논문의 citation을 지정된 포맷으로 생성

        Args:
            paper: Paper 객체
            format: citation 포맷

        Returns:
            포맷된 citation 문자열
        """
        if format == "bibtex":
            return paper.to_bibtex()
        elif format == "apa":
            return paper.to_apa()
        elif format == "mla":
            return self._to_mla(paper)
        elif format == "chicago":
            return self._to_chicago(paper)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_mla(self, paper: Paper) -> str:
        """MLA 포맷으로 변환 (Phase 3에서 구현)"""
        # TODO: MLA 포맷 구현
        return f"[MLA format not yet implemented for: {paper.title}]"

    def _to_chicago(self, paper: Paper) -> str:
        """Chicago 포맷으로 변환 (Phase 3에서 구현)"""
        # TODO: Chicago 포맷 구현
        return f"[Chicago format not yet implemented for: {paper.title}]"
