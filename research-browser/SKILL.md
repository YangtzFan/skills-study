---
name: research-browser
description: Route every repository request to the appropriate reasoning, web-research, local-document, or image-analysis skills and enforce the shared artifact policy. Use as the mandatory entry point referenced by AGENTS.md.
---

# Research Browser

## Entry Point

This is the mandatory router for every request in this repository.

1. Read and apply `skills-study/critical-reasoning/SKILL.md` before evaluating the request.
2. Classify the request into exactly one case below.
3. Read only the additional skill files required by that case.
4. Preserve the user's scope and do not perform research or create artifacts when the task does not require them.

Use `web-search` and `web-reader` for external sources, use `document-ingest` and `document-qa` for local documents, and use `image-analysis` for image evidence that needs OCR or an external vision model.

## Inputs

- `user_query`: The user's research question.
- `attachments`: Any local file paths supplied by the user.
- `workspace`: The current working directory.

## Work Directory Contract

- Use `skills-study/work-dir/<task-id>/` as the only persistent location for downloaded evidence, extracted evidence, research notes, and intermediate artifacts created by these skills.
- Derive `<task-id>` from the date and a short task slug, and reuse the same directory throughout one task.
- Persist every artifact in this directory as a UTF-8 Markdown file with a `.md` extension. Structured data may appear inside Markdown tables, YAML frontmatter, or fenced code blocks.
- Do not persist JSON, JSONL, HTML, XML, CSV, database, image, PDF, or other non-Markdown files in `skills-study/work-dir/`.
- Keep user-provided source files at their original locations and treat them as read-only.
- When a tool requires a binary or non-Markdown download, use an operating-system temporary directory, extract the required content, write the durable evidence as Markdown under `skills-study/work-dir/<task-id>/`, and remove the temporary file after successful conversion.
- Create artifacts only when they are needed for the task. Do not create placeholder task directories or empty files.
- Record each created artifact in `skills-study/work-dir/<task-id>/index.md` with its purpose, source, and relative path.

## Classification

Choose exactly one case before beginning the research workflow.

### Case 1: External Information

Use this case when the request concerns current or recent information, news, market data, statistics, prices, official documentation, repositories, changelogs, academic literature, or an explicit web search.

1. Read and apply `skills-study/web-search/SKILL.md` with the query and relevant filters.
2. Select the most relevant and authoritative results, usually three to five URLs.
3. Read and apply `skills-study/web-reader/SKILL.md` to the selected URLs.
4. Cross-check consequential claims with an independent source when practical. If only one authoritative primary source exists, identify that limitation.
5. Answer with inline links and a `Sources` section.

If search fails, retry once with a meaningfully revised query. If the retry also fails, report the failure and request a URL or use an available browser automation capability when appropriate.

### Case 2: Local Documents

Use this case when the request references an attachment, a local file path, or facts that exist only in a supplied document.

1. Read and apply `skills-study/document-ingest/SKILL.md` to each attachment that has not already been ingested or whose contents have changed.
2. For a standalone image or a document page whose visual content matters, read and apply `skills-study/image-analysis/SKILL.md` in addition to text extraction.
3. Read and apply `skills-study/document-qa/SKILL.md` to the relevant `doc_id` values.
4. Cite each material claim with the most precise available document or image provenance and a short verbatim quote when the source contains text.

If a supplied path is unreadable, report the exact error and do not guess the file's contents.

### Case 3: External and Local Sources

Use this case when the request compares a local document with current work, asks whether a document remains accurate, or otherwise requires both local and external evidence.

1. Complete the local-document workflow first to establish what the document actually says.
2. Complete the external-information workflow next to obtain current evidence.
3. Organize the answer under `From the Document`, `From the Web`, and `Synthesis`.
4. Identify agreements, contradictions, evidence gaps, and relevant differences in publication date or authority.
5. Do not assume that the newer source is more accurate solely because it is newer.

### Case 4: No Research Required

If the request needs neither external information nor local-document evidence, answer directly without invoking the research skills.

## Output Requirements

- Clearly separate sourced facts from inference or synthesis.
- Cite local evidence with `doc_id` and page, section, sheet, or slide provenance.
- Identify whether image-derived evidence came from OCR, a relay model, or a synthesis of both.
- If an attempted relay request fails, report the failure explicitly even when local OCR succeeds. Do not hide the failure behind an OCR-only result.
- Cite web evidence with descriptive Markdown links to the source URLs.
- Include a concise `Sources` section for external research.
- State important coverage limitations, unresolved conflicts, and information that could not be verified.
- Never fabricate source content, citations, publication dates, or document locations.
