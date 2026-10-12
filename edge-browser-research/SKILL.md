---
name: edge-browser-research
description: Use a local Edge or Chromium debugging session for authenticated website research and source-document downloads, including campus-library databases. Use when the user can access a site in Edge but remote readers cannot, or asks to connect, inspect, search, or verify downloads through that session. Do not use for ordinary public-page reading or unrelated browser/account administration.
---

# Edge Browser Research

Use the user's authorized local browser session for the requested sites. Establish connection, institutional access, download completion, and document readability as separate observations.

## Choose the access path

- Read the applicable global instructions and shared [research-browser contract](../research-browser/SKILL.md). Reuse already-read instructions and continue the same task directory when the research task continues.
- Inspect available browser tools and local runtimes. Reuse a usable browser tool or an existing Edge CDP endpoint before recommending MCP installation or new dependencies.
- This workflow does not authorize unrelated tabs, account changes, proxy changes, credential export, or third-party uploads. The user enters passwords, MFA, and CAPTCHA directly in the browser. Continue after authentication is verified; do not request the same authorization again.
- A remote reader does not inherit local browser cookies, campus network access, or v2rayN routing. Successful access in Edge does not establish that command-line HTTP traffic takes the same route.

## Connect to Edge

If the user already enabled debugging, inspect the loopback endpoint and relevant page first. Do not restart Edge or replace its profile unnecessarily.

If debugging is unavailable, explain that an ordinary running Edge window cannot automatically be controlled just because the user can browse the site. Offer a dedicated research window. On Windows, the user can run the following in PowerShell; the executable path must exist:

```powershell
$edgePath = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path -LiteralPath $edgePath)) {
    $edgePath = 'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
}
if (-not (Test-Path -LiteralPath $edgePath)) {
    throw 'Edge executable not found; locate the installed application first.'
}
& $edgePath --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="$env:TEMP\edge-paper-session" 'about:blank'
```

The dedicated profile does not inherit the user's ordinary Edge login state. Keep profiles outside research artifacts; never copy their cookies or credentials into `.agents-work/`. Have the user open the library/database entry point and complete authentication in this window.

The user may verify that `http://127.0.0.1:9222/json/version` opens. The agent should verify the endpoint independently; a user's confirmation alone is not proof that the current tool can connect. Do not ask the user to paste the debugger's WebSocket URL or authentication data into chat.

## Inspect and research

The existing [CDP helper](../web-reader/scripts/edge_cdp.py) supports `list`, selected-page `inspect`, and `download`. Resolve its path against this skill directory, then run it from the research workspace so artifacts land in that workspace:

```text
python <pack-root>/web-reader/scripts/edge_cdp.py list
python <pack-root>/web-reader/scripts/edge_cdp.py inspect --target <current-target-id>
```

- `list` returns sanitized page addresses and IDs; inspect only relevant pages. Target IDs belong to the live session and must not be hardcoded into reusable instructions.
- Use a native browser tool for navigation, form filling, search submission, and rendered controls when available. Otherwise use local CDP `Target.createTarget`, `Page.navigate`, and `Runtime.evaluate` within the user's authorized task. For approved clicks that open a tab or download, set `userGesture: true`. Wait for the resulting state rather than assuming `.click()` succeeded.
- The helper does not implement a general search/form automation API. Do not invent nonexistent subcommands. Use an available CDP/browser capability or state the missing capability precisely.
- Navigate through the actual library entry point, preserving the resulting session and proxy host. Do not substitute an unproxied publisher address when the authorized page uses a library proxy.
- Before using extracted text, check visibility. A CAPTCHA transcript can remain in an off-screen DOM after verification; `innerText` or a nonzero element rectangle alone does not prove the challenge is active. Check its displayed position and the actual blocking page state.
- Distinguish institutional access from personal-account login. Labels such as an institution name or “Access provided by” support session recognition, but actual article/download access still requires testing. A download can complete even if an auxiliary tab subsequently displays a login page; check completed files before reporting failure.
- Avoid logging signed links, return URLs, or opaque authentication parameters. Use a stable public article ID, DOI, title, or sanitized institution entry as durable provenance.

## Download and verify

Follow the detailed [local browser reference](../web-reader/references/local-browser.md). Create `.agents-work/<task-id>/downloads/` before downloading and register source files in the task `index.md`. Necessary processing files belong in `intermediates/`; evidence notes remain Markdown.

For a site's real download link or button:

```text
python <pack-root>/web-reader/scripts/edge_cdp.py download --target <current-target-id> --selector <download-css-selector> --task-id <YYYY-MM-DD-task-slug> --name <short-unique-name.pdf> --format pdf
```

Use `--format caj` and a `.caj` filename for CAJ/KDH. Select the actual clickable link; a containing span with matching text may not trigger the download.

- Keep the browser-level CDP session alive from `Browser.setDownloadBehavior` through `Browser.downloadProgress` completion. Disconnecting immediately after configuring the destination can restore Edge's default Downloads directory.
- Run one download at a time in a dedicated research browser. `target=_blank` may hide the opener through `noopener`; the helper associates events by relevant frames, related popups, or source/link origin. With unrelated concurrent downloads or cross-origin redirects, use a browser tool that can trace the full navigation.
- If the publisher opens a PDF preview rather than downloading, inspect the preview's iframe/embed source. Use the normal download control, or a same-session browser retrieval when the user authorized the file. Validate the response before writing; do not send its authenticated URL to a remote reader or silently export browser cookies into a separate HTTP client.
- Check completion state, real saved path, actual byte count, and file signature. For PDF format verification, check `%PDF-` and an EOF marker; for CAJ/KDH, retain the actual format. Record a hash when useful. These checks do not prove a parser can read the full document.
- Preserve short deterministic filenames on Windows and refuse unintended overwrites. When checking repeated operations, compare hashes; do not remove files merely because their names are similar.
- If a file landed in the default Downloads folder, identify the exact file created by this task, migrate it into the task directory subject to filesystem permissions, and update the index. Do not sweep or delete unrelated user downloads.
- Report per-database results separately. One successful article does not prove access to every journal, year, degree thesis, or file format. Apply [document-ingest](../document-ingest/SKILL.md) only when content extraction is needed; a download test need not ingest the full paper.

## Stop conditions and handoff

- Follow the shared external-call and spending budget. Local DOM checks consume no external attempts; navigation and file retrieval do. Do not blindly repeat a click when a login page, preview, challenge, cancellation, or timeout explains the missing download.
- Authentication failures require a changed/verified session before retrying. Let the user complete challenges; do not automate CAPTCHA solving or bypass subscription restrictions.
- Browser access, source-file download, format validation, and content extraction may have different success states. Return the actual completed work, saved file/record link, and remaining limitation in the user's language.
- If debugging was started only for this task, offer to close the dedicated research window when the user no longer needs it. Do not terminate unrelated Edge processes or interrupt a session the user wants to keep using.

## Validation and known coverage

The shared helper has offline regression checks:

```text
python -B <pack-root>/web-reader/scripts/test_edge_cdp.py
```

In the observed campus-library workflow, IEEE, Wanfang, and VIP delivered PDFs, and CNKI delivered CAJ/KDH. The new helper also completed an actual Wanfang PDF download into the task directory. These observations validate those tested paths, not universal database entitlement, CAJ extraction support, or every local HTTP/browser policy. No passwords, cookies, account identifiers, live target IDs, or authentication-bearing URLs belong in this skill.
