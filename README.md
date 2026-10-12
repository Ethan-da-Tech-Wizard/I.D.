# I.D. — Creative Suite Design

Design specifications and a procedural sample generator for a desktop creative-suite concept.

**Status:** Design and supporting tools  
**Built with:** Python and design documents

[Project guide](docs/PROJECT_GUIDE.md) · [Every file explained](docs/FILE_GUIDE.md) · [Licenses and dependencies](docs/LICENSE_REVIEW.md)

## Start here

- [docs/IDE_VISION_SPEC.md](docs/IDE_VISION_SPEC.md) — Documentation: IDE Vision Spec: Next-Generation Script Editor. Covers North Star; Platform Decision; Workspace Layout.
- [generate_samples.py](generate_samples.py) — Python implementation of generate samples. Defines `create_dir`, `save_wav`, `generate_kick`, `generate_snare`, `generate_hihat`, `generate_wub` and 2 more top-level symbols.
- [project.ideas](project.ideas) — Structured project data; top-level fields: `version`, `ide_filename`, `ide_content`, `daw`.

[Detailed setup, usage, and development notes](PROJECT_NOTES.md) preserve the previous project documentation.

## Repository layout

| Path | Role |
| --- | --- |
| [docs/](docs/) | Project documentation, decisions, and reference material (6 tracked entries). |

## Scope and current limits

The larger NeonDAW application is maintained in the separate I.D.E.A.S. repository.

## License

Original project code retains **MIT** terms in [LICENSE](LICENSE). Third-party libraries, media, data, models, and tools retain their own terms. See the [license review](docs/LICENSE_REVIEW.md) and [dependency inventory](docs/DEPENDENCIES.csv).
