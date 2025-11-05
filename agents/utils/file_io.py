"""
File I/O utilities for JSON and JSONL
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from loguru import logger


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"[LOAD] Reading JSON from {file_path}")
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data as JSON file"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    logger.info(f"[SAVE] Saved JSON to {file_path}")


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load JSONL file (one JSON object per line)"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"[LOAD] Reading JSONL from {file_path}")

    lines = path.read_text(encoding='utf-8').strip().split('\n')
    return [json.loads(line) for line in lines if line.strip()]


def save_jsonl(data: List[Dict[str, Any]], file_path: str) -> None:
    """Save list of dicts as JSONL file"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [json.dumps(item, ensure_ascii=False) for item in data]
    path.write_text('\n'.join(lines), encoding='utf-8')

    logger.info(f"[SAVE] Saved {len(data)} items to JSONL: {file_path}")
