---
name: document-qa
description: Answer questions from previously ingested local documents with precise provenance and verbatim evidence. Use when a document has a doc_id from document-ingest or when research-browser needs local-document evidence.
---

# Document Question Answering

## When to Use

- Use this skill when a relevant `doc_id` already exists from `document-ingest`.
- Use it when the user asks a factual question about an ingested document.
- Use it for the local-document phase of a combined local and external research task.
- Use it when the answer depends on a document registered in the project knowledge base at `.agents-work/knowledge/`.

## Inputs

- `doc_id`: One document identifier or a list of document identifiers. A knowledge base document is addressed by the same `doc_id` form.
- `question`: The question to answer from the documents.
- `top_k`: The optional maximum number of retrieved chunks, with a default of 8.

## Retrieval

- Read `.agents-work/knowledge/index.md` first when the question may concern project background, and include the relevant knowledge base documents alongside any documents ingested for the current task.
- For a document with no more than 30 chunks, read its `content.md` in full when the context window permits.
- For a larger document or multiple documents, retrieve approximately 20 candidate sections from `chunks.md` with keyword or BM25 search, optionally rerank them with embeddings when a configured vector store is available, and retain the best `top_k` chunks.
- Preserve `chunk_id`, page, section, sheet, or slide metadata throughout retrieval.
- Expand retrieval when the initial evidence is incomplete or conflicting.

## Answer Rules

- Base document claims only on retrieved or fully read document content.
- Support each material factual claim with a verbatim quote and the most precise available provenance.
- Use `(doc_id, p<page>)` for paginated sources and an explicit section, sheet, or slide label for non-paginated sources.
- If the evidence does not answer a question, state `Not found in <doc_id>.` for that question and do not fill the gap with outside knowledge.
- If document passages conflict, present both passages with their provenance.
- Never invent page numbers, locations, or quotations.

## Output

```markdown
## Answer
<answer with provenance>

## Evidence
- doc_id=ab12cd34ef56, p7, "exact sentence ..."
- doc_id=ab12cd34ef56, p12, "exact sentence ..."

## Not Found
- <sub-question not covered by the document>

## Coverage
- chunks_scanned=12/48, method=bm25
```

Omit the `Not Found` section when every part of the question is answered.

## Research Router Handoff

- When `research-browser` invokes this skill for a combined task, return a clearly labeled local-evidence block.
- Do not merge external sources into this block because the router performs the synthesis.
- Mark a claim with `needs_external: true` when it requires current or external verification.

## Work Directory

- Read document artifacts from `.agents-work/<task-id>/documents/<doc_id>/` for the current task, and from `.agents-work/knowledge/documents/<doc_id>/` for project background documents, unless the user explicitly provides another existing ingestion location.
- If retrieval notes, evidence selections, or draft synthesis must be persisted, write them as Markdown files under the active `.agents-work/<task-id>/` directory.
- Do not persist indexes, embeddings, JSON, or other non-Markdown intermediate files in the work directory. Use an ephemeral system temporary location when a tool requires such data.

## Failure Handling

- If no `doc_id` exists, use `document-ingest` before answering.
- If the cache or index is empty or unreadable, report the exact problem and stop instead of inferring document content.
