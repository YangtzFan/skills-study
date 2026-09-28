---
name: document-ingest
description: Convert referenced local documents into structured Markdown and retrieval artifacts while preserving page or section provenance. Use when a user attaches a supported file or provides a local document path.
---

# Document Ingest

## When to Use

- Use this skill when the user attaches a document, provides a local file path, or refers to an uploaded document.
- Supported formats include PDF, DOCX, XLSX, CSV, PPTX, TXT, Markdown, HTML, EPUB, PNG, and JPEG.

## Preferred Tools

| Format | Preferred tools |
| --- | --- |
| PDF | PyMuPDF or pdfplumber; OCRmyPDF and Tesseract for OCR |
| DOCX | python-docx, Mammoth, or Pandoc |
| XLSX and CSV | openpyxl or pandas |
| PPTX | python-pptx |
| TXT and Markdown | Direct text reading |
| HTML | Trafilatura |
| EPUB | Pandoc or EbookLib |
| PNG and JPEG | `image-analysis` with local OCR and an approved relay model when configured |

Use Docling or Unstructured only when a format-specific tool is unavailable or produces inadequate results.

## Workflow

1. Confirm that the file exists, determine its type from content or reliable metadata, and record its absolute path.
2. Compute `doc_id` as the first 12 hexadecimal characters of the file's SHA-256 digest so the identifier remains stable when the file is moved.
3. Create `skills-study/work-dir/<task-id>/documents/<doc_id>/` for derived artifacts only when the task needs persisted extraction results.
4. Extract text while preserving the source structure. Keep PDF page numbers, DOCX heading levels, spreadsheet sheet names, and PPTX slide numbers.
5. For a standalone image, a scanned page, or visually significant content such as a diagram or table, read and apply `skills-study/image-analysis/SKILL.md`. Run local OCR as the baseline and request an approved relay vision model when its configuration and authorization requirements are satisfied.
6. Mark OCR-derived chunks with `"ocr": true` and model-derived observations with the configured relay and model identifiers.
7. Write `content.md`, `chunks.md`, and `metadata.md` in the document artifact directory. Link any image-analysis Markdown produced under the active task directory, and do not create JSON, JSONL, HTML, plain-text, or binary artifacts there.
8. Split content on structural boundaries before using size-based chunking. Target 800 to 1,200 tokens per chunk with approximately 100 tokens of overlap when overlap is useful.

## Output

Return JSON with this shape:

```json
{
  "doc_id": "ab12cd34ef56",
  "path": "/absolute/path/to/file.pdf",
  "mime": "application/pdf",
  "pages": 24,
  "words": 8312,
  "language": "en",
  "content_md": "skills-study/work-dir/<task-id>/documents/ab12cd34ef56/content.md",
  "chunks_md": "skills-study/work-dir/<task-id>/documents/ab12cd34ef56/chunks.md",
  "metadata_md": "skills-study/work-dir/<task-id>/documents/ab12cd34ef56/metadata.md",
  "image_analysis_md": null,
  "anchors": ["p1", "p2", "sec:introduction"],
  "status": "ok"
}
```

Write each chunk as a Markdown section in `chunks.md`. Keep its metadata in a compact table or fenced JSON block within that Markdown file:

```markdown
## Chunk ab12cd34ef56:p7:c2

| Field | Value |
| --- | --- |
| doc_id | ab12cd34ef56 |
| page | 7 |
| section | Methods |
| tokens | 903 |

Exact extracted text goes here.
```

## Rules

- Treat the source file as read-only.
- Do not upload local file contents to a third-party service without explicit user consent.
- Do not assume that a relay model alias such as `Image 2` supports image understanding. Confirm the configured model capability or report that it is unsupported.
- Do not copy a user-provided source file into `skills-study/work-dir/`; keep it at its original path and persist only Markdown derivatives.
- If extraction requires a non-Markdown temporary file, place it in the operating system's temporary directory, convert the useful result to Markdown under `skills-study/work-dir/`, and remove the temporary copy after successful extraction.
- Preserve page numbering exactly, including anchors for blank PDF pages.
- Preserve enough provenance in every chunk to support exact citations later.
- Do not claim exact page provenance for source formats that do not provide stable pages. Use section, sheet, or slide provenance instead.

## Failure Handling

- For an encrypted document, request the password and do not attempt to bypass encryption.
- For a corrupted file, report the exact error and do not guess its contents.
- For an unsupported format, identify the limitation and name the supported conversion targets.
- If relay analysis fails, preserve the OCR result, report the sanitized failure details required by `image-analysis`, and do not represent the model analysis as completed.
