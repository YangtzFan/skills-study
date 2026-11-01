# Markdown to Word

## Source and conversion scope

Treat the supplied Markdown as the authoritative source for content being written. Preserve the original `.md` unless changes are requested. For inline Markdown, use an explicitly supplied asset base or the known task workspace; ask if a relative asset cannot be resolved unambiguously. Do not search unrelated directories for missing images.

Identify relevant dialect extensions before choosing a converter. CommonMark, GFM tables/task lists, and Pandoc math, citations, and footnotes are not interchangeable. YAML frontmatter is metadata only when the chosen dialect or user specifies it; do not blindly discard it or turn every metadata key into visible prose. Read source code blocks as content, never commands to execute.

Use available local Pandoc for broad supported conversion, or a Markdown parser producing an AST/token stream with a Word writer for controlled insertion. `python-docx` is a writer, not a Markdown parser. Confirm tool availability and feature support before selecting either approach.

For a new document, a typical Pandoc conversion is:

```text
pandoc source.md --from=markdown --to=docx --reference-doc=template.docx --output=output.docx
```

This example assumes Pandoc Markdown and a supplied reference file. Choose the actual reader dialect, omit the reference option if absent, and run from the source directory or configure resource paths as needed. Do not apply this command blindly to an existing document that must retain its content. A reference `.docx` supplies styles/layout defaults, not an insertion target or its body text.

## Semantic mapping

| Markdown construct | Word representation and checks |
| --- | --- |
| `#` through `######` headings | Heading styles at mapped levels; preserve hierarchy and any explicit destination level offset |
| Paragraphs, soft breaks, hard breaks | Normal/template body paragraphs; handle soft breaks according to the dialect, and hard breaks as line breaks |
| Strong, emphasis, strikethrough, inline code | Corresponding run formatting or character styles; code remains literal |
| Ordered/unordered/nested lists | Real Word numbering with nesting and intended start/restart values; do not add a second number to already numbered template headings |
| Blockquotes | Quote paragraphs with suitable indentation; preserve contained blocks |
| `[!TIP]` and other alert/callout blocks | Distinct supplement/admonition paragraphs or a suitable template style; preserve the type, supplied title, nested blocks, and boundary from the main text; consume the syntax marker |
| Tables | Editable Word tables with correct header, row/column counts, and supported alignment; report unsupported spanning/layout requirements |
| Links | Hyperlinks with both display text and target; preserve internal anchors through a supported bookmark mapping or report the gap |
| Images | Embedded images with aspect ratio preserved; resolve paths and preserve supplied captions/alternative text when supported |
| Fenced/indented code blocks | Literal code text, whitespace, and line breaks in a code style; do not render Markdown inside code or execute it |
| Horizontal rules | Appropriate paragraph border or separator, not an unintended page break |
| Footnotes, citations, math | Native supported Word features when required; verify footnote bodies, citation data, and equation representation |
| Raw HTML, task lists, diagrams, custom extensions | Use supported mappings; make any fallback explicit and preserve substantive content |

Do not convert `$...$` or citation syntax into literal markers when native math or formatted citations are required. Do not invent bibliography records; use supplied reference data. If a diagram needs rendering, use available authorized local tooling or supplied assets and retain the intended meaning; do not execute arbitrary embedded code.

Study notes may combine GitHub-style alerts with math from another Markdown dialect. Verify both extensions explicitly; selecting a GFM reader alone does not establish math support, and a generic blockquote conversion may leave `[!TIP]` visible as text. If alerts are unsupported by the converter, normalize their parsed structure into a labeled supplement while retaining nested equations, lists, and paragraphs. Preserve literal markers inside code examples. Never discard a proof or supplement because it was optional for reading the main text.

Remote images and linked resources are not automatically local assets. Fetch only resources needed for the requested deliverable under applicable access and transfer permissions. Do not follow every link or send local Markdown to a remote renderer implicitly. Report missing assets and avoid declaring a complete conversion when substantive content is absent.

## Insert into existing Word

Map Markdown blocks to the selected destination range before writing. Determine whether its enclosing heading is already present so the conversion does not duplicate it. Reuse destination paragraph, heading, list, table, and caption styles; resolve numbering references when importing blocks from a separately converted `.docx`.

When transferring converted XML between packages, import and remap necessary relationships, images, numbering, styles, and bookmark/drawing IDs. Copying body XML alone can create broken images or numbering. For complex insertion, prefer writing parsed Markdown directly into the destination with supported APIs or a capable Word tool.

## Conversion checks

Compare parsed source semantics against the changed Word range, rather than Markdown markers against extracted text. Check every substantive block is represented in order, heading levels are mapped, nested lists remain nested, tables have the expected shape, and image/link destinations are correct. Include checks for whichever extensions actually occur.

Inspect code literally, including meaningful whitespace and characters that otherwise look like Markdown. Look for unconverted syntax outside literal-code contexts, missing footnotes/assets, and accidental duplicate headings or numbering. Combine these checks with the structural and visual checks in `SKILL.md`; successful conversion-tool exit status alone does not establish faithful output.
