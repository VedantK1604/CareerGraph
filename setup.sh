#!/bin/bash

# CareerGraph Setup Script

echo "🚀 Setting up CareerGraph..."
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key!"
    echo ""
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment is not activated!"
    echo "Please run: source venv/bin/activate"
    echo ""
else
    echo "✅ Virtual environment is activated"
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python -c "import fastapi, uvicorn, langgraph, langchain" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Dependencies are installed"
else
    echo "⚠️  Dependencies not fully installed"
    echo "Run: pip install -r requirements.txt"
    echo ""
fi

echo ""
echo "📋 Next Steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Run: uvicorn careergraph.main:app --reload"
echo "3. Open: http://localhost:8000"
echo ""
echo "🎉 Setup complete! Happy roadmapping!"
