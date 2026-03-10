# ref-finder-mcp

논문 검색부터 참조문헌 생성까지 end-to-end 자동화를 제공하는 MCP 서버.
arXiv, Google Scholar, Semantic Scholar를 통합 검색하고, BibTeX/APA citation을 자동 생성합니다.

## 설치 및 실행

```bash
uv sync
uv run python -m ref_finder_mcp.server
```

## MCP 도구 목록

| 도구 | 설명 |
|------|------|
| `search_papers` | 멀티소스 논문 검색 (arXiv, Google Scholar, Semantic Scholar) |
| `get_paper_details` | 논문 상세 정보 조회 |
| `generate_citation` | BibTeX / APA citation 생성 |
| `save_paper` | 논문을 세션에 저장 |
| `list_saved_papers` | 저장된 논문 목록 조회 |
| `remove_paper` | 저장된 논문 삭제 |
| `export_bibliography` | 저장된 논문 전체를 BibTeX / APA / Markdown으로 export |
| `get_author_info` | Google Scholar 기반 저자 정보 조회 |
| `get_recommended_papers` | Semantic Scholar 기반 유사 논문 추천 |

## 검색 소스

| 소스 | ID prefix | 특징 |
|------|-----------|------|
| arXiv | `arxiv:` | 프리프린트 중심, 카테고리 필터 지원 |
| Google Scholar | `scholar:` | 폭넓은 커버리지, 저자 검색 |
| Semantic Scholar | `s2:` | 공식 API, citation count, 논문 추천 |

멀티소스 검색 시 arXiv ID / DOI / 제목 기반으로 자동 중복 제거됩니다.

## 사용 예시

### 논문 검색 + BibTeX 생성

```
"ReAct 논문 찾아서 BibTeX 만들어줘"

→ search_papers(query="ReAct Synergizing Reasoning Acting", sources=["arxiv"])
→ generate_citation(paper_id="arxiv:2210.03629", format="bibtex")
```

### 멀티소스 검색

```
"transformer 관련 논문 arXiv랑 Semantic Scholar에서 찾아줘"

→ search_papers(query="transformer", sources=["arxiv", "semantic_scholar"], max_results=20)
  (중복 논문은 자동 병합)
```

### 유사 논문 추천

```
"ReAct 논문이랑 비슷한 논문 추천해줘"

→ get_recommended_papers(paper_id="arxiv:2210.03629", max_results=5)
```

### 저자 정보 조회

```
"Geoffrey Hinton의 h-index와 주요 논문 알려줘"

→ get_author_info(author_name="Geoffrey Hinton")
  (소속, h-index, 인용 수, 주요 논문 등 반환)
```

## MCP 클라이언트 연동

```json
{
  "mcpServers": {
    "ref-finder": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/ref-finder-mcp",
        "python", "-m", "ref_finder_mcp.server"
      ]
    }
  }
}
```

## 개발

```bash
fastmcp dev src/ref_finder_mcp/server.py   # Hot reload 개발 서버
uv run pytest                               # 테스트
uv run ruff check --fix                     # 린트
```

## 라이선스

MIT
