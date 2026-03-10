"""Academic Paper MCP Server - FastMCP 3.0"""

from fastmcp import FastMCP
from typing import Optional
import sys

from .clients.arxiv import ArxivClient
from .clients.google_scholar import GoogleScholarClient
from .services.citation import CitationGenerator

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("academic-paper-server")

# 클라이언트 및 서비스 초기화
arxiv_client = ArxivClient()
google_scholar_client = GoogleScholarClient()
citation_gen = CitationGenerator()

# 세션 스토리지 (메모리 기반 - Phase 2에서 파일 기반으로 전환)
saved_papers = {}


@mcp.tool(
    annotations={
        "readOnly": True,
        "cacheHint": "1h",  # 1시간 캐싱 힌트
    }
)
async def search_papers(
    query: str,
    sources: list[str] = ["arxiv"],
    max_results: int = 10,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    categories: Optional[list[str]] = None,
    author: Optional[str] = None,
) -> dict:
    """
    멀티소스에서 논문을 검색합니다.

    Args:
        query: 검색 키워드 (예: "transformer attention mechanism")
        sources: 검색할 소스 리스트 (지원: ["arxiv", "google_scholar"])
        max_results: 최대 결과 수 (기본: 10)
        date_from: 시작 날짜 (YYYY-MM-DD)
        date_to: 종료 날짜 (YYYY-MM-DD)
        categories: arXiv 카테고리 (예: ["cs.AI", "cs.LG"])
        author: 저자 이름 필터 (Google Scholar용)

    Returns:
        검색 결과 (papers 리스트, 메타데이터 포함)
    """
    sys.stderr.write(f"Searching papers: query='{query}', sources={sources}\n")

    papers = []

    # arXiv 검색
    if "arxiv" in sources:
        arxiv_papers = await arxiv_client.search(
            query=query,
            max_results=max_results,
            date_from=date_from,
            date_to=date_to,
            categories=categories,
        )
        papers.extend(arxiv_papers)

    # Google Scholar 검색
    if "google_scholar" in sources:
        year_low = int(date_from[:4]) if date_from else None
        year_high = int(date_to[:4]) if date_to else None

        scholar_papers = await google_scholar_client.search(
            query=query,
            max_results=max_results,
            year_low=year_low,
            year_high=year_high,
            author=author,
        )
        papers.extend(scholar_papers)

    # Paper 객체를 딕셔너리로 변환
    papers_dict = [paper.to_dict() for paper in papers]

    return {
        "papers": papers_dict,
        "total": len(papers_dict),
        "sources_queried": sources,
        "query": query,
    }


@mcp.tool(annotations={"readOnly": True})
async def get_paper_details(paper_id: str) -> dict:
    """
    논문의 상세 정보를 조회합니다.

    Args:
        paper_id: 논문 ID (예: "arxiv:2210.03629")

    Returns:
        논문 상세 정보
    """
    sys.stderr.write(f"Getting paper details: {paper_id}\n")

    # ID 타입 파싱
    if paper_id.startswith("arxiv:"):
        arxiv_id = paper_id.replace("arxiv:", "")
        paper = await arxiv_client.get_paper(arxiv_id)

        if paper:
            return paper.to_dict()
        else:
            return {"error": f"Paper not found: {paper_id}"}
    else:
        return {"error": f"Unsupported paper ID format: {paper_id}"}


