# ref-finder-mcp

An MCP server for end-to-end academic paper workflow — search across arXiv, Google Scholar, and Semantic Scholar, read paper content section by section, and auto-generate BibTeX/APA citations.

## Installation

```bash
uv sync
uv run python -m ref_finder_mcp.server
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_papers` | Multi-source paper search (arXiv, Google Scholar, Semantic Scholar) |
| `get_paper_details` | Retrieve detailed paper information |
| `generate_citation` | Generate BibTeX / APA citations |
| `save_paper` | Save a paper to the session |
| `list_saved_papers` | List saved papers |
| `remove_paper` | Remove a saved paper |
| `export_bibliography` | Export all saved papers as BibTeX / APA / Markdown |
| `get_author_info` | Look up author info via Google Scholar |
| `get_recommended_papers` | Get similar paper recommendations via Semantic Scholar |
| `list_paper_sections` | List sections (table of contents) of an arXiv paper |
| `get_paper_section` | Fetch the full text of a specific section from an arXiv paper |

## Search Sources

| Source | ID prefix | Notes |
|--------|-----------|-------|
| arXiv | `arxiv:` | Preprints, category filters |
| Google Scholar | `scholar:` | Broad coverage, author search |
| Semantic Scholar | `s2:` | Official API, citation counts, recommendations |

Duplicates are automatically merged by arXiv ID / DOI / title when searching across multiple sources.

## Reading Paper Content

`list_paper_sections` and `get_paper_section` give section-level access to arXiv paper full text via [ar5iv](https://ar5iv.labs.arxiv.org). The workflow is designed to be token-efficient: fetch the table of contents first, then pull only the sections you actually need.

- Supported: all arXiv papers that have an HTML version on ar5iv
- Math formulas are preserved as LaTeX (`$...$` / `$$...$$`)
- Figures and tables are replaced with caption placeholders (`[Figure N: ...]`)
- Parsed documents are cached in-memory to avoid redundant network requests

## Usage Examples

### Search + Generate BibTeX

```
"Find the ReAct paper and generate BibTeX"

→ search_papers(query="ReAct Synergizing Reasoning Acting", sources=["arxiv"])
→ generate_citation(paper_id="arxiv:2210.03629", format="bibtex")
```

### Multi-source Search

```
"Search transformer papers on arXiv and Semantic Scholar"

→ search_papers(query="transformer", sources=["arxiv", "semantic_scholar"], max_results=20)
  (duplicates are automatically merged)
```

### Paper Recommendations

```
"Recommend papers similar to the ReAct paper"

→ get_recommended_papers(paper_id="arxiv:2210.03629", max_results=5)
```

### Author Info

```
"What's Geoffrey Hinton's h-index and top papers?"

→ get_author_info(author_name="Geoffrey Hinton")
  (returns affiliation, h-index, citation count, top publications, etc.)
```

### Reading Paper Content

```
"Summarize the Methods section of the Mixtral paper"

→ list_paper_sections(paper_id="arxiv:2401.04088")
  (returns table of contents with section IDs)
→ get_paper_section(paper_id="arxiv:2401.04088", section_id="S2")
  (returns full text of the Architectural details section)
```

## MCP Client Configuration

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

## Development

```bash
fastmcp dev src/ref_finder_mcp/server.py      # Dev server with hot reload
uv run pytest                                  # Run unit tests
uv run pytest -m integration                   # Run integration tests (network required)
uv run ruff check --fix                        # Lint
```

## License

MIT
