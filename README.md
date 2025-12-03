# CareerGraph - AI-Powered Career Roadmap Generator

CareerGraph is a sophisticated multi-agent AI application that generates interactive, hierarchical career roadmaps with curated learning resources. Built with FastAPI, LangGraph, and OpenAI's GPT-4.

## ✨ Features

- **Real-Time Web Search** (NEW! 🔥):
  - Live search for current YouTube tutorials (2025)
  - Active online courses from Coursera, Udemy, edX
  - Up-to-date official documentation
  - Validated, accessible URLs
  - No hallucinated or outdated resources

- **Multi-Agent AI System**: Three specialized agents work together:
  - **Validation Agent**: Ensures queries are career/education-related
  - **Research Agent**: Uses web search to find real resources
  - **Structure Agent**: Creates hierarchical roadmap structure

- **Interactive Visualization**: 
  - Cytoscape.js-powered graph visualization
  - Hierarchical layout with expandable nodes
  - Color-coded by level (root, topics, subtopics, units)
  - Click nodes to view detailed resources

- **Curated Resources**:
  - YouTube tutorials and courses
  - Documentation and guides
  - Online courses (Coursera, edX, Udemy)
  - Source attribution (YouTube, Official Docs, etc.)
  - 5-7 verified resources per topic

- **Export Functionality**:
  - Download as standalone HTML file
  - Fully functional offline
  - Maintains all interactivity

- **Modern UI**:
  - Dark theme with glassmorphism
  - Smooth animations and transitions
  - Responsive design
  - Real-time agent progress indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (required)
- Serper API key (optional, for web search - see [SERPER_SETUP.md](file:///home/vedant/Desktop/testing_gravity/SERPER_SETUP.md))

### Installation

1. **Clone or navigate to the project directory**:
```bash
cd /home/vedant/Desktop/testing_gravity
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Optional: Enable web search for current resources
SERPER_API_KEY=your_serper_api_key_here
SEARCH_ENABLED=true
```

See [SERPER_SETUP.md](file:///home/vedant/Desktop/testing_gravity/SERPER_SETUP.md) for web search setup.

### Running the Application

1. **Start the server**:
```bash
uvicorn careergraph.main:app --reload
```

Or from within the virtual environment:
```bash
./venv/bin/python -m uvicorn careergraph.main:app --reload
```

2. **Open your browser**:
Navigate to `http://localhost:8000`

3. **Generate a roadmap**:
- Enter a career query (e.g., "How to become a CA in India")
- Watch the AI agents work
- Explore the interactive roadmap
- Export as HTML for offline use

## 📁 Project Structure

```
careergraph/
├── careergraph/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── agents/
│   │   ├── __init__.py
│   │   └── graph.py         # LangGraph multi-agent orchestration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── utils/
│   │   ├── __init__.py
│   │   └── export.py        # HTML export functionality
│   └── static/
│       ├── index.html       # Main UI
│       ├── styles.css       # Modern styling
│       └── graph.js         # Cytoscape visualization
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 API Endpoints

### `POST /api/generate-roadmap`
Generate a career roadmap from a query.

**Request**:
```json
{
  "query": "How to become a CA in India"
}
```

**Response**:
```json
{
  "query": "How to become a CA in India",
  "title": "Chartered Accountant Career Roadmap",
  "description": "Complete path to becoming a CA in India",
  "nodes": [...],
  "total_time": "3-4 years",
  "generated_at": "2025-12-03T20:00:00"
}
```

### `POST /api/export-roadmap`
Export roadmap as standalone HTML file.

**Request**:
```json
{
  "roadmap": {...},
  "include_styles": true
}
```

**Response**: HTML file download

### `GET /health`
Health check endpoint.

## 🎨 Usage Examples

### Career Paths
- "How to become a CA in India"
- "Roadmap for AI Engineer"
- "Path to becoming a Data Scientist"
- "How to become a Full Stack Developer"

### Learning Goals
- "How to learn thermodynamics in physics"
- "Master machine learning from scratch"
- "Learn cloud computing with AWS"

### Skills
- "Become proficient in React.js"
- "Learn DevOps practices"
- "Master digital marketing"

## 🧠 How It Works

1. **Query Validation**: The validation agent checks if the query is career/education-related
2. **Research Phase**: The research agent identifies key topics and gathers resources
3. **Structure Phase**: The structure agent creates a hierarchical roadmap with prerequisites
4. **Visualization**: Frontend renders an interactive Cytoscape.js graph
5. **Export**: Generate standalone HTML with all data and functionality embedded

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Multi-Agent**: LangGraph
- **LLM**: OpenAI GPT-4
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: Cytoscape.js
- **Styling**: Custom CSS with glassmorphism

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4-turbo-preview)

### Customization

- **Agent Prompts**: Modify prompts in `careergraph/agents/graph.py`
- **UI Theme**: Update colors in `careergraph/static/styles.css`
- **Graph Layout**: Adjust Cytoscape settings in `careergraph/static/graph.js`

## 📝 Notes

- **Response Time**: Expect 30-60 seconds per query due to multi-agent processing
- **API Costs**: Using GPT-4 incurs OpenAI API costs based on usage
- **Query Quality**: More specific queries yield better roadmaps

## 🐛 Troubleshooting

### Server won't start
- Ensure virtual environment is activated
- Check that all dependencies are installed
- Verify `.env` file exists with valid API key

### Roadmap generation fails
- Verify OpenAI API key is valid
- Check internet connection
- Ensure query is career/education-related

### Graph not displaying
- Check browser console for JavaScript errors
- Ensure Cytoscape.js CDN is accessible
- Try clearing browser cache

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify for your needs.

## 📧 Support

For issues or questions, please refer to the implementation documentation.

---

Built with ❤️ using LangGraph and OpenAI
