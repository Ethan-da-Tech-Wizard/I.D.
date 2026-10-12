# IDE Vision Spec: Next-Generation Script Editor

This document records the product and architecture direction for the IDE pillar
of NeonDAW / I.D.E.A.S., decided with Ethan on 2026-08-01. It is additive: it
does not replace `README.md`, `ARCHITECTURE.md`, `THE_IDEAS_MANIFEST.md`,
`THREAT_MODEL.md`, `SECURITY.md`, or the feature security review process.

## North Star

The IDE becomes a professional native script workstation for both full project
authoring and live performance control. It should feel closer to Ableton Live
plus Max/MSP than a generic text editor: fast enough for expert daily work,
visual enough for beginners to understand the system, and tightly connected to
the DAW, Engine, Studio, Git, and macro-runtime surfaces.

The target user set is broad by design:

- Non-programmer audio creators who need guided discovery, visual parameters,
  examples, and clear errors.
- Technical sound designers who need live modulation, deterministic rendering,
  project organization, and rapid iteration.
- Internal developers who need real IDE features, Git workflow support, search,
  diagnostics, keybindings, and project-scale navigation.

## Platform Decision

- **Editor core**: build on a native Qt widget stack, not Monaco, CodeMirror, or
  an embedded browser. This follows `ARCHITECTURE.md`: PySide6, Qt Widgets,
  offline startup, no embedded browser controls, no local HTTP servers.
- **Shell/UI model**: one local desktop process. Services such as indexing,
  diagnostics, Git, execution, macro extraction, and theme/keybinding loading
  are direct in-process Python services unless a reviewed wrapper explicitly
  allows a subprocess.
- **Design language**: Ableton/Max-style dockable production surface: dense,
  resizable, stable, keyboardable, low ornament, high feedback.

## Workspace Layout

The IDE layout is a dockable workspace, not a single editor panel.

Required default regions:

- **Left sidebar: Project Explorer**
  - File tree rooted at the active workspace.
  - Create, rename, delete, duplicate, reveal, copy relative path, and open
    actions.
  - Recent files, examples, snippets, script metadata, presets, safe API docs,
    and asset references relevant to the selected script.
  - First-class Git file status badges.
- **Center: Editor Grid**
  - Multi-tab editing.
  - Horizontal and vertical split panes.
  - Native gutter with line numbers, break/error/warning markers, changed-line
    Git markers, and executable-line affordances where supported.
  - Inline diff view for file, hunk, and selection-level review.
- **Bottom: Run / Terminal / Problems Pane**
  - Collapsible, resizable, and detachable.
  - Tabs for Run Output, Problems, Logs, Render Status, Audio Telemetry, Git
    Output, and optional interactive console surfaces.
  - Shows stdout/stderr-like script output as plain text, structured runtime
    events, errors, render progress, waveform/render preview status, and live
    engine telemetry.
- **Right: Inspector / Parameters**
  - Symbol outline, documentation, selected function details, script metadata,
    parameter bindings, and current execution state.
- **Separate Performance / Macro Runner Mode**
  - A focused live-control surface for parameter sliders, knobs, toggles,
    dropdowns, XY pads, envelopes, color controls, presets, transport, and
    safety state.

All panels must be collapsible, resizable, and layout-persisted per workspace
and per mode. Detachable panes must remain native Qt windows and must not create
browser or server surfaces.

## Git Integration

Git is first-class in the IDE, using the reviewed `app/ide/git.py` style of
explicit argument lists and workspace validation.

Required capabilities:

- Changed files in the sidebar.
- Changed-line gutter markers for additions, modifications, and deletions.
- Inline diff view for current file and selected hunks.
- Stage, unstage, commit, and revert hunk actions.
- Branch display in the IDE chrome.
- Git output/log pane.
- Clear handling of non-Git workspaces, detached HEAD, merge conflicts, and
  command failures.

Remote operations remain gated by the existing security posture: explicit user
action, reviewed wrappers, no shell command construction, and no hidden network
activity.

## Execution Model

The IDE must support both render-style execution and long-running live engine
execution.

