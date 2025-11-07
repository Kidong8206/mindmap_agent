import json
from pathlib import Path

def load_jsonl(file_path):
    """JSONL 파일 읽기 (대화 데이터)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_json(data, file_path):
    """JSON 파일 저장"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(file_path):
    """JSON 파일 읽기"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_keywords(graph):
    """그래프에서 키워드 추출 (노드 라벨)"""
    return set(node['label'] for node in graph['graph']['nodes'])
