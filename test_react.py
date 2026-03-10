"""ReAct 논문 정확히 찾기 테스트"""

import asyncio
from src.mcp_textref.server import search_papers, generate_citation


async def test_react_paper():
    """ReAct 논문 (Yao et al., 2022) 찾기"""

    print("🔍 ReAct 논문 검색 중...")
    print()

    # 더 구체적인 검색어
    result = await search_papers(
        query="ReAct Synergizing Reasoning Acting Language Models",
        max_results=10,
        categories=["cs.AI", "cs.CL", "cs.LG"],
    )

    print(f"총 {result['total']}개 논문 발견:")
    print()

    for i, paper in enumerate(result["papers"], 1):
        print(f"{i}. {paper['title']}")
        print(f"   저자: {', '.join(paper['authors'][:3])}")
        print(f"   연도: {paper['year']}, arXiv: {paper.get('arxiv_id', 'N/A')}")
        print()

        # ReAct 논문인지 확인
        if "ReAct" in paper["title"] and "Synergizing" in paper["title"]:
            print("✨ ReAct 논문 발견!")
            print()

            # BibTeX 생성
            citation_result = await generate_citation(paper["id"], format="bibtex")
            print("BibTeX:")
            print("=" * 80)
            print(citation_result["citation"])
            print("=" * 80)
            break


if __name__ == "__main__":
    asyncio.run(test_react_paper())
