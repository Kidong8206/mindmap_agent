def validate_sessions(data):
    """Stage 1 출력 검증"""
    assert "conversation_id" in data, "conversation_id 누락"
    assert "sessions" in data, "sessions 누락"
    
    sessions = data["sessions"]
    assert len(sessions) > 0, "세션이 비어있음"
    
    all_turns = []
    for session in sessions:
        assert "session_id" in session, "session_id 누락"
        assert "title" in session, "title 누락"
        assert "turn_ids" in session, "turn_ids 누락"
        
        # 최소 길이 확인
        assert len(session["turn_ids"]) >= 5, f"세션 {session['session_id']} 너무 짧음 (< 5턴)"
        
        # 연속성 확인
        turn_ids = session["turn_ids"]
        for i in range(len(turn_ids) - 1):
            assert turn_ids[i+1] == turn_ids[i] + 1, "turn_ids 비연속"
        
        all_turns.extend(turn_ids)
    
    # 중복/누락 확인
    assert len(all_turns) == len(set(all_turns)), "turn_id 중복 존재"
    
    return True

def validate_contexts(data):
    """Stage 2 출력 검증"""
    assert "conversation_id" in data, "conversation_id 누락"
    assert "contexts" in data, "contexts 누락"
    
    contexts = data["contexts"]
    main_path_count = 0
    
    for ctx in contexts:
        assert "turn_id" in ctx, "turn_id 누락"
        assert "session_id" in ctx, "session_id 누락"
        assert "level" in ctx, "level 누락"
        assert "parent_turn_id" in ctx or ctx["parent_turn_id"] is None, "parent_turn_id 문제"
        
        if ctx["level"] == 0:
            main_path_count += 1
    
    # 메인 경로 존재 확인
    assert main_path_count > 0, "메인 경로 없음"
    
    # 메인 경로 연속성 확인
    main_contexts = [c for c in contexts if c["level"] == 0]
    for i in range(len(main_contexts) - 1):
        curr = main_contexts[i]
        next_ctx = main_contexts[i+1]
        assert next_ctx["parent_turn_id"] == curr["turn_id"], "메인 경로 비연속"
    
    return True

def validate_keywords(data):
    """Stage 3 출력 검증"""
    assert "conversation_id" in data, "conversation_id 누락"
    assert "keywords" in data, "keywords 누락"
    
    for kw_set in data["keywords"]:
        assert "turn_id" in kw_set, "turn_id 누락"
        assert "keywords" in kw_set, "keywords 누락"
        
        keywords = kw_set["keywords"]
        assert len(keywords) > 0, f"턴 {kw_set['turn_id']} 키워드 없음"
        
        for kw in keywords:
            assert "text" in kw, "keyword text 누락"
            assert "type" in kw, "keyword type 누락"
    
    return True

def validate_graph(data):
    """Stage 4 출력 검증"""
    assert "conversation_id" in data, "conversation_id 누락"
    assert "layout" in data, "layout 누락"
    assert "graph" in data, "graph 누락"
    
    graph = data["graph"]
    assert "nodes" in graph, "nodes 누락"
    assert "edges" in graph, "edges 누락"
    
    nodes = graph["nodes"]
    edges = graph["edges"]
    
    # 최소 노드 확인
    assert len(nodes) >= 3, "노드 수 너무 적음 (< 3)"
    
    # 노드 구조 확인
    node_ids = set()
    for node in nodes:
        assert "id" in node, "node id 누락"
        assert "label" in node, "node label 누락"
        assert "level" in node, "node level 누락"
        assert "position" in node, "node position 누락"
        
        node_ids.add(node["id"])
    
    # 간선 유효성 확인
    for edge in edges:
        assert "from" in edge, "edge from 누락"
        assert "to" in edge, "edge to 누락"
        assert edge["from"] in node_ids, f"존재하지 않는 노드: {edge['from']}"
        assert edge["to"] in node_ids, f"존재하지 않는 노드: {edge['to']}"
    
    return True
