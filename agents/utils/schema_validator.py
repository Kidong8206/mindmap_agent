"""
JSON Schema validation utilities
"""

import json
from pathlib import Path
from typing import Dict, Any

import jsonschema
from loguru import logger


SCHEMA_DIR = Path("configs/schema")


def load_schema(schema_name: str) -> Dict[str, Any]:
    """
    Load JSON schema from configs/schema/

    Args:
        schema_name: Schema filename (e.g., "turns_schema.json")

    Returns:
        Schema dictionary
    """
    schema_path = SCHEMA_DIR / schema_name

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    return json.loads(schema_path.read_text(encoding='utf-8'))


def validate_schema(data: Dict[str, Any], schema_name: str) -> bool:
    """
    Validate data against JSON schema

    Args:
        data: Data to validate
        schema_name: Schema filename (e.g., "turns_schema.json")

    Returns:
        True if valid, raises ValidationError otherwise
    """
    schema = load_schema(schema_name)

    try:
        jsonschema.validate(instance=data, schema=schema)
        logger.info(f"[VALIDATION SUCCESS] Data matches schema: {schema_name}")
        return True

    except jsonschema.ValidationError as e:
        logger.error(f"[VALIDATION ERROR] {e.message}")
        logger.error(f"Failed path: {list(e.path)}")
        logger.error(f"Schema path: {list(e.schema_path)}")
        raise

    except Exception as e:
        logger.error(f"[VALIDATION ERROR] Unexpected error: {e}")
        raise
