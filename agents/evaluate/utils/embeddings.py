"""
Embedding calculation utilities for evaluation

Handles sentence embeddings and similarity computations.
"""

import numpy as np
from typing import List, Optional
from pathlib import Path


def calculate_embeddings(
    texts: List[str],
    model_name: str = "jhgan/ko-sroberta-multitask",
    cache_path: Optional[str] = None
) -> np.ndarray:
    """
    Calculate embeddings for list of texts

    Args:
        texts: List of text strings
        model_name: Sentence transformer model name
        cache_path: Optional path to save/load embeddings

    Returns:
        Embedding matrix of shape (n_texts, embedding_dim)
    """
    # Check cache first
    if cache_path and Path(cache_path).exists():
        return np.load(cache_path)

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        embeddings = model.encode(texts, show_progress_bar=False)

        # Save to cache
        if cache_path:
            Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
            np.save(cache_path, embeddings)

        return embeddings

    except ImportError:
        # Fallback: return random embeddings for testing
        import warnings
        warnings.warn(
            "sentence-transformers not installed. Using random embeddings for testing."
        )
        return np.random.randn(len(texts), 384)


def cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """
    Calculate pairwise cosine similarity matrix

    Args:
        embeddings: Embedding matrix (n, d)

    Returns:
        Similarity matrix (n, n)
    """
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / (norms + 1e-8)

    # Compute cosine similarity
    similarity = normalized @ normalized.T

    return similarity


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def calculate_coherence(
    embeddings: np.ndarray,
    indices: Optional[List[int]] = None
) -> float:
    """
    Calculate coherence of a set of embeddings

    Coherence = average cosine similarity to centroid

    Args:
        embeddings: Full embedding matrix
        indices: Optional indices to select subset

    Returns:
        Coherence score (0-1)
    """
    if indices:
        subset = embeddings[indices]
    else:
        subset = embeddings

    if len(subset) < 2:
        return 1.0  # Single item is perfectly coherent

    # Calculate centroid
    centroid = subset.mean(axis=0)

    # Calculate similarity of each item to centroid
    similarities = []
    for emb in subset:
        sim = cosine_similarity(emb, centroid)
        similarities.append(sim)

    return np.mean(similarities)


def calculate_path_coherence(
    embeddings: np.ndarray,
    path_turns: List[int]
) -> dict:
    """
    Calculate detailed coherence metrics for a path

    Args:
        embeddings: Full embedding matrix
        path_turns: List of turn indices in the path

    Returns:
        Dict with coherence metrics
    """
    if len(path_turns) < 2:
        return {
            "coherence": 1.0,
            "mean_similarity": 1.0,
            "std_similarity": 0.0,
            "min_similarity": 1.0
        }

    path_embeddings = embeddings[path_turns]
    centroid = path_embeddings.mean(axis=0)

    # Calculate similarities
    similarities = [
        cosine_similarity(emb, centroid)
        for emb in path_embeddings
    ]

    return {
        "coherence": np.mean(similarities),
        "mean_similarity": np.mean(similarities),
        "std_similarity": np.std(similarities),
        "min_similarity": np.min(similarities),
        "max_similarity": np.max(similarities),
        "centroid_norm": np.linalg.norm(centroid)
    }


def calculate_topic_transition_stability(
    embeddings: np.ndarray,
    session_boundaries: List[int]
) -> float:
    """
    Calculate smoothness of topic transitions between sessions

    Args:
        embeddings: Full embedding matrix
        session_boundaries: List of session start indices

    Returns:
        Stability score (0-1)
    """
    if len(session_boundaries) < 2:
        return 1.0

    # Calculate centroid for each session
    session_centroids = []
    for i in range(len(session_boundaries)):
        start = session_boundaries[i]
        end = session_boundaries[i + 1] if i + 1 < len(session_boundaries) else len(embeddings)

        session_embs = embeddings[start:end]
        centroid = session_embs.mean(axis=0)
        session_centroids.append(centroid)

    # Calculate similarity between consecutive sessions
    transitions = []
    for i in range(len(session_centroids) - 1):
        sim = cosine_similarity(session_centroids[i], session_centroids[i + 1])
        transitions.append(sim)

    return np.mean(transitions)
