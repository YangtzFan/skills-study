# Practical DOCX Editing

Read the sections relevant to the chosen tool and document features. These notes describe implementation hazards, not a requirement to use Python or OOXML for every task.

## Inspect before editing

A `.docx` is an OOXML ZIP package. Main body content is usually in `word/document.xml`; styles, numbering, headers, footers, comments, footnotes, and media have separate parts and relationships. Inspect what the operation needs, while accounting for features the chosen tool may discard.

`Document.paragraphs` alone does not represent the full document: tables, nested cells, text boxes, headers/footers, and review markup can contain additional text. Use supported body iteration APIs where available, or inspect block elements in document order. Do not claim complete coverage from a body-paragraph scan.

For a targeted edit, record the target's structural context and expected occurrence count before modifying it. Page numbers from a text parser are not reliable insertion anchors; use a capable renderer or a stable structural anchor.

## Python and OOXML

- Check that `python-docx` is installed before importing it. Install missing dependencies only under applicable host permissions; do not assume network access or introduce an online converter as a fallback.
- Creating or assigning `paragraph.text` replaces runs and can remove inline formatting and features. Assigning `cell.text` similarly replaces cell content. Use these only when replacement of the whole affected structure is intended.
- Word often splits a visible phrase across runs. Locate a match across logical text spans, then map offsets back to affected runs. Define how replacement formatting is inherited. Do not join across field, hyperlink, bookmark, or revision boundaries unless the operation deliberately handles them. A naive per-run replacement can miss the target; rebuilding a paragraph can destroy it.
- For simple insertions, reuse the appropriate paragraph style and necessary paragraph properties. Do not copy XML with bookmark, drawing, comment, or relationship IDs without ensuring uniqueness and remapping references. Moving or copying content between packages also requires related parts and media.
- Preserve `w:sectPr`, including paragraph-level section breaks and final body section properties. Headers and footers may be linked to earlier sections; editing one can affect others. Unlink only when the requested change requires independent content.
- Save explicitly as `.docx`. Loading and saving with a library does not guarantee preservation of every unsupported Word feature; select another method when required features cannot be retained.
- If editing a package directly, use namespace-aware XML tooling and preserve unmodified parts. Do not perform broad regex replacements on raw XML. Validate relationship targets and IDs affected by the edit.

## Chinese and mixed-script formatting

`run.font.name` generally sets Latin font attributes; East Asian glyphs may still use another font. For an explicitly chosen Chinese font, set `w:rFonts/@w:eastAsia` on the relevant style or run as well. Preserve theme-based fonts when the template relies on them. Check installed fonts before claiming visual equivalence; fallback can alter wrapping and pagination.

Distinguish points from centimeters and font size from line spacing. In `python-docx`, a numeric paragraph line spacing is a multiple; a `Pt(...)` length expresses fixed spacing. Fixed line heights can clip tall glyphs, equations, or inline images. Set line-spacing rules deliberately.

Use page dimensions minus margins and applicable gutters/columns when sizing content. Table-cell width further reduces usable width for nested images or tables. Control table autofit and column widths when required, and verify the rendered result. Long tables may need repeated header rows and deliberate row-splitting behavior.

## Fields and review features

TOC, PAGE, cross-reference, and citation fields contain instructions and cached results. Inserting a field or marking it for update is distinct from calculating it. `python-docx` is not a pagination or field-evaluation engine.

`python-docx` does not provide complete high-level support for tracked changes, Word citations, text boxes, and every equation or content control. Check the installed version's actual APIs rather than assuming support or absence from memory. Tracked revisions require proper revision elements and metadata; colored text or a comment is not a tracked change.

For advanced existing documents, prefer a capable Word tool when available or make a narrowly scoped package edit with explicit feature verification. If fidelity cannot be established, disclose the limitation instead of flattening the document silently.

## Verification examples

- **Append under a heading:** verify the new block appears before the next peer heading, after the intended existing content, and exactly once. Inspect adjacent tables or section breaks if present.
- **Replace a phrase:** verify intended matches changed, unintended matches did not, and formatting outside matched spans remains intact. Include split-run text in the check when present.
- **Populate a template:** check every required placeholder's resolved state and confirm intended headers, footers, and repeated locations. Do not assume all braces or underscores are placeholders.
- **Change page layout:** render affected sections and inspect pagination, headers/footers, table fit, and image dimensions. Reopening the ZIP package is insufficient for this operation.
