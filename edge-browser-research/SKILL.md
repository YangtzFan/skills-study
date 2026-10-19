---
name: edge-browser-research
description: Use an authorized local Microsoft Edge session for website authentication, academic-database paper search, and paper downloads, including campus-library databases. Requires available Edge browser tools or a loopback debugging session. Do not use for general web search, ordinary public-page reading, or unrelated browser/account administration.
---

# Edge Browser Research

Use the user's authorized local browser session for the requested sites. Establish connection, institutional access, download completion, and document readability as separate observations.

## Boundary with public browsing

This worker owns authorized website authentication, academic-database paper search, and paper downloads in that Edge workflow. General public search and ordinary public-page reading belong to [web-research](../web-research/SKILL.md), even when its chosen browser is Microsoft Edge. Browser brand alone does not invoke this skill. Its Edge-only requirement does not restrict the public worker's use of Firefox, Chrome, Chromium, or Edge.

Public search CAPTCHAs alone do not trigger this authentication workflow; the public worker handles verification state under its own guidance. When the task actually needs authenticated or institutional access, follow this skill with the applicable authorization and retain the active task and budget. Do not attach a public-search task to this worker's persistent authenticated profile, export its Cookies to an HTTP client, or delete that profile during public-task cleanup. The public worker's temporary-session rules do not replace this skill's profile and task-window rules.

## Choose the access path

- Read the applicable global instructions and shared [research-browser contract](../research-browser/SKILL.md). Reuse already-read instructions and continue the same task directory when the research task continues.
- Inspect available browser tools and local runtimes. Reuse a usable browser tool or an existing Edge CDP endpoint before recommending MCP installation or new dependencies.
- This workflow does not authorize unrelated tabs, account changes, proxy changes, credential export, or third-party uploads. The user enters passwords, MFA, and CAPTCHA directly in the browser. Continue after authentication is verified; do not request the same authorization again.
- A remote reader does not inherit local browser cookies, campus network access, or v2rayN routing. Successful access in Edge does not establish that command-line HTTP traffic takes the same route.

## Separate the profile from task sessions

The global profile below retains browser preferences and login state across projects. Task pages, search progress, and restoration instructions belong to `.agents-work/<task-id>/browser/session.json`, registered in that task's `index.md`. Never copy browser profiles, cookies, passwords, or Chromium `Sessions/` files into the task directory. Separate windows share authentication and storage; they do not isolate accounts.

Before creating, resuming, checkpointing, or closing task windows, read [task browser sessions](references/task-sessions.md). A new task gets a fresh blank window in the shared research profile. Continuing a task restores only that task's safe recorded pages, after checking for its already-open window. Do not infer the active task from whichever tabs happen to be open or from the last browser session.

## Connect to Edge

Connect only to a loopback debugging endpoint and inspect only task-relevant tabs. Prefer a dedicated research profile; debugging gives control of the connected browser. If the user already enabled debugging, inspect the endpoint and relevant page first. Do not restart Edge or replace its profile unnecessarily.

Use a persistent dedicated research profile, independent of the current project or working directory:

- Windows: `%LOCALAPPDATA%\CodexBrowser\EdgeResearch`. Resolve `LocalApplicationData` from the operating system; do not hard-code a username.
- Linux: `${XDG_CONFIG_HOME:-$HOME/.config}/codex-browser/edge-research`. Honor `XDG_CONFIG_HOME` only when it is an absolute path; otherwise use `$HOME/.config`. Resolve paths on the machine running the browser, including when the agent runs in WSL or a container. A Windows Edge instance uses the Windows profile path, not a Linux path.

Resolve the profile for the browser's OS user, not a different sandbox/container account. If the browser host/user cannot be established, diagnose that mismatch instead of creating another profile under the agent's home or workspace.

Reuse the selected directory when it exists and create it only when absent. Never use a project-local `.agents-edge-session`, a temporary directory, or the user's ordinary Edge profile for a new research session. These paths are local to each OS/user; do not share one live profile between Windows and Linux or assume credentials can be transferred between them.