@mcp.tool(annotations={"readOnly": True})
async def generate_citation(
    paper_id: str, format: str = "bibtex"
) -> dict:
    """
    논문의 citation을 생성합니다.

    Args:
        paper_id: 논문 ID (예: "arxiv:2210.03629")
        format: citation 포맷 ("bibtex", "apa", "mla", "chicago")

    Returns:
        생성된 citation
    """
    sys.stderr.write(f"Generating citation: {paper_id}, format={format}\n")

    # 논문 정보 조회
    paper_data = await get_paper_details(paper_id)

    if "error" in paper_data:
        return paper_data

    # Paper 객체로 변환
    from .models.paper import Paper

    paper = Paper.from_dict(paper_data)

    # Citation 생성
    try:
        citation = citation_gen.generate(paper, format)
        return {"paper_id": paper_id, "format": format, "citation": citation}
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool(annotations={"readOnly": False})
async def save_paper(paper_id: str) -> dict:
    """
    논문을 세션에 저장합니다.

    Args:
        paper_id: 논문 ID (예: "arxiv:2210.03629")

    Returns:
        저장 결과
    """
    sys.stderr.write(f"Saving paper: {paper_id}\n")

    # 논문 정보 조회
    paper_data = await get_paper_details(paper_id)

    if "error" in paper_data:
        return paper_data

    # 메모리에 저장
    saved_papers[paper_id] = paper_data

    return {
        "status": "success",
        "paper_id": paper_id,
        "title": paper_data["title"],
        "total_saved": len(saved_papers),
    }


@mcp.tool(annotations={"readOnly": True})
async def list_saved_papers() -> dict:
    """
    저장된 논문 목록을 조회합니다.

    Returns:
        저장된 논문 목록 (간단 정보)
    """
    sys.stderr.write("Listing saved papers\n")

    papers_list = []
    for paper_id, paper_data in saved_papers.items():
        papers_list.append(
            {
                "id": paper_id,
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "year": paper_data["year"],
            }
        )

    return {"papers": papers_list, "total": len(papers_list)}


@mcp.tool(annotations={"readOnly": False, "destructive": True})
async def remove_paper(paper_id: str) -> dict:
    """
    저장된 논문을 삭제합니다.

    Args:
        paper_id: 논문 ID

    Returns:
        삭제 결과
    """
    sys.stderr.write(f"Removing paper: {paper_id}\n")

    if paper_id in saved_papers:
        del saved_papers[paper_id]
        return {
            "status": "success",
            "paper_id": paper_id,
            "total_saved": len(saved_papers),
        }
    else:
        return {"error": f"Paper not found in saved list: {paper_id}"}


@mcp.tool(annotations={"readOnly": True})
async def export_bibliography(format: str = "bibtex") -> dict:
    """
    저장된 모든 논문의 참조문헌을 export합니다.

    Args:
        format: citation 포맷 ("bibtex", "apa", "markdown")

    Returns:
        생성된 참조문헌
    """
    sys.stderr.write(f"Exporting bibliography: format={format}\n")

    if not saved_papers:
        return {"error": "No papers saved"}

    citations = []

    for paper_id, paper_data in saved_papers.items():
        from .models.paper import Paper

        paper = Paper.from_dict(paper_data)

        if format in ["bibtex", "apa"]:
            citation = citation_gen.generate(paper, format)
            citations.append(citation)
        elif format == "markdown":
            # Markdown 포맷
            md = f"- **{paper.title}** ({paper.year})\n"
            md += f"  - Authors: {', '.join(paper.authors)}\n"
            md += f"  - Source: {paper.source}\n"
            if paper.url:
                md += f"  - URL: {paper.url}\n"
            citations.append(md)
        else:
            return {"error": f"Unsupported format: {format}"}

    # 포맷에 따라 구분자 추가
    if format == "bibtex":
        bibliography = "\n\n".join(citations)
    elif format == "apa":
        bibliography = "\n\n".join(citations)
    elif format == "markdown":
        bibliography = "\n".join(citations)

    return {
        "format": format,
        "total_papers": len(saved_papers),
        "bibliography": bibliography,
    }


@mcp.tool(annotations={"readOnly": True})
async def get_author_info(author_name: str) -> dict:
    """
    Google Scholar에서 저자 정보를 조회합니다.

    Args:
        author_name: 저자 이름 (예: "Geoffrey Hinton")

    Returns:
        저자 정보 (소속, 인용 수, h-index, 주요 논문 등)
    """
    sys.stderr.write(f"Getting author info: {author_name}\n")

    author_info = await google_scholar_client.get_author_info(author_name)

    if author_info:
        return {
            "status": "success",
            "author": author_info,
        }
    else:
        return {"error": f"Author not found: {author_name}"}


if __name__ == "__main__":
    # FastMCP 서버 실행
    mcp.run()
