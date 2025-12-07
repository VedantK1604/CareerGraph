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
    
    # Step 1: Use LLM to identify topics with detailed hierarchical structure
    structure_prompt = f"""You are a research agent. Create a comprehensive, detailed learning roadmap structure for this goal.

Query: {state['query']}

Generate a DETAILED hierarchical structure with:
- Main Topics (8-12 major areas)
- Subtopics (3-5 subtopics per main topic)
- Learning Units (2-4 specific units per subtopic)

Respond with a JSON object:
{{
    "topics": [
        {{
            "title": "Topic Name (Context)",
            "description": "What this topic covers and why it's important",
            "search_keywords": ["keyword1", "keyword2"],
            "subtopics": [
                {{
                    "title": "Subtopic Name",
                    "description": "Brief description",
                    "search_keywords": ["keyword1", "keyword2"],
                    "units": [
                        "Specific Unit 1",
                        "Specific Unit 2",
                        "Specific Unit 3"
                    ]
                }}
            ]
        }}
    ]
}}

IMPORTANT:
1. Create 8-12 main topics for comprehensive coverage
2. Each main topic should have 3-5 detailed subtopics
3. Each subtopic should break down into 2-4 specific learning units
4. Include current/trending technologies for 2025
5. Order topics from fundamentals to advanced

Example structure for "AI Engineer":
- Topic 1: "Basics of Programming (Python)" with subtopics: "Python Basics", "Intermediate Python", "Advanced Python"
  - Python Basics units: "Variables, Data Types, Operators", "If-else, Loops", "Functions", "Modules"
- Topic 2: "Mathematics for AI" with subtopics: "Linear Algebra", "Probability & Statistics", "Calculus Basics"
- ... and so on for 8-12 total topics"""

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
                books = []
                
                print(f"  📚 Searching for: {topic['title']}")
                
                # Search for MORE resources at the topic level
                # Videos - increase from 2 to 3-4
                videos = search_tool.search_youtube(topic["title"], max_results=4)
                print(f"    ✓ Found {len(videos)} YouTube videos")
                topic_resources.extend(videos)
                
                # Courses - increase from 2 to 3
                courses = search_tool.search_courses(topic["title"], max_results=3)
                print(f"    ✓ Found {len(courses)} courses")
                topic_resources.extend(courses)
                
                # Documentation
                docs = search_tool.search_documentation(topic["title"], max_results=2)
                print(f"    ✓ Found {len(docs)} documentation")
                topic_resources.extend(docs)
                
                # NEW: Search for books
                books = search_tool.search_books(topic["title"], max_results=3)
                print(f"    ✓ Found {len(books)} books")
                
                # Add resources to subtopics
                for subtopic in topic.get("subtopics", []):
                    subtopic_query = f"{topic['title']} {subtopic['title']}"
                    
                    # Resources for subtopics
                    sub_videos = search_tool.search_youtube(subtopic_query, max_results=2)
                    sub_courses = search_tool.search_courses(subtopic_query, max_results=1)
                    sub_docs = search_tool.search_documentation(subtopic_query, max_results=1)
                    
                    subtopic["resources"] = sub_videos + sub_courses + sub_docs
                    print(f"      - {subtopic['title']}: {len(subtopic['resources'])} resources")
                
                # Attach main topic resources and books
                topic["resources"] = topic_resources
                topic["books"] = books
                print(f"  Total for '{topic['title']}': {len(topic_resources)} resources + {len(books)} books")
        else:
            print(f"⚠️  Web search DISABLED - Using LLM fallback")
            # Fallback: Use LLM to suggest resources (old behavior)
            for topic in topics_structure.get("topics", []):
                topic["resources"] = []
                topic["books"] = []
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
    
    prompt = f"""You are a structure agent. Create a detailed hierarchical learning roadmap from the research data.

Query: {state['query']}
Research Data:
{research_summary}

IMPORTANT: The research data contains:
- Real resources (YouTube videos, courses, documentation) from web search
- Book recommendations  
- Detailed hierarchical structure with topics, subtopics, and learning units
- You MUST include ALL of this information in the roadmap

Create a complete roadmap with nodes at ALL levels:
- Level 0: Root node (the overall career goal)
- Level 1: Main topics/phases (e.g., "Basics of Programming (Python)")
- Level 2: Subtopics within each main topic (e.g., "Python Basics", "Intermediate Python")
- Level 3: Individual learning units (e.g., "Variables, Data Types, Operators")

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
                    "type": "video|documentation|course|book",
                    "description": "Brief description",
                    "source": "YouTube|Coursera|Official Docs|Book",
                    "duration": "time if known"
                }}
            ],
            "prerequisites": [],
            "estimated_time": "time estimate"
        }}
    ]
}}

CRITICAL INSTRUCTIONS:
1. Create nodes for ALL hierarchy levels:
   - 1 root node (level 0)
   - All main topics from research as level 1 nodes
   - All subtopics as level 2 nodes (parent_id = main topic id)
   - All learning units as level 3 nodes (parent_id = subtopic id)

2. Resource distribution:
   - Level 0 (root): No resources
   - Level 1 (main topics): Include ALL resources AND books from research data
   - Level 2 (subtopics): Include resources from research data
   - Level 3 (units): Can be lightweight with minimal or no resources

3. **COPY ALL RESOURCES from research data**:
   - Main topics should include their "resources" array AND "books" array
   - Subtopics should include their "resources" array
   - Do NOT leave resource arrays empty if research data has them

4. Use descriptive IDs: "root", "topic-python", "python-basics", "python-basics-variables"

5. Set proper parent-child relationships with parent_id

6. Define prerequisites where applicable (e.g., Python before Machine Learning)

7. Provide realistic time estimates for each node

Example node hierarchy for "AI Engineer":
- root (level 0)
  - topic-python (level 1, parent: root) - with video/course/doc/book resources
    - python-basics (level 2, parent: topic-python) - with video/course resources
      - python-basics-variables (level 3, parent: python-basics)
      - python-basics-loops (level 3, parent: python-basics)
    - python-intermediate (level 2, parent: topic-python)
      - python-oop (level 3, parent: python-intermediate)
  - topic-mathematics (level 1, parent: root) - with video/course/doc/book resources
    ...and so on

**Match the research data structure exactly** - if research has 10 topics with 3-5 subtopics each, create nodes for all of them."""

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
        
        # Log statistics for better observability
        print(f"📊 Roadmap structure created:")
        print(f"   Total nodes: {len(nodes)}")
        print(f"   Level 0 (root): {len([n for n in nodes if n.level == 0])}")
        print(f"   Level 1 (topics): {len([n for n in nodes if n.level == 1])}")
        print(f"   Level 2 (subtopics): {len([n for n in nodes if n.level == 2])}")
        print(f"   Level 3 (units): {len([n for n in nodes if n.level == 3])}")
        
        total_resources = sum(len(n.resources) for n in nodes)
        print(f"   Total resources: {total_resources}")
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