First check the existing loopback CDP endpoint (normally `http://127.0.0.1:9222/json/version`). If it is usable and authorized for the task, connect to it without restarting Edge or migrating its active profile, then select or create the current task's window using the session rules above. Reusing a browser process does not assign its existing pages to the current task. If the fixed profile is already in use but no usable endpoint is available, diagnose that instance; do not launch competing instances with the same profile or remove profile locks. Do not forcibly migrate an existing legacy profile.

Before controlling an existing endpoint, verify its browser instance and profile using known authorized launch information or scoped local process metadata. A reachable port or a successful `/json/version` response alone does not prove it uses the expected profile. If an explicitly authorized legacy instance is reused, report that exception rather than claiming the fixed profile was selected. Do not attach to an unknown instance or stop the process occupying the port; diagnose the mismatch and preserve the authorized instance.

If debugging is unavailable, explain that an ordinary running Edge window cannot automatically be controlled just because the user can browse the site. Within the user's authorization, launch a dedicated research window, or provide the appropriate command below when manual launch is needed. Check the endpoint first as above; the executable path must exist.

Windows (PowerShell):

```powershell
$edgePath = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path -LiteralPath $edgePath)) {
    $edgePath = 'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
}
if (-not (Test-Path -LiteralPath $edgePath)) {
    throw 'Edge executable not found; locate the installed application first.'
}
$edgeLocalData = [Environment]::GetFolderPath('LocalApplicationData')
if ([string]::IsNullOrWhiteSpace($edgeLocalData)) {
    throw 'LocalApplicationData could not be resolved; do not fall back to a project or temporary directory.'
}
$edgeProfilePath = Join-Path $edgeLocalData 'CodexBrowser\EdgeResearch'
if (-not (Test-Path -LiteralPath $edgeProfilePath)) {
    New-Item -ItemType Directory -Path $edgeProfilePath -Force | Out-Null
}
if (-not (Test-Path -LiteralPath $edgeProfilePath -PathType Container)) {
    throw 'The research profile path exists but is not a directory.'
}
& $edgePath --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="$edgeProfilePath" --new-window 'about:blank'
```

