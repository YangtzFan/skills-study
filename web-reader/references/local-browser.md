# Local authenticated browser access

Use this reference when a task needs an already-authorized browser session, interactive database access, or source-file downloads. It does not authorize access to unrelated tabs or credential export.

This reference documents local browser download mechanics and the existing helper interface. Use only an authorized local session and keep authentication in the browser.

## Downloads

- Follow the Work Directory Contract in `../../research-browser/SKILL.md`. Create `.agents-work/<task-id>/downloads/` before starting. Keep the browser/CDP connection alive from download configuration through the completion event; closing it early can restore the default destination.
- Wait for completion with a bounded timeout, then inspect the actual file path, byte count, and signature (PDF header `%PDF-` and EOF marker; CAJ/KDH markers for those formats). Record whether validation checked only the format or also parsed the document. Inspect the browser's download history if the file landed elsewhere; migrate only files identified as created by this task, subject to filesystem permissions.
- A homepage institutional label does not prove full-text entitlement. A download button does not prove a completed download. CAJ/KDH success does not prove PDF availability or a working text parser.
- Use short deterministic filenames on Windows. Refuse unintended overwrites. Use hashes to identify repeat files before deciding whether to retain or remove them.
- Keep authentication-bearing URLs out of logs and indexes. Register files with a sanitized source page and a stable public article ID/DOI when available.

## Optional local CDP helper

`../scripts/edge_cdp.py` uses Python's standard library plus the already-installed `websocket-client` package. It neither starts a browser nor installs packages. Its default endpoint is `http://127.0.0.1:9222`; it rejects non-loopback debugging endpoints.

Run from the target workspace. Inspect its `--help` first when needed:

```text
python <skill-directory>/scripts/edge_cdp.py list
python <skill-directory>/scripts/edge_cdp.py inspect --target <target-id>
python <skill-directory>/scripts/edge_cdp.py download --target <target-id> --selector a.download --task-id 2026-10-12-paper-search --name Wanfang-article.pdf --format pdf
```

`list` prints sanitized page URLs, `inspect` reads only the selected page's visible text, and `download` clicks the specified link/button as a browser user gesture, holds the browser connection through completion, saves inside the active workspace task directory, checks format markers, and appends a verification entry to `index.md`. It does not extract the paper's text or prove parser compatibility. The agent must still respect the shared external-call budget and the user's task scope.

Run download actions sequentially in a dedicated research browser, with no unrelated downloads in progress. The helper associates events with the selected frame, a related popup, or the source/link origin because `target=_blank` with `noopener` may conceal the popup's opener. A redirect to an unrelated origin may require a browser tool that can trace the full navigation rather than this helper.

Offline regression checks are available with `python <skill-directory>/scripts/test_edge_cdp.py`; these do not contact a site or launch a browser.

If the site opens a preview, login page, or challenge instead of starting a download, the helper stops after its timeout. Inspect the resulting browser state and resolve the actual missing interaction; do not blindly repeat the click.
