"""ReAct 논문 직접 조회 (arXiv ID 사용)"""

import asyncio
from src.mcp_textref.server import get_paper_details, generate_citation, save_paper, export_bibliography


async def test_react_direct():
    """ReAct 논문 (arXiv:2210.03629) 직접 조회"""

    print("=" * 80)
    print("검증 기준 테스트: ReAct 논문 찾아서 BibTeX 만들기")
    print("=" * 80)
    print()

    # ReAct 논문의 실제 arXiv ID
    paper_id = "arxiv:2210.03629"

    print(f"📄 논문 조회 중: {paper_id}")
    print()

    # 1. 상세 정보 조회
    details = await get_paper_details(paper_id)

    if "error" not in details:
        print("✅ 논문 발견!")
        print(f"   제목: {details['title']}")
        print(f"   저자: {', '.join(details['authors'])}")
        print(f"   연도: {details['year']}")
        print(f"   arXiv ID: {details['arxiv_id']}")
        print()
        print(f"   초록: {details['abstract'][:200]}...")
        print()

        # 2. BibTeX 생성
        print("📝 BibTeX 생성 중...")
        citation_result = await generate_citation(paper_id, format="bibtex")
        print()
        print("생성된 BibTeX:")
        print("=" * 80)
        print(citation_result["citation"])
        print("=" * 80)
        print()

        # 3. APA 포맷도 생성
        print("📝 APA 포맷 생성 중...")
        apa_result = await generate_citation(paper_id, format="apa")
        print()
        print("생성된 APA:")
        print("=" * 80)
        print(apa_result["citation"])
        print("=" * 80)
        print()

        # 4. 논문 저장
        print("💾 논문 저장 중...")
        save_result = await save_paper(paper_id)
        print(f"✅ 저장 완료: {save_result['total_saved']}개 논문")
        print()

        # 5. Export
        print("📤 Bibliography export 중...")
        bib_result = await export_bibliography(format="bibtex")
        print()
        print("최종 BibTeX 파일:")
        print("=" * 80)
        print(bib_result["bibliography"])
        print("=" * 80)
        print()

        print("🎉 검증 완료: ReAct 논문 찾아서 BibTeX 만들기 성공!")

    else:
        print(f"❌ 오류: {details['error']}")


if __name__ == "__main__":
    asyncio.run(test_react_direct())
