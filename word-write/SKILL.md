---
name: word-write
description: Convert Markdown content into Word documents (.docx), creating files or inserting and replacing content in existing documents while respecting template styles. Use when Markdown is the content source and a Word file is the deliverable; reading or answer-only drafting alone does not require this skill.
---

# Word Write

## Contract

Markdown is the source of the content written into Word. Accept a Markdown file or inline Markdown, its referenced assets, an optional existing Word document or template, and the intended output location. Convert its structure and inline formatting into native Word content, either as a new document or within the requested range of an existing document. The existing Word file supplies the destination structure and styles; the Markdown supplies the new or replacement content.

If drafting is part of the request, prepare the content as Markdown before conversion. Inline Markdown is sufficient; do not require a physical `.md` intermediate unless requested or useful for reproducibility. If neither source Markdown nor authorization to draft is available, ask for the missing content. Do not silently expand this workflow into arbitrary Word-only editing.

Capability selection and research handoffs belong to [AGENTS.md](../AGENTS.md) and [research-browser](../research-browser/SKILL.md). Reuse existing content and evidence; writing a Word document does not itself require extraction, research, or knowledge-base registration.

## Resolve the operation

- Carry forward the source Markdown, destination, template, and formatting requirements. Preserve supplied wording and semantics unless editing is authorized; conversion removes syntax markers by interpreting them, not by rewriting the prose.
- For existing files, identify the target by heading, bookmark, table label, placeholder, or distinctive surrounding text. Inspect all matching locations before changing them. Ask only when ambiguous matches would change which content is edited.
- Inspect the actual document structure and relevant styles, sections, tables, headers, footers, and existing review markup before choosing an editing method. A flattened text extraction cannot establish layout fidelity.
- Respect the requested destination. Otherwise save a clearly named `.docx` in the user's task workspace, outside the skill installation. Preserve the original by default with a separate output; an explicit request to overwrite authorizes that write, subject to host permissions. Do not require another confirmation for an already authorized edit.

## Choose available tools

Inspect installed libraries and exposed tools before relying on them. Prefer the least invasive available method that can preserve the features involved:

| Situation | Suitable approach |
| --- | --- |
| Markdown to a new document | Available local Pandoc with a reference `.docx` when appropriate, or a Markdown parser plus `python-docx`/a capable Word tool |
| Markdown into an existing document | Parse Markdown and insert native Word blocks into the selected range, using destination styles; preserve unrelated content |
| Targeted changes in an existing `.docx` | Edit the relevant runs/elements; preserve surrounding package parts and relationships |
| Precise Word pagination, field updates, advanced equations, or review markup | Available Microsoft Word automation or a document tool with demonstrated support |
| Legacy `.doc` input | Use an available genuine converter or Word; renaming the extension is not conversion |
| `.docm`, signed documents, or embedded objects | Choose a method that preserves the required features; disclose conversion or signature consequences before a consequential write |

Read [references/docx-editing.md](references/docx-editing.md) when using `python-docx`, manipulating OOXML, or handling mixed Chinese/Latin formatting. Do not silently round-trip a complex document through a tool that cannot preserve its required features. If no available method meets the requirement, explain the concrete limitation and retain usable work.

Local processing is the default. Do not upload source documents to online converters or other external services without applicable authorization. Do not execute embedded macros. Word automation must close only documents and application instances owned by the task; never kill a user's Word session to release a lock.

## Convert Markdown semantics

Read [references/markdown-to-word.md](references/markdown-to-word.md) for source handling, mappings, and conversion-specific verification. Establish the Markdown dialect from the source and requested features, including tables, footnotes, math, or other extensions. Use a real parser or converter; regex stripping and literal Markdown pasted into Word do not fulfill conversion.

Map headings, paragraphs, emphasis, links, lists, tables, code, and images into their corresponding Word structures. Preserve their order and nesting. Apply the destination's style mapping, including any requested heading-level offset. Report unsupported substantive constructs rather than silently dropping them. Resolve asset paths against the Markdown file's directory or an explicit base for inline input.

For an existing Word document, convert only the supplied Markdown into the requested target range. A Pandoc reference document supplies styles and layout defaults; it does not merge content into an existing document or preserve its body automatically. Do not regenerate the whole destination when only a section was requested.

## Write and format

- Reuse template styles and section settings. For new documents, use semantic heading, paragraph, caption, and list styles; choose restrained defaults when no specification exists. Do not impose a thesis or official-document format unless requested.
- Match the requested insertion position and preserve body order, including interleaved tables. When appending, account for the final section properties; do not accidentally place content outside the document body or change earlier section settings.
- Preserve unaffected text and formatting, numbering, table merges, hyperlinks, fields, bookmarks, headers, footers, and page/section breaks. Treat unsupported features explicitly rather than claiming universal fidelity.
- For Chinese text, set East Asian fonts where needed as well as Latin fonts; use real paragraph spacing, indents, and line spacing instead of manual spaces and blank lines. Use real numbering when an editable numbered list is required.
- Insert tables as tables and images with appropriate dimensions and captions. Preserve image aspect ratios and fit within usable page width. Do not replace an editable table with a screenshot unless requested.
- Keep quotations, citations, numbers, and source labels faithful to supplied evidence. Do not invent references or populate unknown substantive template values as facts. Mark unresolved values visibly only when a draft is acceptable.
- Comments, tracked changes, citations, contents, and page numbers are document features, not merely styled text. Create them through supported mechanisms when requested. Do not silently accept existing revisions or flatten fields into their displayed text.

## Save and verify

Save to a temporary sibling file where practical, validate it, then place it at the final destination. Do not overwrite a locked document or leave a partial file presented as the completed deliverable.

Verification should follow the scope and features actually changed:

1. Confirm the saved file exists, is nonempty, and can be reopened by the chosen reader. For `.docx`, check ZIP integrity and the required document package parts.
2. Compare the source Markdown's parsed blocks and inline semantics with the converted Word range: text, heading hierarchy, order, list nesting, table dimensions, links, images, code, and any requested extensions. Check insertion location and occurrence counts. For targeted edits, confirm surrounding structures remain intact. Account for Markdown syntax being consumed during conversion; raw text equality or a whole-document phrase search is insufficient.
3. When layout matters, render with an available Word or compatible renderer and inspect affected pages for overflow, clipping, broken tables, headings stranded at page ends, or blank pages. Inspect the whole document when template or section changes can affect every page. Keep renders separate from the requested Word deliverable.
4. Update fields through a capable engine when needed, then recheck. A request to update fields on open does not prove that fields, contents, references, or page numbers have been recalculated. Renderer differences do not prove identical Word pagination.

When rendering or a required feature is unavailable, state precisely what was checked and what remains unverified. Structural checks alone do not establish visual fidelity. Do not claim that an unopened file was tested in Microsoft Word.

## Delivery

Return a clickable link to the final Word file, a brief description of what was written or changed, and any material unresolved issue. Report the final artifact rather than only a script, plan, or pasted draft. Preserve user-requested originals and deliverables; remove only task-owned disposable files when appropriate.
