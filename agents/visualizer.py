"""
Mindmap visualization module

Renders graph JSON to PNG image using networkx and matplotlib.
"""

from typing import Dict, Any
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from loguru import logger

from agents.utils import load_json


def visualize_mindmap(
    graph_json_path: str,
    output_png_path: str,
    figsize: tuple = (16, 12),
    dpi: int = 150
) -> None:
    """
    Visualize mindmap graph as PNG image

    Args:
        graph_json_path: Path to graph JSON from Stage 4
        output_png_path: Path to save PNG image
        figsize: Figure size in inches (width, height)
        dpi: Image resolution (dots per inch)
    """
    logger.info(f"[VISUALIZE] Rendering mindmap to {output_png_path}")

    # Load graph data
    data = load_json(graph_json_path)
    graph_data = data.get("graph", {})

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    layout_info = graph_data.get("layout", {})

    if not nodes:
        logger.warning("[VISUALIZE] No nodes to visualize")
        return

    # Create NetworkX directed graph
    G = nx.DiGraph()

    # Add nodes
    for node in nodes:
        G.add_node(
            node["id"],
            label=node["label"],
            type=node["type"],
            color=node["color"],
            size=node["size"],
            x=node["x"],
            y=node["y"]
        )

    # Add edges
    for edge in edges:
        G.add_edge(
            edge["source"],
            edge["target"],
            weight=edge.get("weight", 1.0),
            edge_type=edge.get("type", "main")
        )

    # Extract positions from nodes (GPT already calculated them)
    pos = {node["id"]: (node["x"], node["y"]) for node in nodes}

    # Extract colors and sizes
    node_colors = [G.nodes[n]["color"] for n in G.nodes]
    node_sizes = [G.nodes[n]["size"] * 30 for n in G.nodes]  # Scale up for visibility

    # Extract labels
    labels = {n: G.nodes[n]["label"] for n in G.nodes}

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        edge_color='#cccccc',
        width=2,
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        ax=ax
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        ax=ax
    )

    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=10,
        font_weight='bold',
        font_family='DejaVu Sans',
        ax=ax
    )

    # Add legend
    root_patch = mpatches.Patch(color='#3498db', label='Root (Session Topic)')
    main_patch = mpatches.Patch(color='#2ecc71', label='Main Path')
    side_patch = mpatches.Patch(color='#95a5a6', label='Side Path')
    ax.legend(handles=[root_patch, main_patch, side_patch], loc='upper right')

    # Add title
    session_id = data.get("session_id", "unknown")
    layout_type = layout_info.get("type", "unknown")
    ax.set_title(
        f"Mindmap: {session_id} (Layout: {layout_type})",
        fontsize=16,
        fontweight='bold',
        pad=20
    )

    # Remove axes
    ax.axis('off')

    # Tight layout
    plt.tight_layout()

    # Save
    output_path = Path(output_png_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"[VISUALIZE] SUCCESS: Saved to {output_png_path}")


def visualize_comparison(
    graph_paths: list,
    titles: list,
    output_png_path: str,
    figsize: tuple = (20, 8)
) -> None:
    """
    Visualize multiple mindmaps side-by-side for comparison

    Args:
        graph_paths: List of graph JSON paths
        titles: List of titles for each graph
        output_png_path: Path to save comparison PNG
        figsize: Figure size in inches
    """
    n_graphs = len(graph_paths)

    if n_graphs == 0:
        logger.warning("[VISUALIZE] No graphs to compare")
        return

    fig, axes = plt.subplots(1, n_graphs, figsize=figsize)

    if n_graphs == 1:
        axes = [axes]

    for idx, (graph_path, title) in enumerate(zip(graph_paths, titles)):
        ax = axes[idx]

        # Load graph
        data = load_json(graph_path)
        graph_data = data.get("graph", {})
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        # Create graph
        G = nx.DiGraph()

        for node in nodes:
            G.add_node(node["id"], **node)

        for edge in edges:
            G.add_edge(edge["source"], edge["target"])

        pos = {node["id"]: (node["x"], node["y"]) for node in nodes}
        node_colors = [G.nodes[n]["color"] for n in G.nodes]
        node_sizes = [G.nodes[n]["size"] * 20 for n in G.nodes]
        labels = {n: G.nodes[n]["label"] for n in G.nodes}

        # Draw
        nx.draw_networkx_edges(G, pos, edge_color='#cccccc', width=1.5, arrows=True, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, ax=ax)

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_png_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    logger.info(f"[VISUALIZE] Comparison saved to {output_png_path}")
