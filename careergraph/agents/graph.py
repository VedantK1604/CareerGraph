"""LangGraph multi-agent orchestration for roadmap generation."""
import os
import re
from typing import TypedDict, List, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import operator
import json

from careergraph.models.schemas import RoadmapNode, Resource


def extract_json(text: str) -> str:
    """Extract JSON from markdown code blocks or plain text."""
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find JSON object directly
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text


class AgentState(TypedDict):
    """Shared state across all agents."""
    query: str
    is_valid: bool
    validation_message: str
    research_data: Annotated[List[dict], operator.add]
    roadmap_structure: dict
    nodes: List[RoadmapNode]
    current_agent: str
    error: str


def create_llm():
    """Create OpenAI LLM instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    return ChatOpenAI(
        model=model,
        temperature=0.7,
        api_key=api_key
    )


def validation_agent(state: AgentState) -> AgentState:
    """Validate if query is career/education related."""
    llm = create_llm()
    
    prompt = f"""You are a validation agent. Determine if the following query is related to career development, education, or learning.
    
Query: {state['query']}

Respond with a JSON object:
{{
    "is_valid": true/false,
    "message": "explanation of why it is or isn't valid"
}}

Only accept queries about:
- Career paths and roadmaps
- Educational goals and learning paths
- Skill development
- Professional certifications

Reject queries about:
- General knowledge questions
- Non-educational topics
- Entertainment
- Personal advice unrelated to career/education"""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        json_text = extract_json(response.content)
        result = json.loads(json_text)
        state["is_valid"] = result.get("is_valid", False)
        state["validation_message"] = result.get("message", "")
        state["current_agent"] = "validation"
    except (json.JSONDecodeError, Exception) as e:
        state["is_valid"] = False
        state["validation_message"] = f"Failed to validate query: {str(e)}"
        state["error"] = f"Validation parsing error: {response.content[:200]}"
    
    return state


def research_agent(state: AgentState) -> AgentState:
    """Research and gather learning resources for the query."""
    llm = create_llm()
    
    prompt = f"""You are a research agent specializing in finding educational resources.
    
Query: {state['query']}

Your task is to identify the main topics and subtopics that someone would need to learn to achieve this goal.
For each topic, suggest 3-5 high-quality learning resources.

Respond with a JSON object containing an array of topics:
{{
    "topics": [
        {{
            "title": "Topic Name",
            "description": "Brief description",
            "subtopics": [
                {{
                    "title": "Subtopic Name",
                    "description": "Brief description",
                    "resources": [
                        {{
                            "title": "Resource Title",
                            "url": "https://example.com",
                            "type": "video|documentation|course|book|paper",
                            "description": "What this resource covers",
                            "duration": "estimated time"
                        }}
                    ]
                }}
            ]
        }}
    ]
}}

Focus on:
- YouTube educational channels and tutorials
- Official documentation and guides
- Online courses (Coursera, edX, Udemy)
- Highly-rated books
- Research papers (if applicable)

Be specific and provide realistic, high-quality resources."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        json_text = extract_json(response.content)
        result = json.loads(json_text)
        state["research_data"] = [result]
        state["current_agent"] = "research"
    except (json.JSONDecodeError, Exception) as e:
        state["research_data"] = []
        state["error"] = f"Research parsing error: {str(e)}"
    
    return state


def structure_agent(state: AgentState) -> AgentState:
    """Structure the research data into a hierarchical roadmap."""
    llm = create_llm()
    
    research_summary = json.dumps(state.get("research_data", []), indent=2)
    
    prompt = f"""You are a structure agent. Create a hierarchical learning roadmap from the research data.

Query: {state['query']}
Research Data:
{research_summary}

Create a complete roadmap with nodes at different levels:
- Level 0: Root node (the overall goal)
- Level 1: Main topics/phases
- Level 2: Subtopics within each main topic
- Level 3: Individual learning units

Respond with a JSON object:
{{
    "title": "Roadmap Title",
    "description": "Overview of the learning path",
    "total_time": "Estimated total time",
    "nodes": [
        {{
            "id": "unique-id",
            "title": "Node title",
            "description": "Node description",
            "level": 0,
            "parent_id": null,
            "resources": [],
            "prerequisites": [],
            "estimated_time": "time estimate"
        }}
    ]
}}

Ensure:
1. Create a clear hierarchy with proper parent_id relationships
2. Assign appropriate resources to each node from the research data
3. Define prerequisites where applicable
4. Provide realistic time estimates
5. Make IDs descriptive (e.g., "fundamentals-python", "advanced-ml")"""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        json_text = extract_json(response.content)
        result = json.loads(json_text)
        state["roadmap_structure"] = result
        
        # Convert to RoadmapNode objects
        nodes = []
        for node_data in result.get("nodes", []):
            node = RoadmapNode(
                id=node_data["id"],
                title=node_data["title"],
                description=node_data["description"],
                level=node_data["level"],
                parent_id=node_data.get("parent_id"),
                resources=[Resource(**r) for r in node_data.get("resources", [])],
                prerequisites=node_data.get("prerequisites", []),
                estimated_time=node_data.get("estimated_time")
            )
            nodes.append(node)
        
        state["nodes"] = nodes
        state["current_agent"] = "structure"
    except (json.JSONDecodeError, Exception) as e:
        state["nodes"] = []
        state["error"] = f"Structure parsing error: {str(e)}"
    
    return state


def should_continue(state: AgentState) -> str:
    """Determine which agent to call next."""
    if state.get("error"):
        return "end"
    
    current = state.get("current_agent", "")
    
    if current == "":
        return "validation"
    elif current == "validation":
        if not state.get("is_valid", False):
            return "end"
        return "research"
    elif current == "research":
        return "structure"
    elif current == "structure":
        return "end"
    
    return "end"


def create_roadmap_graph():
    """Create the LangGraph workflow for roadmap generation."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validation", validation_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("structure", structure_agent)
    
    # Set entry point
    workflow.set_entry_point("validation")
    
    # Add edges
    workflow.add_conditional_edges(
        "validation",
        should_continue,
        {
            "research": "research",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "research",
        should_continue,
        {
            "structure": "structure",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "structure",
        should_continue,
        {
            "end": END
        }
    )
    
    return workflow.compile()


async def generate_roadmap(query: str) -> dict:
    """Generate a roadmap for the given query."""
    graph = create_roadmap_graph()
    
    initial_state: AgentState = {
        "query": query,
        "is_valid": False,
        "validation_message": "",
        "research_data": [],
        "roadmap_structure": {},
        "nodes": [],
        "current_agent": "",
        "error": ""
    }
    
    # Run the graph
    final_state = await graph.ainvoke(initial_state)
    
    return final_state