Linux (Bash, in the user's graphical desktop session):

```bash
(
    set -eu
    edge_path=''
    for edge_candidate in microsoft-edge microsoft-edge-stable microsoft-edge-beta microsoft-edge-dev; do
        if command -v "$edge_candidate" >/dev/null 2>&1; then
            edge_path=$(command -v "$edge_candidate")
            break
        fi
    done
    if [ -z "$edge_path" ]; then
        printf '%s\n' 'Edge executable not found; locate the installed application first.' >&2
        exit 1
    fi
    case "${XDG_CONFIG_HOME:-}" in
        /*) edge_config_root=$XDG_CONFIG_HOME ;;
        *) edge_config_root="${HOME:?HOME must be set}/.config" ;;
    esac
    case "$edge_config_root" in
        /*) ;;
        *) printf '%s\n' 'The profile root must be an absolute path.' >&2; exit 1 ;;
    esac
    edge_profile_path="$edge_config_root/codex-browser/edge-research"
    if [ ! -d "$edge_profile_path" ]; then
        (umask 077; mkdir -p -- "$edge_profile_path")
    fi
    "$edge_path" --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 \
        --user-data-dir="$edge_profile_path" --new-window 'about:blank'
)
```

On Linux, use an available graphical session for manual authentication. If none is available, report that limitation or connect to an already authorized reachable loopback session; do not silently switch to headless mode or add `--no-sandbox`.

Do not pass `--restore-last-session`. For the dedicated research profile, check Edge's own startup setting when establishing this workflow; configure it through the normal settings interface to open a new tab rather than resume the previous session. Do not change the ordinary Edge profile or edit live preference/session databases. Explicit `about:blank` and `--new-window` arguments alone do not prove that startup settings, policy, or crash recovery cannot reopen old pages. Verify the actual windows after launch; follow the task-session reference if old pages reappear.

The dedicated profile does not inherit the user's ordinary Edge login state. Reusing it preserves saved browser state, but sites can expire authentication; verify access and let the user complete login, MFA, or CAPTCHA when required. Keep profiles outside research artifacts; never copy their cookies or credentials into `.agents-work/`. Have the user open the library/database entry point and complete authentication in this window when needed. Retain the profile across tasks and browser restarts; do not delete or reset it as task cleanup.

The user may verify that `http://127.0.0.1:9222/json/version` opens. The agent should verify the endpoint independently; a user's confirmation alone is not proof that the current tool can connect. Do not ask the user to paste the debugger's WebSocket URL or authentication data into chat.

## Inspect and research

Use the browser tools exposed by the host or available local CDP capabilities; this skill has no bundled browser helper. Inspect the actual tool/protocol schema and use current target IDs from the live session.

- Use a native browser tool for navigation, form filling, search submission, and rendered controls when available. Otherwise use local CDP `Target.createTarget`, `Page.navigate`, and `Runtime.evaluate` within the user's authorized task. For approved clicks that open a tab or download, set `userGesture: true`. Wait for the resulting state rather than assuming `.click()` succeeded.
- Do not invent helper subcommands or assume a general search/form API exists. Use an available CDP/browser capability or state the missing capability precisely.
- Navigate through the actual library entry point, preserving the resulting session and proxy host. Do not substitute an unproxied publisher address when the authorized page uses a library proxy.
- Before using extracted text, check visibility. A CAPTCHA transcript can remain in an off-screen DOM after verification; `innerText` or a nonzero element rectangle alone does not prove the challenge is active. Check its displayed position and the actual blocking page state.
- Distinguish institutional access from personal-account login. Labels such as an institution name or “Access provided by” support session recognition, but actual article/download access still requires testing. A download can complete even if an auxiliary tab subsequently displays a login page; check completed files before reporting failure.
- Avoid logging signed links, return URLs, or opaque authentication parameters. Use a stable public article ID, DOI, title, or sanitized institution entry as durable provenance.

## Download and verify

Before triggering a download, create the active task's `downloads/` directory and configure that destination through an available browser tool or a supported CDP download-setting command. Coordinate browser-wide settings with other task windows. Choose the actual clickable control, rather than a containing span, and observe its resulting navigation or download state before retrying.

Verify completion through available download events/history and the actual saved file; report a limitation if completion cannot be established. Check that the file is nonempty and matches the expected format rather than a login/error page; record its path, size or hash, and sanitized source in the task index. Preserve the actual format, checking PDF or CAJ/KDH signatures as applicable; a renamed extension does not convert a file or prove parser support. Retain the same task ID and shared budget.

When full text of an external paper is needed, download and verify it in the task `downloads/` directory before reading it, preferring an authorized PDF. If PDF is unavailable, retain a permitted source in its actual format; do not persist authentication data. If a valid full-text file cannot be saved, report the limitation and do not claim full-text review from a preview. Abstract or metadata review alone does not require downloading the full paper.

- If the publisher opens a PDF preview rather than downloading, inspect the preview's iframe/embed source. Use the normal download control, or a same-session browser retrieval when the user authorized the file. Validate the response before writing; do not send its authenticated URL to a remote reader or silently export browser cookies into a separate HTTP client.
- Report per-database results separately. One successful article does not prove access to every journal, year, degree thesis, or file format. Download verification does not establish document readability.

## Stop conditions and output

- Follow the shared external-call and spending budget. Local DOM checks consume no external attempts; navigation and file retrieval do. Do not blindly repeat a click when a login page, preview, challenge, cancellation, or timeout explains the missing download.
- Authentication failures require a changed/verified session before retrying. Let the user complete challenges; do not automate CAPTCHA solving or bypass subscription restrictions.
- Return sanitized results appropriate to the task: discovery candidates (title, stable URL/ID, relevance); page evidence (URL, exact passages and anchors, observed access/coverage); or downloads (saved path, source ID/URL, completion, size/hash, format checks). Do not invent HTTP status or extraction results. Return actual results and remaining limitations in the user's language.
- Checkpoint the current task's safe pages and progress before an authorized close. Close only its verified owned targets/windows and retain the persistent global profile. Do not use browser-wide `Browser.close`, terminate all Edge processes, or close another task's window as routine cleanup; those actions require an explicit user request covering them.

## Validation

Validate modified automation with relevant checks for the actual browser tool or CDP implementation; live site tests require the task's authorization and budget. A tested article verifies only that session, article, and file format, not every database entitlement or parser.

For task-session changes, also use the acceptance checks in the task-session reference. Report profile reuse, task-page restoration, and current site authentication as separate results; restored tabs or an existing Cookie database do not establish a valid login.
