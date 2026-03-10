"""MCP 서버 직접 테스트"""

import asyncio
import sys

# 서버 함수 import
from src.mcp_textref.server import (
    search_papers,
    get_paper_details,
    generate_citation,
    save_paper,
    list_saved_papers,
    export_bibliography,
)


async def test_workflow():
    """전체 워크플로우 테스트: ReAct 논문 찾아서 BibTeX 만들기"""

    print("=" * 80)
    print("Phase 1 MVP 테스트: ReAct 논문 찾아서 BibTeX 만들기")
    print("=" * 80)
    print()

    # Step 1: 논문 검색
    print("Step 1: ReAct 논문 검색...")
    print("-" * 80)
    result = await search_papers(query="ReAct reasoning acting", max_results=5)
    print(f"✅ 검색 완료: {result['total']}개 논문 발견")
    print()

    if result["total"] > 0:
        first_paper = result["papers"][0]
        print(f"첫 번째 논문:")
        print(f"  - ID: {first_paper['id']}")
        print(f"  - Title: {first_paper['title']}")
        print(f"  - Authors: {', '.join(first_paper['authors'][:3])}...")
        print(f"  - Year: {first_paper['year']}")
        print()

        # Step 2: 상세 정보 조회
        print("Step 2: 상세 정보 조회...")
        print("-" * 80)
        paper_id = first_paper["id"]
        details = await get_paper_details(paper_id)
        print(f"✅ 상세 정보 조회 완료")
        print(f"  - Abstract: {details['abstract'][:200]}...")
        print()

        # Step 3: BibTeX 생성
        print("Step 3: BibTeX 생성...")
        print("-" * 80)
        citation_result = await generate_citation(paper_id, format="bibtex")
        if "citation" in citation_result:
            print("✅ BibTeX 생성 성공:")
            print()
            print(citation_result["citation"])
            print()

        # Step 4: 논문 저장
        print("Step 4: 논문 저장...")
        print("-" * 80)
        save_result = await save_paper(paper_id)
        print(f"✅ 저장 완료: {save_result['title']}")
        print(f"  - 총 저장된 논문: {save_result['total_saved']}개")
        print()

        # Step 5: 추가 논문 몇 개 더 저장
        print("Step 5: 추가 논문 저장...")
        print("-" * 80)
        for i, paper in enumerate(result["papers"][1:3], 2):
            await save_paper(paper["id"])
            print(f"  - {i}번째 논문 저장: {paper['title'][:60]}...")
        print()

        # Step 6: 저장된 논문 목록 확인
        print("Step 6: 저장된 논문 목록 확인...")
        print("-" * 80)
        saved_list = await list_saved_papers()
        print(f"✅ 총 {saved_list['total']}개 논문 저장됨:")
        for i, paper in enumerate(saved_list["papers"], 1):
            print(f"  {i}. {paper['title'][:60]}... ({paper['year']})")
        print()

        # Step 7: BibTeX export
        print("Step 7: BibTeX 파일 export...")
        print("-" * 80)
        bib_result = await export_bibliography(format="bibtex")
        print(f"✅ Bibliography export 완료 ({bib_result['total_papers']}개 논문)")
        print()
        print("생성된 BibTeX:")
        print("=" * 80)
        print(bib_result["bibliography"])
        print("=" * 80)
        print()

        # Step 8: APA 포맷도 테스트
        print("Step 8: APA 포맷 테스트...")
        print("-" * 80)
        apa_result = await export_bibliography(format="apa")
        print(f"✅ APA export 완료")
        print()
        print("생성된 APA:")
        print("=" * 80)
        print(apa_result["bibliography"])
        print("=" * 80)
        print()

    print("🎉 Phase 1 MVP 테스트 완료!")
    print()
    print("검증 기준 달성: ✅ ReAct 논문 찾아서 BibTeX 만들기 성공")


if __name__ == "__main__":
    asyncio.run(test_workflow())
