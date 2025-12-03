# CareerGraph - Quick Reference

## 🚀 Getting Started (First Time)

```bash
# 1. Navigate to project
cd /home/vedant/Desktop/testing_gravity

# 2. Activate virtual environment
source venv/bin/activate

# 3. Create .env file
cp .env.example .env

# 4. Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
# Add: OPENAI_API_KEY=sk-your-actual-key-here

# 5. Start the server
uvicorn careergraph.main:app --reload

# 6. Open browser
# Navigate to: http://localhost:8000
```

## 🔄 Running (After Setup)

```bash
cd /home/vedant/Desktop/testing_gravity
source venv/bin/activate
uvicorn careergraph.main:app --reload
```

## 📝 Example Queries

### Career Paths
- How to become a CA in India
- Roadmap for AI Engineer
- Path to becoming a Data Scientist
- How to become a Full Stack Developer
- Become a Cloud Architect

### Learning Goals
- How to learn thermodynamics in physics
- Master machine learning from scratch
- Learn cloud computing with AWS
- Become proficient in React.js

### Skills Development
- Master DevOps practices
- Learn digital marketing
- Become a cybersecurity expert

## 🔧 Troubleshooting

### Server won't start
```bash
# Check if virtual env is activated
echo $VIRTUAL_ENV

# If not, activate it
source venv/bin/activate

# Verify dependencies
pip list | grep -E "fastapi|langgraph|langchain"
```

### "OpenAI API key not set"
```bash
# Check .env file exists
ls -la .env

# Verify it contains your key
cat .env | grep OPENAI_API_KEY

# If missing, add it
echo "OPENAI_API_KEY=your-key-here" > .env
```

### Graph not displaying
- Check browser console (F12)
- Verify internet connection (Cytoscape.js loads from CDN)
- Try different browser
- Clear cache and reload

## 📊 Project Structure

```
testing_gravity/
├── careergraph/           # Main application package
│   ├── main.py           # FastAPI app & API endpoints
│   ├── agents/
│   │   └── graph.py      # Multi-agent orchestration
│   ├── models/
│   │   └── schemas.py    # Data models
│   ├── utils/
│   │   └── export.py     # HTML export
│   └── static/           # Frontend files
│       ├── index.html    # UI
│       ├── styles.css    # Styling
│       └── graph.js      # Visualization
├── venv/                 # Virtual environment
├── requirements.txt      # Dependencies
├── .env                  # Your configuration (SECRET!)
└── README.md            # Documentation
```

## 🎯 Key Features

✨ **3-Agent System**: Validation → Research → Structure  
🎨 **Modern UI**: Dark theme with glassmorphism  
📊 **Interactive Graph**: Cytoscape.js visualization  
💾 **Export**: Standalone HTML files  
⚡ **Fast API**: Async FastAPI backend  

## ⚙️ Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-4, gpt-3.5-turbo
```

### Change Port
```bash
uvicorn careergraph.main:app --reload --port 8080
```

### Production Mode
```bash
uvicorn careergraph.main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

- `POST /api/generate-roadmap` - Generate roadmap
- `POST /api/export-roadmap` - Export as HTML
- `GET /health` - Health check
- `GET /` - Main application UI

## 💡 Tips

1. **More specific queries** = Better roadmaps
2. Expected response time: **30-60 seconds**
3. Each query costs ~$0.10-0.30 in API fees
4. Export roadmaps to share offline
5. Click nodes to see detailed resources
6. Double-click nodes to focus on them

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Activate venv: `source venv/bin/activate` |
| Port already in use | Use different port: `--port 8080` |
| API key error | Check `.env` file has valid key |
| Slow generation | Normal for GPT-4 (30-60s) |
| Graph not interactive | Check browser console for errors |

## 📚 Documentation

- README.md - Full documentation
- walkthrough.md - Implementation details
- .env.example - Configuration template

---

**Need more help?** Check the comprehensive [README.md](file:///home/vedant/Desktop/testing_gravity/README.md)
