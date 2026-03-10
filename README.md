# Academic Paper MCP Server (mcp-textref)

논문 검색부터 참조문헌 생성까지 end-to-end 자동화를 제공하는 MCP 서버

## 현재 상태: Phase 1.5

✅ **구현 완료**:
- arXiv 논문 검색
- Google Scholar 논문 검색 (NEW!)
- Google Scholar 저자 정보 조회 (NEW!)
- BibTeX/APA citation 생성
- 세션 기반 논문 관리 (메모리)
- FastMCP 3.0 기반 서버

🚧 **예정** (Phase 2):
- Semantic Scholar 통합
- Crossref 통합
- 중복 제거
- 파일 기반 세션 저장

## 설치

```bash
# uv로 의존성 설치
uv sync

# 개발 모드로 실행
uv run python -m mcp_textref.server
```

## MCP 도구

### 1. `search_papers`
멀티소스에서 논문 검색 (arXiv, Google Scholar)

```python
# arXiv에서 검색
search_papers(
    query="transformer attention",
    sources=["arxiv"],
    max_results=10,
    categories=["cs.AI", "cs.LG"]
)

# Google Scholar에서 검색
search_papers(
    query="deep learning",
    sources=["google_scholar"],
    max_results=10,
    date_from="2020-01-01",
    author="Yann LeCun"
)

# 여러 소스에서 동시 검색
search_papers(
    query="neural networks",
    sources=["arxiv", "google_scholar"],
    max_results=20
)
```

### 2. `get_paper_details`
논문 상세 정보 조회

```python
get_paper_details(paper_id="arxiv:2210.03629")
```

### 3. `generate_citation`
Citation 생성 (BibTeX/APA)

```python
generate_citation(
    paper_id="arxiv:2210.03629",
    format="bibtex"
)
```

### 4. `save_paper`
논문 저장

```python
save_paper(paper_id="arxiv:2210.03629")
```

### 5. `list_saved_papers`
저장된 논문 목록

```python
list_saved_papers()
```

### 6. `remove_paper`
논문 삭제

```python
remove_paper(paper_id="arxiv:2210.03629")
```

### 7. `export_bibliography`
참조문헌 일괄 export

```python
export_bibliography(format="bibtex")
```

### 8. `get_author_info`
Google Scholar에서 저자 정보 조회

```python
get_author_info(author_name="Geoffrey Hinton")
```

반환 정보:
- 소속 기관
- 총 인용 수
- h-index, i10-index
- 연구 분야
- 주요 논문 (상위 5개)

## Claude Code 연동

```json
// .claude/mcp.json (project-scope)
{
  "mcpServers": {
    "academic": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "--directory",
        "/Users/a11706/mcp_library/mcp-textref",
        "python",
        "-m",
        "mcp_textref.server"
      ]
    }
  }
}
```

## 사용 예시

### 예시 1: arXiv에서 논문 검색
```
[사용자] "ReAct 논문 찾아서 BibTeX 만들어줘"

[Claude] (search_papers 실행)
         "ReAct 논문을 찾았습니다: Yao et al., 2022"

         (generate_citation 실행)
         "@article{yao2022react,
           title={ReAct: Synergizing Reasoning and Acting...},
           author={Yao, Shunyu and Zhao, Jeffrey and ...},
           year={2022},
           ...
         }"
```

### 예시 2: Google Scholar에서 저자 정보 조회
```
[사용자] "Geoffrey Hinton의 h-index와 주요 논문 알려줘"

[Claude] (get_author_info 실행)
         "Geoffrey Hinton:
          - 소속: University of Toronto
          - h-index: 176
          - 총 인용 수: 500,000+
          - 주요 논문:
            1. ImageNet Classification with Deep CNNs (2012)
            2. Deep Learning (2015)
            ..."
```

### 예시 3: 멀티소스 검색
```
[사용자] "transformer 관련 최신 논문 arXiv랑 Google Scholar에서 찾아줘"

[Claude] (search_papers 실행)
         "arXiv와 Google Scholar에서 총 20개의 논문을 찾았습니다:

          [arXiv]
          1. Attention Is All You Need (2017)
          ...

          [Google Scholar]
          1. BERT: Pre-training of Deep Bidirectional Transformers (2019)
          ..."
```

## 개발

```bash
# Hot reload 개발 서버
fastmcp dev src/mcp_textref/server.py

# 테스트 실행
uv run pytest

# 코드 포맷팅
uv run ruff check --fix
```

## 라이선스

MIT