Scripts stay Python-like. The goal is not to invent a separate beginner
language; the goal is a constrained, well-documented, Python-shaped creative
runtime with strong editor assistance, visible safe APIs, and progressive
power for trusted projects.

Required controls:

- Run
- Stop
- Restart
- Preview
- Render
- Export
- Clear Output
- Toggle Problems
- Toggle Macro Runner

Running a script may stream audio immediately, produce a file, or do both,
depending on the selected run profile. Execution output and errors appear in
all relevant surfaces:

- Inline editor markers.
- Problems panel.
- Run/output console.

Diagnostics that affect safe execution are blocking by default. The UI should
distinguish syntax errors, policy violations, invalid audio parameters, missing
assets/imports, range errors, performance warnings, and runtime failures.

Runtime capabilities should include:

- Project helper imports, subject to the active execution tier and workspace
  boundary.
- Persistent state for long-running live scripts, so parameter changes can
  update a running performance without resetting musical context.
- Musical scheduling primitives for bars, beats, steps, BPM sync, quantized
  launches, delayed events, and looped callbacks.
- Direct control of approved DAW state: tracks, mixer values, effects,
  transport, clips/patterns, render/export profiles, and live performance
  parameters.
- Run profiles that define whether a script is a one-shot render, preview,
  live performance process, utility task, or trusted external-tool action.

## Script Language And Runtime

The scripting surface remains Python-like, with normal Python syntax where it
can be supported safely and clearly. Beginner-friendly examples and templates
should still look like Python, not a proprietary patch language.

The runtime needs two complementary modes:

- **Render/evaluation mode**: deterministic script execution that produces a
  preview, render, exported file, asset transform, or project change.
- **Live performance mode**: a long-running runtime that keeps state between
  UI parameter changes, musical clock ticks, transport changes, and DAW events.

Live scripts should be able to subscribe to and schedule against musical time:

- `on_beat`
- `on_bar`
- `on_step`
- `every`
- `after`
- quantized launch points
- BPM-synced parameter ramps

Direct DAW control is in scope. The safe API should eventually expose approved
objects for transport, tracks, mixer channels, clips, samples, effects, render
targets, macro values, and automation. These APIs must be explicit capability
objects, not raw access to internal widget instances.

Project helper imports are allowed as a product goal. The implementation must
resolve them from the workspace manifest/index, reject path traversal, and make
their permission requirements visible before execution.

## Security Posture For Scripts

The user preference is to trust local scripts and allow external tools where
useful, but the application cannot treat that as arbitrary host execution by
default. The existing project security model forbids unsandboxed editor
execution, arbitrary Python, shell access, subprocess access, unsafe imports,
and path traversal.

The IDE therefore supports explicit execution tiers:

- **Safe Mode**: default. Scripts run through AST validation and reviewed
  capability APIs such as safe audio functions. Blocking diagnostics prevent
  execution when the script escapes the approved surface.
- **Trusted Project Mode**: project-wide opt-in. The whole workspace is marked
  trusted, and the IDE shows a persistent visible trust badge in the title/status
  chrome and run controls. Trusted scripts still run through a documented runner
  with workspace boundaries, resource caps, audit coverage, visible trust state,
  tests, and user-readable permission summaries.
- **External Tool Mode**: future reviewed capability for launching selected
  external tools. This is allowed as a product goal, but only through explicit
  run profiles, whitelisted commands, argument-list subprocess wrappers,
  workspace-scoped file access, visible confirmation, logs, and security review.

Blocking errors disable Run in Safe Mode. Experts may use a visible "run anyway"
path only when the project is already in Trusted Project Mode and the run
profile explicitly allows the required capability. Trusted scripts are still
prevented from touching files outside the workspace unless a future reviewed
capability grants narrow, user-selected access.

No feature in this spec authorizes raw `exec`, `shell=True`, arbitrary hidden
terminal commands, plugin loading, native code execution, or unrestricted file
access without a separate reviewed design.

## IntelliSense

Autocomplete is required for V1.

The completion engine must understand:

