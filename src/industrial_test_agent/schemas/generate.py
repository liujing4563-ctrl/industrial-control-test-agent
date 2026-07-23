"""Generate deterministic JSON Schema files from Pydantic models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from industrial_test_agent.schemas.registry import SCHEMA_MODELS


JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_ID_PREFIX = "urn:industrial-test-agent:schema:"


def generate_schema_documents() -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for filename, model in SCHEMA_MODELS.items():
        schema_name = filename.removesuffix(".schema.json")
        schema = model.model_json_schema(mode="validation")
        documents[filename] = {
            "$id": f"{SCHEMA_ID_PREFIX}{schema_name}:1.0",
            "$schema": JSON_SCHEMA_DIALECT,
            **schema,
        }
    return documents


def render_schema(document: dict[str, Any]) -> str:
    return json.dumps(
        document,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def write_schema_documents(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_files = set(SCHEMA_MODELS)
    for path in output_dir.glob("*.json"):
        if path.name not in expected_files:
            path.unlink()
    for filename, document in generate_schema_documents().items():
        (output_dir / filename).write_text(
            render_schema(document),
            encoding="utf-8",
        )


def find_schema_drift(output_dir: Path) -> list[str]:
    expected = generate_schema_documents()
    actual_files = {path.name for path in output_dir.glob("*.json")}
    drift = sorted(actual_files ^ set(expected))
    for filename, document in expected.items():
        path = output_dir / filename
        if path.is_file() and path.read_text(encoding="utf-8") != render_schema(
            document
        ):
            drift.append(filename)
    return sorted(set(drift))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从 Pydantic 契约生成 JSON Schema",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("schemas"),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查已提交 Schema 是否与模型一致",
    )
    args = parser.parse_args()

    if args.check:
        drift = find_schema_drift(args.output_dir)
        if drift:
            parser.error(f"JSON Schema 存在漂移：{', '.join(drift)}")
        return
    write_schema_documents(args.output_dir)


if __name__ == "__main__":
    main()
