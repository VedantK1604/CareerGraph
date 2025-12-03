"""FastAPI application for CareerGraph."""
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv
import asyncio

from careergraph.models.schemas import (
    RoadmapQuery,
    RoadmapResponse,
    ExportRequest,
    RoadmapNode
)
from careergraph.agents.graph import generate_roadmap
from careergraph.utils.export import generate_html_export

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CareerGraph API",
    description="AI-powered career roadmap generator with multi-agent orchestration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="careergraph/static"), name="static")


@app.get("/")
async def root():
    """Serve the main application page."""
    return FileResponse("careergraph/static/index.html")


@app.post("/api/generate-roadmap", response_model=RoadmapResponse)
async def create_roadmap(query: RoadmapQuery):
    """
    Generate a career roadmap based on the user query.
    
    This endpoint orchestrates multiple AI agents to:
    1. Validate the query is career/education related
    2. Research and gather learning resources
    3. Structure the information into a hierarchical roadmap
    """
    try:
        # Generate roadmap using multi-agent system
        result = await generate_roadmap(query.query)
        
        # Check if validation failed
        if not result.get("is_valid", False):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query: {result.get('validation_message', 'Query must be career or education related')}"
            )
        
        # Check for errors
        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"Error generating roadmap: {result['error']}"
            )
        
        # Extract roadmap structure
        structure = result.get("roadmap_structure", {})
        nodes = result.get("nodes", [])
        
        if not nodes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate roadmap nodes"
            )
        
        # Create response
        response = RoadmapResponse(
            query=query.query,
            title=structure.get("title", f"Roadmap: {query.query}"),
            description=structure.get("description", "Career learning roadmap"),
            nodes=nodes,
            total_time=structure.get("total_time"),
            generated_at=datetime.now().isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@app.post("/api/export-roadmap")
async def export_roadmap(request: ExportRequest):
    """
    Export a roadmap as a standalone HTML file.
    
    The exported file includes all interactivity and works offline.
    """
    try:
        html_content = generate_html_export(request.roadmap)
        
        # Generate filename
        safe_title = "".join(c for c in request.roadmap.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"roadmap_{safe_title}.html"
        
        # Save to temp file
        temp_path = f"/tmp/{filename}"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return FileResponse(
            path=temp_path,
            filename=filename,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
