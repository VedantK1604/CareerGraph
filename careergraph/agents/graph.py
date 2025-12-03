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
    """Research and gather learning resources for the query using web search."""
    llm = create_llm()
    search_enabled = os.getenv("SEARCH_ENABLED", "true").lower() == "true"
    
    # Step 1: Use LLM to identify topics and structure
    structure_prompt = f"""You are a research agent. Identify the main topics and subtopics needed to achieve this goal.

Query: {state['query']}

Respond with a JSON object containing topics to research:
{{
    "topics": [
        {{
            "title": "Topic Name",
            "description": "Brief description",
            "search_keywords": ["keyword1", "keyword2"],
            "subtopics": [
                {{
                    "title": "Subtopic Name",
                    "description": "Brief description",
                    "search_keywords": ["keyword1", "keyword2"]
                }}
            ]
        }}
    ]
}}

Focus on current, practical topics. Include trending technologies for 2025."""

    response = llm.invoke([HumanMessage(content=structure_prompt)])
    
    try:
        json_text = extract_json(response.content)
        topics_structure = json.loads(json_text)
        
        # Step 2: If search enabled, find real resources
        if search_enabled:
            print(f"🔍 Web search ENABLED - Using Serper API")
            from careergraph.utils.search import SerperSearchTool
            search_tool = SerperSearchTool()
            
            # Enhance each topic with real web search results
            for topic in topics_structure.get("topics", []):
                topic_resources = []
                
                print(f"  📚 Searching for: {topic['title']}")
                
                # Search for videos
                videos = search_tool.search_youtube(topic["title"], max_results=2)
                print(f"    ✓ Found {len(videos)} YouTube videos")
                topic_resources.extend(videos)
                
                # Search for courses
                courses = search_tool.search_courses(topic["title"], max_results=2)
                print(f"    ✓ Found {len(courses)} courses")
                topic_resources.extend(courses)
                
                # Search for documentation
                docs = search_tool.search_documentation(topic["title"], max_results=1)
                print(f"    ✓ Found {len(docs)} documentation")
                topic_resources.extend(docs)
                
                # Add resources to subtopics
                for subtopic in topic.get("subtopics", []):
                    subtopic_query = f"{topic['title']} {subtopic['title']}"
                    
                    # Fewer resources for subtopics
                    sub_videos = search_tool.search_youtube(subtopic_query, max_results=1)
                    sub_courses = search_tool.search_courses(subtopic_query, max_results=1)
                    
                    subtopic["resources"] = sub_videos + sub_courses
                    print(f"      - {subtopic['title']}: {len(subtopic['resources'])} resources")
                
                # Attach main topic resources
                topic["resources"] = topic_resources
                print(f"  Total resources for '{topic['title']}': {len(topic_resources)}")
        else:
            print(f"⚠️  Web search DISABLED - Using LLM fallback")
            # Fallback: Use LLM to suggest resources (old behavior)
            for topic in topics_structure.get("topics", []):
                for subtopic in topic.get("subtopics", []):
                    # Add placeholder resources
                    subtopic["resources"] = [
                        {
                            "title": f"Learn {subtopic['title']}",
                            "url": "https://example.com",
                            "type": "course",
                            "description": f"Comprehensive guide to {subtopic['title']}",
                            "source": "LLM Suggestion"
                        }
                    ]
        
        print(f"✅ Research complete. Total topics: {len(topics_structure.get('topics', []))}")
        state["research_data"] = [topics_structure]
        state["current_agent"] = "research"
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ Research error: {str(e)}")
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

IMPORTANT: The research data contains real resources (YouTube videos, courses, documentation) that you MUST include in the roadmap nodes.

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
            "resources": [
                {{
                    "title": "Resource Title",
                    "url": "https://actual-url.com",
                    "type": "video|documentation|course",
                    "description": "Brief description",
                    "source": "YouTube|Coursera|Official Docs",
                    "duration": "time if known"
                }}
            ],
            "prerequisites": [],
            "estimated_time": "time estimate"
        }}
    ]
}}

CRITICAL INSTRUCTIONS:
1. Create a clear hierarchy with proper parent_id relationships
2. **COPY ALL RESOURCES from the research data topics/subtopics to the corresponding roadmap nodes**
3. Match topics from research data to roadmap nodes and include their resources
4. Do NOT leave resources arrays empty if research data has resources for that topic
5. Define prerequisites where applicable
6. Provide realistic time estimates
7. Make IDs descriptive (e.g., "fundamentals-python", "advanced-ml")

Example: If research data has a topic "HTML Basics" with 5 resources, the roadmap node for "HTML Basics" should include all 5 resources."""

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
