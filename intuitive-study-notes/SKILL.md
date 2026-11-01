---
name: intuitive-study-notes
description: Write, extend, or polish Chinese science and engineering study notes and lecture material through gradual explanation, intuitive meaning, simple worked examples, and selective proofs.
---

# Intuitive Study Notes

Help readers understand concepts, follow calculations, and judge when a method applies. Build on their existing knowledge, preserve accuracy, and keep abstraction and proof overhead proportionate.

## Contract and inputs

Accept the topic or outline, requested scope, reader background when supplied, existing notes, and any source text or evidence handoff. For continuation or polishing, inspect the target passage and enough surrounding material to preserve its notation, prerequisites, heading levels, and progression. Ask only when missing material prevents the requested work; a new note on a specified topic does not require an existing file.

Use supplied sources and available knowledge within the request's scope. Preserve source locators and coverage limitations when writing from evidence; distinguish added explanations or examples from claims attributed to a source. Do not fill unreadable or uninspected source passages with invented content. Capability selection and missing-evidence or output-format handoffs follow [AGENTS.md](../AGENTS.md) and [research-browser](../research-browser/SKILL.md#routing-and-handoffs); this writing skill requires no prior research workflow.

## Writing principles

- **Follow the learning progression.** Introduce concepts through familiar ideas, concrete problems, or natural questions. Explain why they are needed; move from concrete to general and simple to complex as appropriate. Adapt the order instead of forcing a template or an engineering application into every topic.
- **Give formulas meaning.** State necessary conditions and explain new symbols. Use geometry, operations, or practical meaning to show what changes and what the result tells the reader. Analogies support definitions rather than replacing them.
- **Teach through small examples.** Choose simple cases that expose the idea. Show key steps and their purpose, then interpret the result. Reuse examples across related topics; add a counterexample or variation when it resolves a likely confusion, without accumulating exercises.
- **Select proofs for understanding.** Keep short explanatory derivations in the main text; usually omit complex proofs. Put a few important proofs or supplements in `> [!TIP]` blocks with short titles, rather than moving every omitted proof there. The main text must remain understandable and usable without these blocks; keep applicability conditions in the main text.
- **Guide with connected prose.** Use plain, direct language and transitions that reflect the actual progression or reasoning. Avoid forced contrasts, unexplained jargon, and formula-only jumps. Briefly recall or reference earlier material instead of repeatedly teaching it again.
- **Keep the note structure simple.** Follow existing heading levels, numbering, and notation. Use bold phrases within sections and display important formulas separately. Use lists or tables for parallel properties, steps, or comparisons; explain ideas in paragraphs.
- **Keep intuition accurate.** Distinguish easily confused objects and concepts, and retain assumptions that affect conclusions. Examples illustrate general claims but do not establish them. Check formulas and calculations; do not inherit source errors as stylistic conventions.

Before delivery, read for continuity, meaningful explanations of key formulas, useful examples, and proofs or supplements that interrupt the main thread. Remove repetition and expansions that do not help understanding.

## Output

Return the requested prose directly for an answer-only task, or write the requested passage/file at its specified destination. Follow the existing Markdown dialect and asset paths when editing notes; preserve unrelated sections. Use Markdown for a Markdown deliverable or a conversion handoff, without requiring a saved intermediate. In Markdown, keep `[!TIP]` supplements within properly quoted blocks, including their paragraphs and formulas, so their boundaries remain clear. For other output formats, preserve the supplement's title, content, and separation from the main explanation.
