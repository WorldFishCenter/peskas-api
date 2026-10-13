"""
FIELDS.md, the column reference of every dataset, rendered from field_metadata.py.

Regenerate after changing a field:  python -m peskas_api.schema.fields_doc
tests/test_field_metadata.py fails while FIELDS.md is out of date.
"""

from pathlib import Path

from peskas_api.schema.dataset_config import get_all_dataset_types
from peskas_api.schema.field_metadata import get_all_fields_metadata
from peskas_api.schema.scopes import SCOPE_DEFINITIONS

FIELDS_MD = Path(__file__).resolve().parents[3] / "FIELDS.md"


def _sentence(text: str) -> str:
    text = " ".join(text.split()).replace("|", "\\|")
    return text if text.endswith(".") else text + "."


def render() -> str:
    """The whole FIELDS.md text."""
    lines = [
        "<!-- Generated from src/peskas_api/schema/field_metadata.py by",
        "     `python -m peskas_api.schema.fields_doc`. Do not edit by hand. -->",
        "",
        "# Fields",
        "",
        "Every column each endpoint returns, in order. The API serves the same",
        "descriptions at `/metadata/{dataset}`, which needs no key.",
    ]
    for dataset in get_all_dataset_types():
        fields = get_all_fields_metadata(dataset.name)
        lines += [
            "",
            f"## `/data/{dataset.endpoint}`",
            "",
            f"{dataset.description}. {len(fields)} columns.",
            "",
            "| Column | Type | Unit | Description |",
            "| --- | --- | --- | --- |",
        ]
        for f in fields.values():
            text = _sentence(f.description)
            if f.possible_values:
                text += " Values: " + ", ".join(f"`{v}`" for v in f.possible_values) + "."
            if f.ontology_url:
                text += f" [Ontology]({f.ontology_url})"
            if f.url:
                text += f" [Reference]({f.url})"
            lines.append(f"| `{f.name}` | {f.data_type} | {f.unit or ''} | {text} |")

        scopes = SCOPE_DEFINITIONS.get(dataset.name, {})
        if scopes:
            lines.append("")
            for scope, columns in scopes.items():
                listed = ", ".join(f"`{c}`" for c in columns)
                lines.append(f"- `scope={scope}` returns {listed}.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    FIELDS_MD.write_text(render())
