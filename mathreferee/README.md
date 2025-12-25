# MathReferee

An autonomous AI referee system for mathematical and statistical papers using Gemini Pro.

## Features

- **Agentic AI System**: Fully autonomous paper review with multi-step reasoning
- **Tool Usage**: Integrates arXiv, literature search, symbolic math, and statistical analysis
- **Epistemic Tracking**: Tracks confidence and uncertainty for all claims
- **Self-Critique**: Multi-level critique of reasoning and findings
- **Adaptive Planning**: Dynamically adjusts review strategy based on findings

## Architecture

```
mathreferee/
├── app/
│   ├── agent/          # Agent components
│   │   ├── referee_agent.py    # Main orchestrator
│   │   ├── planner.py          # Review planning
│   │   ├── critic.py           # Self-critique
│   │   └── synthesizer.py      # Result synthesis
│   ├── tools/          # External tools
│   │   ├── arxiv.py           # arXiv integration
│   │   ├── literature.py      # Literature search
│   │   ├── symbolic.py        # Symbolic math
│   │   └── stats.py           # Statistical analysis
│   ├── models/         # Data models
│   │   └── review_models.py   # Pydantic models
│   ├── core/           # Core utilities
│   │   ├── gemini.py          # Gemini API client
│   │   └── state.py           # State management
│   └── api/            # API routes
│       └── routes.py          # FastAPI endpoints
├── frontend/
│   └── app.py          # Streamlit UI
├── requirements.txt
└── README.md
```

## Installation

1. **Clone the repository**
```bash
cd mathreferee
```

2. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

## Usage

### Start the API Server

```bash
python -m uvicorn app.api.routes:app --reload
```

The API will be available at `http://localhost:8000`

### Start the Frontend

In a new terminal:

```bash
streamlit run frontend/app.py
```

The UI will open at `http://localhost:8501`

### API Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /review/arxiv/{arxiv_id}` - Review an arXiv paper
- `POST /papers/submit` - Submit a custom paper
- `GET /tools` - List available tools

### Example: Review an arXiv Paper

```python
import requests

response = requests.post(
    "http://localhost:8000/review/arxiv/2301.12345",
    params={"verbose": True}
)

review = response.json()
print(f"Recommendation: {review['recommendation']}")
print(f"Confidence: {review['confidence']}")
```

## Components

### RefereeAgent
Main orchestrator that coordinates the entire review process.

### Planner
Creates structured review plans and adapts them based on findings.

### Critic
Performs self-critique at multiple levels:
- Individual claims
- Reasoning steps
- Overall review coherence

### Synthesizer
Combines findings into coherent section summaries and final reviews.

### Tools

1. **ArxivTool**: Search and retrieve papers from arXiv
2. **LiteratureTool**: Search academic literature via Semantic Scholar
3. **SymbolicMathTool**: Symbolic computation with SymPy
4. **StatisticalTool**: Statistical analysis with SciPy/statsmodels

## Models

All data structures use Pydantic v2 for validation:

- `Paper`: Paper metadata and content
- `Review`: Complete review with sections and recommendations
- `Claim`: Mathematical/statistical claims with epistemic state
- `ReasoningStep`: Individual reasoning steps with tool calls
- `Critique`: Self-critiques with severity levels
- `EpistemicState`: Confidence and uncertainty tracking

## Development

### Running Tests

```bash
pytest
```

### Code Structure

- All components are fully functional (no placeholders)
- Async/await throughout for performance
- Type hints for clarity
- Comprehensive error handling

## Requirements

- Python 3.11+
- Google API key for Gemini Pro
- Internet connection for arXiv and literature search

## License

MIT License

## Contributing

Contributions welcome! Please ensure:
- No placeholder code
- All functions are testable
- Type hints included
- Documentation updated
