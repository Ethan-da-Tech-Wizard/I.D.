# I.D. — Creative Suite Design

Design specifications and a procedural sample generator for a desktop creative-suite concept.

**Status:** Design and supporting tools  
**Built with:** Python and design documents

## Reading order

1. Read the root README for project purpose and setup navigation.
2. Follow the entry points below to find the implementation.
3. Use the file guide to locate individual modules, tests, assets, and configuration.
4. Check component licenses before redistributing dependencies or assets.

## Important paths

- [docs/IDE_VISION_SPEC.md](../docs/IDE_VISION_SPEC.md) — Documentation: IDE Vision Spec: Next-Generation Script Editor. Covers North Star; Platform Decision; Workspace Layout.
- [generate_samples.py](../generate_samples.py) — Python implementation of generate samples. Defines `create_dir`, `save_wav`, `generate_kick`, `generate_snare`, `generate_hihat`, `generate_wub` and 2 more top-level symbols.
- [project.ideas](../project.ideas) — Structured project data; top-level fields: `version`, `ide_filename`, `ide_content`, `daw`.

## Structure

| Path | Role |
| --- | --- |
| [docs/](../docs/) | Project documentation, decisions, and reference material (6 tracked entries). |

## Scope

The larger NeonDAW application is maintained in the separate I.D.E.A.S. repository.

## Maintaining the guide

The file catalog is a source-inspection snapshot, not proof that every runtime path works. Update it when moving files or changing module responsibilities. The 2026-10-12 documentation review did not run every application, deploy services, or validate all historical performance claims.
