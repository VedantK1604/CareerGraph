# CareerGraph System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Browser - localhost:8000)                   │
└────────────────┬────────────────────────────────┬───────────────┘
                 │                                │
                 │ HTTP Request                   │ WebSocket (future)
                 │                                │
┌────────────────▼────────────────────────────────▼───────────────┐
│                      FASTAPI SERVER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                           │  │
│  │  • POST /api/generate-roadmap                            │  │
│  │  • POST /api/export-roadmap                              │  │
│  │  • GET  /health                                          │  │
│  │  • GET  / (static files)                                 │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │          PYDANTIC MODELS (Validation Layer)              │  │
│  │  • RoadmapQuery  • RoadmapNode  • RoadmapResponse       │  │
│  │  • Resource      • ExportRequest                         │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ Invoke Graph
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATION                      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    AGENT STATE                            │ │
│  │  • query             • validation_message                 │ │
│  │  • is_valid          • research_data                      │ │
│  │  • roadmap_structure • nodes                              │ │
│  │  • current_agent     • error                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────┐      ┌──────────────┐      ┌───────────────┐  │
│  │ VALIDATION │      │   RESEARCH   │      │   STRUCTURE   │  │
│  │   AGENT    │─────▶│    AGENT     │─────▶│     AGENT     │  │
│  │            │      │              │      │               │  │
│  │ • Validate │      │ • Find topics│      │ • Create      │  │
│  │   query    │      │ • Gather     │      │   hierarchy   │  │
│  │ • Ensure   │      │   resources  │      │ • Assign      │  │
│  │   career   │      │ • Categorize │      │   resources   │  │
│  │   related  │      │   by type    │      │ • Define      │  │
│  │            │      │              │      │   prereqs     │  │
│  └─────┬──────┘      └──────┬───────┘      └───────┬───────┘  │
│        │                    │                      │           │
│        └────────────────────┼──────────────────────┘           │
│                             │                                  │
│                    All agents use                              │
│                             │                                  │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              │ LLM Calls
                              │
                   ┌──────────▼──────────┐
                   │   OPENAI GPT-4      │
                   │                     │
                   │  • Parse queries    │
                   │  • Generate topics  │
                   │  • Find resources   │
                   │  • Structure data   │
                   └─────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND COMPONENTS                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  index.html  │  │  styles.css  │  │    graph.js        │   │
│  │              │  │              │  │                    │   │
│  │ • Hero       │  │ • Dark theme │  │ • Cytoscape.js     │   │
│  │ • Input form │  │ • Glassmorp. │  │ • Graph rendering  │   │
│  │ • Loading UI │  │ • Animations │  │ • Node clicks      │   │
│  │ • Graph div  │  │ • Responsive │  │ • Export handler   │   │
│  │ • Node panel │  │              │  │                    │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      EXPORT UTILITY                             │
│                                                                 │
│  generate_html_export()                                         │
│  • Embeds roadmap JSON                                          │
│  • Includes all CSS/JS                                          │
│  • Self-contained HTML                                          │
│  • Offline functionality                                        │
└─────────────────────────────────────────────────────────────────┘

DATA FLOW:
1. User enters query in browser
2. Frontend sends POST to /api/generate-roadmap
3. FastAPI validates with Pydantic
4. Graph orchestrator creates initial state
5. Validation agent checks query validity
6. Research agent gathers topics & resources
7. Structure agent builds hierarchical roadmap
8. Response sent back to frontend as JSON
9. Cytoscape.js renders interactive graph
10. User clicks nodes to view resources
11. Optional: Export to standalone HTML

TECHNOLOGY CHOICES:
• FastAPI     → Modern, async Python web framework
• LangGraph   → Multi-agent state management
• OpenAI      → Powerful LLM for research & structuring
• Cytoscape   → Best-in-class graph visualization
• Pydantic    → Runtime type validation
• Vanilla JS  → No build step, simple deployment
```

## Key Design Patterns

### 1. Multi-Agent Orchestration
- **Pattern**: Sequential pipeline with conditional routing
- **State**: Shared TypedDict passed between agents
- **Benefits**: Clear separation of concerns, easy to extend

### 2. Async API Design
- **Pattern**: Async/await throughout
- **Benefits**: Non-blocking LLM calls, better concurrency
- **Trade-off**: More complex but worth it for I/O operations

### 3. Component-Based Frontend
- **Pattern**: Vanilla JS with separated concerns
- **Files**: HTML (structure), CSS (style), JS (behavior)
- **Benefits**: No build step, easy to understand

### 4. Graph-First Data Model
- **Pattern**: Hierarchical nodes with parent/child relationships
- **Structure**: Level 0 (root) → Level 1-3 (topics/subtopics/units)
- **Benefits**: Natural tree representation, easy to visualize

### 5. Embedded Export
- **Pattern**: Self-contained HTML with inline data
- **Technique**: JSON embedded in script tag
- **Benefits**: Single-file distribution, offline capable

## Scale Considerations

### Current Limitations
- Single-server deployment
- Synchronous LLM calls per request
- No caching layer
- In-memory state only

### Future Scalability
- Add Redis for caching common roadmaps
- Implement request queuing for high load
- Use streaming responses for progress updates
- Add database for user roadmaps
- Deploy with Docker/Kubernetes
- Use CDN for static assets
