def evaluate(generated_graph, golden_graph):
    """
    3가지 지표로 마인드맵 평가
    
    Args:
        generated_graph: 생성된 마인드맵 (dict)
        golden_graph: 정답 마인드맵 (dict)
    
    Returns:
        dict: {
            "node_count": int,
            "node_score": float (0-100),
            "keyword_overlap": float (0-100),
            "max_depth": int,
            "depth_score": float (0-100),
            "total_score": float (0-100)
        }
    """
    from utils import extract_keywords
    
    # 1. 노드 개수 평가 (30%)
    node_count = len(generated_graph['graph']['nodes'])
    if 10 <= node_count <= 30:
        node_score = 100
    elif node_count < 10:
        node_score = max(0, node_count * 10)  # 10개 이하는 감점
    else:
        node_score = max(0, 100 - (node_count - 30) * 2)  # 30개 초과 감점
    
    # 2. 키워드 중복도 평가 (40%)
    generated_keywords = extract_keywords(generated_graph)
    golden_keywords = extract_keywords(golden_graph)
    
    if len(golden_keywords) == 0:
        keyword_overlap = 0
    else:
        overlap_count = len(generated_keywords & golden_keywords)
        keyword_overlap = (overlap_count / len(golden_keywords)) * 100
    
    # 3. 구조 깊이 평가 (30%)
    max_depth = max(node['level'] for node in generated_graph['graph']['nodes'])
    if 2 <= max_depth <= 5:
        depth_score = 100
    elif max_depth < 2:
        depth_score = max_depth * 50  # 너무 얕으면 감점
    else:
        depth_score = max(0, 100 - (max_depth - 5) * 10)  # 너무 깊으면 감점
    
    # 총점 계산
    total_score = (node_score * 0.3) + (keyword_overlap * 0.4) + (depth_score * 0.3)
    
    return {
        "node_count": node_count,
        "node_score": round(node_score, 2),
        "keyword_overlap": round(keyword_overlap, 2),
        "max_depth": max_depth,
        "depth_score": round(depth_score, 2),
        "total_score": round(total_score, 2)
    }
