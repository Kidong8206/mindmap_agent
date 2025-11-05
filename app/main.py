"""
Mindmap Laboratory API

FastAPI application for mindmap generation pipeline.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

from scripts.run_pipeline import run_pipeline
from agents.utils import load_json

# Initialize FastAPI
app = FastAPI(
    title="Mindmap Laboratory API",
    description="GPT-powered mindmap generation pipeline",
    version="1.0.0"
)


# ===== Request/Response Models =====

class PipelineRequest(BaseModel):
    """Request model for pipeline execution"""
    session_id: Optional[str] = None
    layout_type: str = "hierarchical"
    layout_direction: str = "top-down"


class PipelineResponse(BaseModel):
    """Response model for pipeline execution"""
    status: str
    session_id: str
    run_id: str
    total_processing_time: float
    visualization_path: Optional[str] = None
    error: Optional[str] = None


# ===== API Endpoints =====

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "msg": "Mindmap Laboratory API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline_endpoint(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    layout_type: str = "hierarchical",
    layout_direction: str = "top-down"
):
    """
    Run complete mindmap generation pipeline

    Args:
        file: Raw conversation file (text or JSON)
        session_id: Optional conversation ID
        layout_type: Layout algorithm (hierarchical, radial, timeline, force_directed)
        layout_direction: Layout direction (top-down, left-right, radial-out, chronological)

    Returns:
        Pipeline execution result with paths and metrics
    """
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Run pipeline
        result = run_pipeline(
            input_conversation=tmp_path,
            session_id=session_id,
            layout_type=layout_type,
            layout_direction=layout_direction
        )

        return PipelineResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/results/{run_id}/metadata")
def get_result_metadata(run_id: str):
    """
    Get pipeline result metadata

    Args:
        run_id: Run identifier

    Returns:
        Metadata JSON
    """
    metadata_path = f"outputs/runs/{run_id}/metadata.json"

    if not Path(metadata_path).exists():
        raise HTTPException(status_code=404, detail="Run not found")

    return load_json(metadata_path)


@app.get("/results/{run_id}/graph")
def get_result_graph(run_id: str):
    """
    Get generated mindmap graph JSON

    Args:
        run_id: Run identifier

    Returns:
        Graph JSON
    """
    graph_path = f"outputs/runs/{run_id}/4_graph.json"

    if not Path(graph_path).exists():
        raise HTTPException(status_code=404, detail="Graph not found")

    return load_json(graph_path)


@app.get("/results/{run_id}/visualization")
def get_result_visualization(run_id: str):
    """
    Get mindmap visualization image

    Args:
        run_id: Run identifier

    Returns:
        PNG image file
    """
    viz_path = f"outputs/runs/{run_id}/visualization.png"

    if not Path(viz_path).exists():
        raise HTTPException(status_code=404, detail="Visualization not found")

    return FileResponse(
        viz_path,
        media_type="image/png",
        filename=f"{run_id}_mindmap.png"
    )


@app.get("/results/list")
def list_results(limit: int = 10):
    """
    List recent pipeline runs

    Args:
        limit: Maximum number of results to return

    Returns:
        List of run metadata
    """
    runs_dir = Path("outputs/runs")

    if not runs_dir.exists():
        return {"runs": []}

    # Get all run directories sorted by modification time (newest first)
    run_dirs = sorted(
        runs_dir.iterdir(),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:limit]

    results = []
    for run_dir in run_dirs:
        metadata_path = run_dir / "metadata.json"
        if metadata_path.exists():
            try:
                metadata = load_json(str(metadata_path))
                results.append({
                    "run_id": run_dir.name,
                    "session_id": metadata.get("session_id"),
                    "status": metadata.get("status"),
                    "total_time": metadata.get("total_processing_time"),
                    "layout_type": metadata.get("layout_type")
                })
            except Exception:
                continue

    return {"runs": results}


# ===== Development Server =====

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