- Safe audio API functions.
- Function signatures.
- Parameter names, units, value ranges, defaults, and examples.
- Hover documentation.
- User-defined variables and functions in the active file.
- Symbols across open files in the current workspace.
- Snippets/templates for common audio, render, modulation, and project tasks.

Completions should trigger automatically while typing and also be available
through a hotkey. The completion popup must be native Qt, keyboard-first, and
fast enough to avoid interrupting live performance workflows.

Completion ranking should favor creative-context relevance: safe audio
functions, DAW controls, macro variables, project symbols, snippets, then
generic Python symbols. The user should see the safest and most likely creative
actions first without losing access to deeper Python-like constructs.

## Linting And Diagnostics

Real-time linting is required for V1 and should run locally.

Diagnostics must catch:

- Python syntax errors.
- Unsupported language features for the current execution mode.
- Unsafe calls/imports/attributes.
- Invalid safe audio API usage.
- Missing samples/assets/imports.
- Invalid parameter ranges and incompatible units.
- Performance risks such as unbounded loops, oversized generated buffers, or
  live-update code paths that would block audio.

Blocking diagnostics prevent Run/Preview/Render when they violate safety or
runtime correctness. Warnings remain non-blocking but visible. The Problems
panel is the canonical list, with inline markers and hover details mirroring
the same diagnostic objects.

Diagnostic messages must include both beginner-friendly explanations and raw
technical details. The visible summary should say what went wrong and how to fix
it; expanded details should include the precise exception, AST/policy rule,
source range, and execution tier requirement.

## Keybindings And Command Palette

Custom keybindings are required for V1.

Supported configuration surfaces:

- Built-in defaults.
- Global user keybinding JSON.
- Per-project keybinding JSON.
- UI editor for common remaps.
- Command palette for discoverability and keyboard-first operation.

Initial command groups:

- File: new, open, save, save as, duplicate, rename, delete.
- Editor: find, replace, format, comment toggle, go to definition, symbol
  search, split editor, close tab, next/previous tab.
- Run: run, stop, restart, preview, render, export, clear output.
- Layout: toggle sidebar, toggle terminal, toggle problems, toggle inspector,
  focus editor, focus explorer, focus macro runner.
- Git: stage file, stage hunk, unstage, commit, revert hunk, open diff.
- Theme: quick switch, open theme editor.

Conflicts must be detected and shown before saving a keymap.

Suggested default bindings:

