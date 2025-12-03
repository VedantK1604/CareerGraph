"""Pydantic models for CareerGraph API."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Resource(BaseModel):
    """A learning resource with metadata."""
    title: str = Field(..., description="Resource title")
    url: str = Field(..., description="Resource URL")
    type: str = Field(..., description="Resource type: video, documentation, course, book, paper, article")
    description: str = Field(..., description="Brief description of the resource")
    duration: Optional[str] = Field(None, description="Estimated time to complete")
    source: Optional[str] = Field(None, description="Source platform (e.g., YouTube, Coursera, Official Docs)")
    published_date: Optional[str] = Field(None, description="Publication or last updated date")


class RoadmapNode(BaseModel):
    """A node in the career roadmap graph."""
    id: str = Field(..., description="Unique node identifier")
    title: str = Field(..., description="Node title")
    description: str = Field(..., description="Node description")
    level: int = Field(..., description="Hierarchy level (0=root, 1=main topic, 2=subtopic, 3=unit)")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    resources: List[Resource] = Field(default_factory=list, description="Associated learning resources")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite node IDs")
    estimated_time: Optional[str] = Field(None, description="Estimated time to complete this node")


class RoadmapQuery(BaseModel):
    """Input query for roadmap generation."""
    query: str = Field(..., description="Career or learning goal query", min_length=5)


class RoadmapResponse(BaseModel):
    """Response containing the generated roadmap."""
    query: str = Field(..., description="Original query")
    title: str = Field(..., description="Roadmap title")
    description: str = Field(..., description="Roadmap overview")
    nodes: List[RoadmapNode] = Field(..., description="All nodes in the roadmap")
    total_time: Optional[str] = Field(None, description="Total estimated time")
    generated_at: str = Field(..., description="Generation timestamp")


class ExportRequest(BaseModel):
    """Request to export roadmap as HTML."""
    roadmap: RoadmapResponse = Field(..., description="Roadmap data to export")
    include_styles: bool = Field(True, description="Include embedded styles")
