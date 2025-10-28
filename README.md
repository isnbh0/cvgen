# cvgen

**cvgen** is a work-in-progress tool for streamlining the management of multilingual resume content in YAML format.

It is designed to help users maintain a **single source of truth for their resume content**, which can then be used to easily generate resumes in multiple languages and formats.

## Installation

```bash
uv sync
```

## Quick Start Template

If you're looking for a ready-to-use template to quickly test out cvgen's features or jump-start your own CV project, check out the [cvgen-template](https://github.com/isnbh0/cvgen-template) repository. It includes:

- Example CV demonstrating all CVGen features
- Build automation and demo showcasing filtering capabilities
- Complete reference documentation in English and Korean

## Requirements

- Python >= 3.13.3
- rendercv >= 2.0 (uses Typst, no LaTeX required)

## Examples

- [Basic example with Korean content](examples/basic_ko)

## Inspiration

- [rendercv](https://github.com/sinaatalay/rendercv)