- `Ctrl+P`: command palette / quick open.
- `Ctrl+B`: toggle sidebar.
- ``Ctrl+```: toggle bottom run pane.
- `Ctrl+Shift+M`: toggle Problems.
- `Ctrl+Enter`: run current script/profile.
- `Shift+F5`: stop.
- `Ctrl+Shift+Enter`: restart.
- `Ctrl+S`: save.
- `Ctrl+Shift+S`: save as.
- `Ctrl+Alt+M`: toggle Macro Runner.
- `Ctrl+\\`: split editor.
- `F12`: go to definition.
- `Ctrl+Shift+G`: focus Git.

## Themes And Syntax Scopes

Custom themes are required for V1. The theme system should build on the existing
local `.qss` theme engine while adding editor-token scopes.

Required theme capabilities:

- Built-in light, dark, and professional production themes.
- Import/export of custom themes through validated local `.qss` or structured
  theme files.
- Visual theme editor with color pickers.
- Per-scope syntax colors for keyword, function, safe audio function, number,
  string, comment, variable, type/class, parameter, operator, selection,
  caret, gutter, active line, error, warning, info, diff added, diff modified,
  and diff deleted.
- Global user preference and per-project override.

Theme files are configuration, not plugins. They must be bounded, validated,
local-only, and non-executable.

## Macro Runner And Visual Modulation

The Macro Runner is a core V1 feature, not a later add-on.

The editor automatically discovers top-level script variables and can expose
them as live UI controls. It may also infer deeper simple objects when the
shape is stable and safe to reflect, but top-level simple values are the first
supported path. Explicit annotations refine the generated controls.

Example:

```python
tempo = 120  # @slider min=60 max=180 step=1
gain = 0.8   # @slider min=0 max=1 step=0.01
mode = "pad" # @dropdown options=pad,pluck,bass
```

Required control types:

- Sliders.
- Knobs.
- Toggles.
- Dropdowns.
- XY pads.
- Envelopes.
- Color pickers where relevant.
- Numeric steppers/inputs.

Users must also be able to bind variables manually from the UI without editing
code comments. Manual bindings become project metadata and should be visible
next to the source variable so the code and visual surface never drift silently.

Parameter changes must be able to update the running script live. The runtime
must define which variables are hot-swappable, when changes take effect, and
which updates require restart or re-render. Live parameter binding must not
block the audio callback or UI event loop.

Macro Runner goals:

- Live improvisation.
- Reproducible rendering.
- Auto-generated layouts for immediate use.
- Manually arrangeable and saveable performance layouts.
- Performance snapshots that change many parameters at once.
- Saveable presets.
- Automation over time, including live recording while sliders/knobs/XY pads are
  moved.
- Clear mapping between code variables and visual controls.
- Beginner-friendly controls without hiding the underlying script.

Presets and automation data are project assets and must be stored with schema
versions so future migrations are explicit.

The Macro Runner should support both "generated from script" and "designed
performance panel" workflows. Generated controls make scripts usable
immediately. Saved layouts make serious live sets reproducible.

## Professional IDE Feature Set

V1 target capabilities:

- Multi-tab editing.
- Split editor panes.
- Minimap.
- Multiple cursors.
- Rectangular selection.
- Search across files.
- Replace across files with preview.
- Symbol outline / function list.
- Go to definition.
- Hover documentation.
- Inline safe API docs and examples.
- Formatting on save.
- Project templates.
- Snippets/templates.
- Problems panel.
- Git diff and commit flow.
- Workspace-scoped file navigation.
- Persistent layout state.
- Persistent per-project and global configuration.

Formatting runs automatically on save. If the file has syntax or policy errors,
the formatter should either preserve text and show a clear diagnostic or apply
only syntax-safe formatting ranges; it must not damage code while trying to be
helpful.

Examples must support both read-only references and editable copies. A user can
inspect canonical examples without accidentally modifying them, then fork one
into the active project as a normal file.

## Project System

The IDE project is the organizing layer for code, audio, generated assets, run
profiles, permissions, and performance state.

Supported project asset types:

- Python-like scripts.
- Helper modules.
- Audio samples.
- Presets.
- Macro layouts.
- Macro automation.
- Rendered WAVs.
- DAW patterns.
- Engine scenes.
- Images.
- Video files and timeline references.
- Documentation/examples.

Every project should have a manifest file, such as `ideas.project.json`, that
describes:

- Project schema version.
- Display name and description.
- Main scripts and run profiles.
- Asset folders.
- Generated-output folders.
- Required permissions/capabilities.
- Trusted Project Mode state.
- Macro layout/preset references.
- Theme/keybinding overrides.
- Git metadata hints where useful.

Recommended workspace folders:

- `scripts/` for user scripts and helper modules.
- `audio/` for imported project audio.
- `presets/` for reusable parameter and effect presets.
- `macros/` for Macro Runner layouts, snapshots, and automation.
- `renders/` for user-facing audio/video/image exports.
- `scenes/` for Engine scenes.
- `media/` for image/video source assets.
- `.ideas/` for app-owned indexes, caches, layout state, diagnostics snapshots,
  and generated metadata that should not be edited by hand.

Generated files should go where their purpose is clear. User-facing exports go
to `renders/`; implementation caches and indexes go under `.ideas/`; build-like
temporary output should stay under app-owned storage or `.ideas/build/`.

Required project templates:

- Live Sampler.
- Generative Beat.
- FX Macro.
- Game Audio Trigger.
- Visualizer.
- DAW Control Surface.
- Stem Renderer.
- Beginner Safe Script.
- Trusted Tool Runner, disabled until Trusted Project Mode and External Tool
  Mode are implemented and reviewed.

## Native Editor Architecture

Recommended service boundaries:

- `EditorDocument`: text, dirty state, file path, encoding, undo/redo metadata.
- `WorkspaceIndex`: workspace file tree, open files, symbols, examples,
  snippets, and asset references.
- `DiagnosticService`: syntax, policy, semantic, asset, and performance
  diagnostics.
- `CompletionService`: safe API, local symbols, workspace symbols, and snippets.
- `ExecutionService`: run profiles, safe runner integration, render/export
  dispatch, stop/restart lifecycle, output events.
- `MusicalClockService`: bars/beats/steps scheduling, BPM sync, quantized
  launch, and clock events shared with DAW transport.
- `MacroBindingService`: variable discovery, annotation parsing, live bindings,
  presets, automation, and control metadata.
- `GitService`: wrapper around reviewed Git commands and parsed status/diff
  models.
- `KeybindingService`: command registry, default bindings, user/project
  overrides, conflict detection.
- `ThemeService`: app QSS themes plus editor syntax scopes.
- `LayoutService`: per-mode and per-workspace dock/tab/split persistence.
- `ProjectManifestService`: schema-versioned project metadata, run profiles,
  permissions, asset folders, generated folders, and migration.

Services should be testable without a display wherever possible. UI widgets
should consume structured service models instead of parsing command output or
source text directly.

## V1 Roadmap

The desired V1 scope is the full professional script editor described above.
Implementation should still land in reviewable phases because each phase has
different risk.

1. **Editor foundation**
   - Native code editor widget with tabs, splits, gutter, syntax highlighting,
     minimap, multiple cursors, rectangular selection, line markers, file
     open/save, workspace file tree, and layout persistence.
2. **Diagnostics and safe API intelligence**
   - Local syntax/policy diagnostics, Problems panel, hover details,
     auto-complete, safe audio API signatures, snippets, and blocking run gate.
3. **Execution workbench**
   - Run/Stop/Restart/Preview/Render/Export controls, output panes, render
     status, structured runtime events, project helper imports, musical-clock
     scheduling, DAW control APIs, and safe-mode execution profiles.
4. **Git workbench**
   - Status badges, changed-line gutters, inline diff, stage/unstage/commit,
     branch display, hunk revert, and Git output.
5. **Customization**
   - Command palette, keybinding editor/JSON, theme editor/import/export,
     syntax-scope theme support, global and per-project config.
6. **Macro Runner**
   - Variable discovery, annotation parsing, live controls, presets,
     automation recording, performance snapshots, arrangeable layouts,
     performance mode, hot-swappable runtime binding, and render
     reproducibility.
7. **Trusted Project Mode review**
   - Only after Safe Mode is robust: define project-wide trust UX, visible trust
     badge, runner boundary, workspace limits, "run anyway" rules, resource
     limits, audit rules, tests, and documentation.
8. **External Tool Mode review**
   - Define whitelisted external tools, explicit run profiles, confirmation UX,
     subprocess wrappers, logging, workspace I/O rules, tests, and threat model
     updates.

## Explicit Non-Negotiables

- Professional authoring and live performance control are both first-class.
- The UX must serve beginners and experts without splitting into separate apps.
- No browser shell, Node dependency, local web server, or cloud dependency.
- No arbitrary script execution by default.
- Scripts remain Python-like.
- Project-wide Trusted Mode is allowed, visible, and still bounded.
- External tools are allowed only through reviewed, explicit run profiles.
- Local diagnostics, autocomplete, Git status, themes, keybindings, and Macro
  Runner are V1 goals.
- Errors must be understandable at beginner level while preserving exact
  technical detail for experts.
- The editor must remain fast under large projects and stable while audio is
  running.
- Every project has a manifest.
- Examples are available as both read-only references and editable copies.

## Open Decisions To Resolve During Implementation

- Exact native editor widget strategy: extend `QPlainTextEdit`, use
  `QScintilla` only if dependency review approves it, or build a custom text
  viewport.
- Exact trusted-mode permission vocabulary and the run-profile controls inside
  the project-wide trust state.
- Persistence schema for macro presets and automation lanes.
- Whether detached panes restore across sessions on multi-monitor setups.
- How much cross-file symbol intelligence is needed before a full language
  server abstraction becomes justified.
- Exact manifest filename and whether `.ideas/` should be hidden by default in
  the Project Explorer.
