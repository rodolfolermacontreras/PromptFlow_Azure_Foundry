# Outlander Gear Co. AI Copilot - Udacity Azure AI Project 2

> **Code-first RAG implementation using Azure AI Search, Azure OpenAI GPT-4o, and Prompt Flow**

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Testing the Copilot](#testing-the-copilot)
- [Evaluation](#evaluation)
- [Using VS Code Prompt Flow Extension](#using-vs-code-prompt-flow-extension)
- [Deployment](#deployment)
- [Udacity Submission Checklist](#udacity-submission-checklist)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** AI assistant for Outlander Gear Co., a fictional outdoor equipment retailer. The copilot helps customers find products, answer questions about specifications, pricing, and features using natural language.

### Key Features
- ✅ **Hybrid Search**: Vector + keyword search for optimal product retrieval
- ✅ **GPT-4o Integration**: Latest Azure OpenAI model for natural language generation
- ✅ **Prompt Flow**: Visual orchestration with VS Code extension support
- ✅ **100% Evaluation Success**: 13/13 test questions passed
- ✅ **Code-First Approach**: Complete Azure automation with Python

### Technologies Used
- **Azure AI Search**: Product indexing with vector embeddings
- **Azure OpenAI GPT-4o**: Response generation
- **Azure OpenAI Embeddings**: text-embedding-ada-002 (1536 dimensions)
- **Prompt Flow**: Orchestration and deployment
- **Python 3.12**: Core implementation language

---

## 🏗️ Architecture

### System Architecture

```
┌──────────────────┐
│  User Question   │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│           PROMPT FLOW PIPELINE             │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────┐         │
│  │  NODE 1: search_products     │         │
│  ├──────────────────────────────┤         │
│  │ 1. Generate query embedding  │         │
│  │    (text-embedding-ada-002)  │         │
│  │ 2. Hybrid search:            │         │
│  │    - Vector similarity       │         │
│  │    - Keyword (BM25)          │         │
│  │ 3. Return top 3 products     │         │
│  └──────────┬───────────────────┘         │
│             │ context                     │
│             ▼                              │
│  ┌──────────────────────────────┐         │
│  │  NODE 2: generate_response   │         │
│  ├──────────────────────────────┤         │
│  │ 1. Build system prompt       │         │
│  │ 2. Inject product context    │         │
│  │ 3. Call GPT-4o               │         │
│  │ 4. Generate answer           │         │
│  └──────────┬───────────────────┘         │
│             │                              │
└─────────────┼──────────────────────────────┘
              │
              ▼
      ┌───────────────┐
      │  AI Response  │
      └───────────────┘
```

### Flow Configuration

**Inputs:**
- `chat_input` (string): User's question
- `chat_history` (list): Conversation history

**Outputs:**
- `answer` (string): Generated response

**Nodes:**
1. **search_products**: Retrieves relevant products using hybrid search
2. **generate_response**: Generates natural language answer with GPT-4o

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Azure subscription with:
  - Azure AI Search (Free tier works)
  - Azure OpenAI with GPT-4o deployment
  - Azure OpenAI with text-embedding-ada-002 deployment

### Installation

1. **Clone and navigate to project:**
```powershell
cd C:\Training\Udacity\Azure_GenAI\Project2
```

2. **Create virtual environment:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create `.env` file in project root:
```env
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://YOUR_SEARCH_SERVICE.search.windows.net
AZURE_SEARCH_API_KEY=YOUR_SEARCH_KEY
AZURE_SEARCH_INDEX_NAME=outlander-products-index

# Azure OpenAI (GPT-4o)
AZURE_OPENAI_ENDPOINT=https://YOUR_OPENAI_SERVICE.openai.azure.com/
AZURE_OPENAI_API_KEY=YOUR_OPENAI_KEY
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_DEPLOYMENT_NAME=gpt-4o

# Azure OpenAI (Embeddings)
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://YOUR_EMBEDDING_SERVICE.openai.azure.com/
AZURE_OPENAI_EMBEDDING_API_KEY=YOUR_EMBEDDING_KEY
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
```

5. **Build and index products:**
```powershell
python scripts/build_copilot.py
```

This will:
- Create Azure AI Search index
- Upload 20 products
- Generate vector embeddings
- Verify deployment

---

## 📁 Project Structure

```
Project2/
├── prompt_flows/
│   ├── outlander_copilot/              # Main Copilot Flow ⭐
│   │   ├── flow.dag.yaml               # Flow definition (REQUIRED FOR SUBMISSION)
│   │   ├── search_products.py          # Search node implementation
│   │   ├── generate_response.py        # Generation node implementation
│   │   ├── test_flow.py                # Quick testing script
│   │   └── requirements.txt            # Flow dependencies
│   │
│   └── outlander_evaluation/           # Evaluation Flow ⭐ NEW!
│       ├── flow.dag.yaml               # Evaluation flow definition
│       ├── evaluate_metrics.py         # GPT-4o evaluation (5 metrics)
│       ├── calculate_score.py          # Calculate overall score
│       ├── aggregate_results.py        # Aggregate batch results
│       ├── data.jsonl                  # Sample test cases
│       ├── test_evaluation.py          # Test script
│       └── requirements.txt            # Dependencies
│
├── evaluation/
│   ├── evaluation_dataset.jsonl        # 13 test questions (REQUIRED FOR SUBMISSION)
│   └── results/                        # Evaluation outputs
│       └── promptflow_evaluation_*.json
│
├── data/
│   └── products.json                   # 20 outdoor gear products
│
├── scripts/
│   ├── build_copilot.py                # Complete setup automation
│   ├── verify_setup.py                 # Verify Azure resources
│   └── test_copilot.py                 # Integration tests
│
├── screenshots/                         # For Udacity submission
│
├── PROJECT_REPORT.tex                   # Comprehensive LaTeX report (compile with pdflatex)
├── .env                                 # Environment variables (DO NOT COMMIT)
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

**Files to Submit to Udacity:**
1. `prompt_flows/outlander_copilot/flow.dag.yaml`
2. `prompt_flows/outlander_copilot/*.py` (all Python nodes)
3. `evaluation/evaluation_dataset.jsonl`
4. Screenshots (see checklist below)
5. This README.md

---

## ⚙️ Setup Instructions

### Step 1: Azure Resources Setup

The project uses these Azure resources:

**Azure AI Search:**
- Service: `projectaisearchfree`
- Index: `outlander-products-index`
- Documents: 20 products with vector embeddings
- Features: Hybrid search (vector + BM25)

**Azure OpenAI (GPT-4o):**
- Endpoint: `rodol-mi1txno6-northcentralus.openai.azure.com`
- Model: `gpt-4o`
- Max tokens: 800
- Temperature: 0.7

**Azure OpenAI (Embeddings):**
- Model: `text-embedding-ada-002`
- Dimensions: 1536

### Step 2: Verify Setup

```powershell
cd C:\Training\Udacity\Azure_GenAI\Project2
python scripts/verify_setup.py
```

Expected output:
```
✓ Azure AI Search index verified: 20 documents
✓ Azure OpenAI GPT-4o deployment accessible
✓ Azure OpenAI embeddings deployment accessible
✓ All systems operational
```

---

## 🧪 Testing the Copilot

### Method 1: Quick Test Script (Recommended)

```powershell
cd prompt_flows\outlander_copilot
python test_flow.py "Which tent is the most waterproof?"
```

### Method 2: Prompt Flow CLI

```powershell
# Set environment variables
$env:PF_DISABLE_TRACING="true"
Get-Content .env | ForEach-Object { 
    if($_ -match '^([^=]+)=(.*)$') { 
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') 
    } 
}

# Test flow
cd prompt_flows\outlander_copilot
pf flow test --flow . --inputs chat_input="Which tent is the most waterproof?"
```

### Method 3: VS Code Extension (Visual)

1. Install: **Prompt Flow extension** (`ms-toolsai.prompt-flow`)
2. Open: `prompt_flows/outlander_copilot/flow.dag.yaml`
3. Click: **Visual Editor** button (top right)
4. Click: **Test** button
5. Enter question and run

### Sample Test Questions

```python
"Which tent is the most waterproof?"
"Do you have any sleeping bags rated for below freezing temperatures?"
"What backpacks do you offer for multi-day trips?"
"Which cooking gear is best for lightweight backpacking?"
"Do you sell hammocks or tents under $200?"
"How much does the Summit Pro Backpack cost?"
"What is the capacity of the TrailMaster X4 Tent?"
"Do you have any camping chairs?"
"Which sleeping bag has the lowest temperature rating?"
"What outdoor gear products do you sell?"
```

---

## 📊 Evaluation

### Two Ways to Evaluate

#### Option 1: Dedicated Evaluation Flow (Recommended for Udacity) ⭐

The project includes a **separate evaluation flow** in `prompt_flows/outlander_evaluation/` that can be opened in VS Code Prompt Flow extension.

**Test the evaluation flow:**
```powershell
cd prompt_flows\outlander_evaluation
python test_evaluation.py
```

**Run in VS Code:**
1. Open `prompt_flows/outlander_evaluation/flow.dag.yaml`
2. Click "Open Visual Editor"
3. Click "Batch Run"
4. Select `data.jsonl` as input
5. View evaluation metrics and aggregated results

**What it evaluates:**
- Uses GPT-4o as an LLM judge
- 5 metrics: relevance, accuracy, completeness, groundedness, fluency
- Aggregates results across all test cases
- Logs metrics to Prompt Flow

#### Option 2: Legacy Python Script

```powershell
cd prompt_flows\outlander_copilot
python run_batch_evaluation.py
```

**Expected Results:**
```
✓ 13/13 questions passed (100% success rate)
✓ Average response time: ~5 seconds
✓ All responses grounded in product context
```

### Evaluation Metrics

Each response is evaluated on:
1. **Relevance** (0-5): Does it address the question?
2. **Accuracy** (0-5): Is information factually correct?
3. **Completeness** (0-5): Sufficient detail provided?
4. **Groundedness** (0-5): Based only on context?
5. **Fluency** (0-5): Well-written and clear?

**Pass Criteria:** Overall score ≥ 3.5

### View Evaluation Results

```powershell
# Prompt Flow evaluation results:
prompt_flows/outlander_evaluation/ (view in VS Code extension)

# Legacy script results:
evaluation/results/promptflow_evaluation_YYYYMMDD_HHMMSS.json
```

---

## 🎨 Using VS Code Prompt Flow Extension

### Installation

1. Open VS Code Extensions (`Ctrl+Shift+X`)
2. Search: "Prompt Flow"
3. Install: `ms-toolsai.prompt-flow`

### Visual Flow Editor

**Option A - Direct Access:**
1. Open: `prompt_flows/outlander_copilot/flow.dag.yaml`
2. Click: "Open Visual Editor" (top right)

**Option B - Command Palette:**
1. Press: `Ctrl+Shift+P`
2. Type: "Prompt Flow: Open Visual Editor"
3. Select your flow

**Option C - Right-click:**
- Right-click `flow.dag.yaml` → "Open with Prompt Flow Visual Editor"

### Interactive Testing in VS Code

1. **Single Question Test:**
   - Click **Test** button in visual editor
   - Enter question in `chat_input` field
   - Click **Run**
   - View results in output panel

2. **Batch Run:**
   - Click **Batch Run** button
   - Select dataset: `../../evaluation/evaluation_dataset.jsonl`
   - Click **Submit**
   - View aggregated results

### Debugging

- Click on any node to view:
  - Input values
  - Output values
  - Execution logs
  - Error messages

---

## 🚀 Deployment

### Option 1: Deploy with VS Code Extension

1. **Sign in to Azure:**
   - Click Azure icon in sidebar
   - Sign in with credentials
   - Select subscription

2. **Deploy Flow:**
   - Open `flow.dag.yaml` in visual editor
   - Click **Deploy** button (top right)
   - Or: `Ctrl+Shift+P` → "Prompt Flow: Deploy"

3. **Configure Deployment:**
   - **Name:** `outlander-copilot-deployment`
   - **Compute:** Azure Container Instance
   - **Instance Type:** Standard_D2_v2
   - **Region:** North Central US
   - **Environment:** Python 3.12

4. **Set Environment Variables:**
   Configure all variables from `.env` in deployment settings

### Option 2: Deploy with CLI

```powershell
# Build flow package
cd prompt_flows\outlander_copilot
pf flow build --source . --output dist --format docker

# Deploy to Azure
az containerinstance create `
  --resource-group YOUR_RESOURCE_GROUP `
  --name outlander-copilot `
  --image YOUR_ACR.azurecr.io/outlander-copilot:latest `
  --environment-variables `
    AZURE_SEARCH_ENDPOINT=$env:AZURE_SEARCH_ENDPOINT `
    AZURE_OPENAI_ENDPOINT=$env:AZURE_OPENAI_ENDPOINT
```

---

## 📝 Udacity Submission Checklist

### Required Deliverables

#### 1. ✅ Evaluation Report/Screenshots
**Files to submit:**
- `evaluation/results/promptflow_evaluation_*.json`
- Screenshot showing 13/13 questions passed
- Sample question/answer pairs

**How to generate:**
```powershell
cd prompt_flows\outlander_copilot
python run_batch_evaluation.py
```

**What to capture:**
- Terminal output showing "13/13 questions passed"
- Success rate: 100%
- Sample responses demonstrating accuracy

#### 2. ✅ Deployment Confirmation Screenshot
**What to capture:**
- Azure AI Search index: 20 documents indexed
- Azure OpenAI GPT-4o deployment status
- Azure OpenAI embeddings deployment status

**Portal links:**
- Azure Search: https://portal.azure.com → `projectaisearchfree` → Indexes
- Azure OpenAI: https://portal.azure.com → Your OpenAI resource → Deployments

**Verification command:**
```powershell
python scripts/verify_setup.py
```

#### 3. ✅ Sample Interaction Logs
**Capture 3-5 interactions showing:**
- Question asked
- Full AI response
- Response time
- Correct product information

**Run tests:**
```powershell
cd prompt_flows\outlander_copilot
python test_flow.py "Which tent is the most waterproof?"
python test_flow.py "Do you have sleeping bags for winter camping?"
python test_flow.py "What backpacks are available under $100?"
python test_flow.py "Which cooking equipment is lightweight?"
python test_flow.py "Do you sell hammocks?"
```

#### 4. ✅ Prompt Flow Screenshot (REQUIRED!)
**What to capture:**
- Visual flow diagram from VS Code extension showing:
  - 2 nodes: search_products → generate_response
  - Input connections (chat_input, chat_history)
  - Output connection (answer)
  - Node details visible

**How to capture:**
1. Open `flow.dag.yaml` in VS Code
2. Click "Open Visual Editor" (top right)
3. Take screenshot of full flow graph
4. **OR** Open `flow_visualization.html` in browser and screenshot

#### 5. ✅ Evaluation Dataset File (REQUIRED!)
**File to submit:**
- `evaluation/evaluation_dataset.jsonl` (13 questions with ground truth)

**Format:**
```json
{"chat_input": "Which tent is the most waterproof?", "truth": "The Alpine Explorer Tent and SkyView 2-Person Tent", "chat_history": []}
```

### Submission Organization

Create a `submission/` folder with this structure:

```
submission/
├── screenshots/
│   ├── 01_flow_architecture.png               # VS Code visual editor
│   ├── 02_azure_search_index.png              # 20 documents indexed
│   ├── 03_azure_openai_deployments.png        # GPT-4o + embeddings
│   ├── 04_evaluation_results.png              # 13/13 passed
│   ├── 05_sample_interaction_1.png            # Waterproof tent Q&A
│   ├── 06_sample_interaction_2.png            # Winter sleeping bag Q&A
│   ├── 07_sample_interaction_3.png            # Budget backpack Q&A
│   └── 08_deployment_confirmation.png         # Azure resources
│
├── prompt_flows/
│   └── outlander_copilot/
│       ├── flow.dag.yaml                      # REQUIRED
│       ├── search_products.py                 # REQUIRED
│       ├── generate_response.py               # REQUIRED
│       └── requirements.txt
│
├── evaluation/
│   ├── evaluation_dataset.jsonl               # REQUIRED (13 questions)
│   └── results/
│       └── promptflow_evaluation_*.json       # REQUIRED
│
├── PROJECT_REPORT.pdf                          # Compiled from .tex file
└── README.md                                   # This file
```

**Files NOT to submit:**
- `.env` (contains secrets)
- `.venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `temp_repo/` (temporary files)

---

## 🔧 Technical Details

### Node 1: search_products.py

**Purpose:** Retrieve relevant products using hybrid search

**Process:**
1. Generate query embedding (1536 dimensions) using text-embedding-ada-002
2. Perform vector search (cosine similarity)
3. Perform keyword search (BM25)
4. Combine results and return top 3 products

**Input:** `query` (string)
**Output:** Formatted context string with product details

**Azure Services:**
- Azure OpenAI Embeddings: text-embedding-ada-002
- Azure AI Search: Hybrid search with vector + keyword

**Code snippet:**
```python
@tool
def search_products(query: str) -> str:
    """Hybrid search for products using vector + keyword search"""
    
    # Generate embedding
    embedding_response = embedding_client.embeddings.create(
        model=embedding_deployment,
        input=query
    )
    query_vector = embedding_response.data[0].embedding
    
    # Hybrid search
    results = search_client.search(
        search_text=query,
        vector_queries=[VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=3,
            fields="description_vector"
        )],
        select=["item_number", "item_name", "category", 
                "description", "price"],
        top=3
    )
    
    return format_results(results)
```

### Node 2: generate_response.py

**Purpose:** Generate natural language answer using GPT-4o

**Process:**
1. Build system prompt with RAG instructions
2. Inject retrieved product context
3. Call Azure OpenAI GPT-4o
4. Return generated answer

**Inputs:**
- `question` (string): User's question
- `context` (string): Retrieved product information
- `chat_history` (list): Conversation history

**Output:** `answer` (string)

**Azure Services:**
- Azure OpenAI GPT-4o: gpt-4o deployment

**System Prompt:**
```python
system_message = f"""You are an AI assistant for Outlander Gear Co.,
a company that sells high-quality outdoor equipment.

Your role is to help customers find product information, compare 
products, and answer questions about pricing, features, warranties, 
and specifications.

Be helpful, friendly, and accurate. Base your responses ONLY on 
the product information provided in the context below.

Context from product catalog:
{context}"""
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| Total Response Time | ~5 seconds |
| Search Latency | ~2 seconds |
| Generation Latency | ~3 seconds |
| Evaluation Success Rate | 100% (13/13) |
| Average Relevance Score | 4.85/5.0 |
| Average Accuracy Score | 4.92/5.0 |
| Average Groundedness | 4.96/5.0 |

### Product Catalog

**20 Products Indexed:**
- Tents (3): TrailMaster X4, Alpine Explorer, SkyView 2-Person
- Backpacks (3): Summit Pro, TrekLite, Explorer Pro
- Sleeping Bags (3): CozyNights, PolarMax Extreme, SummitRest
- Cooking Gear (3): TrailChef Stove, CampCook Set, CompactFlame
- Hydration (2): AquaPure Filter, QuickSip Bottle
- Lighting (2): SolarBeam Headlamp, LightWave Lantern
- Navigation (2): TrailGuide GPS, CompassPro
- Footwear (1): TrailWalker Hiking Shoes
- Shelter (1): WeatherShield Tarp

---

## 🛠️ Troubleshooting

### Issue: Missing credentials error in VS Code extension

**Error:** `OpenAIError: Missing credentials`

**Solution:**
Environment variables are loaded automatically in each Python node using `python-dotenv`:

```python
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
```

This is already implemented in both `search_products.py` and `generate_response.py`.

### Issue: Prompt Flow installation error

**Error:** `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: 'pf.exe'`

**Solution:**
```powershell
# Stop all Python processes
Get-Process python* | Stop-Process -Force
Get-Process pf* | Stop-Process -Force

# Uninstall and reinstall
pip uninstall promptflow promptflow-devkit promptflow-core -y
pip install promptflow==1.18.1 promptflow-devkit==1.18.1
```

### Issue: Token tracking error

**Error:** `TypeError: unsupported operand type(s) for +: 'int' and 'dict'`

**Solution:**
```powershell
$env:PF_DISABLE_TRACING="true"
```

Or upgrade to Prompt Flow 1.18.1+:
```powershell
pip install --upgrade promptflow>=1.18.0
```

### Issue: Search returns no results

**Verify:**
```powershell
python scripts/verify_setup.py
```

**Check:**
- Search index exists: `outlander-products-index`
- Document count: 20
- Embeddings are populated

### Issue: GPT-4o deployment not found

**Verify:**
```powershell
# Check .env file has correct values
Get-Content .env | Select-String "AZURE_OPENAI"
```

**Test:**
```powershell
python scripts/test_copilot.py
```

### Issue: VS Code extension not showing visual editor

**Solution:**
1. Ensure Prompt Flow extension is installed and enabled
2. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
3. Open `flow.dag.yaml` and look for visual editor icon (top right)
4. Alternative: Use `flow_visualization.html` in browser

---

## 📚 Additional Resources

### Microsoft Documentation
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/azure/search/)
- [Prompt Flow](https://microsoft.github.io/promptflow/)
- [RAG Pattern Best Practices](https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/)

### Project Files
- **Comprehensive Report:** `PROJECT_REPORT.tex` (compile with pdflatex)
- **Flow Visualization:** `prompt_flows/outlander_copilot/flow_visualization.html`
- **Evaluation Dataset:** `evaluation/evaluation_dataset.jsonl`
- **Evaluation Results:** `evaluation/results/promptflow_evaluation_*.json`

### Udacity Project Requirements
This project fulfills all requirements for **Udacity Azure AI Generative AI Nanodegree - Project 2**:
- ✅ AI Studio project and hub (via Azure portal)
- ✅ AI model deployed (GPT-4o + embeddings)
- ✅ Product data uploaded and indexed (20 products)
- ✅ AI Search index created with embeddings
- ✅ Copilot app built using Prompt Flow
- ✅ Copilot tested with sample questions
- ✅ Automated evaluation performed (13 questions)
- ✅ Manual evaluation capability (test_flow.py)
- ✅ Deployment ready (VS Code extension or CLI)

---

## 👤 Author

**Rodolfo Lerma**  
Udacity Azure AI Generative AI Nanodegree - Project 2  
November 16, 2025

---

## 📄 License

This project is for educational purposes as part of the Udacity Azure AI Nanodegree program.

---

## 🎓 Project Completion Status

✅ **All Requirements Met:**
- [x] Azure AI Search index with 20 products
- [x] Hybrid search implementation (vector + keyword)
- [x] GPT-4o integration with RAG pattern
- [x] Prompt Flow with 2 nodes (search → generate)
- [x] VS Code extension compatibility
- [x] 13-question evaluation dataset
- [x] 100% evaluation success rate
- [x] Comprehensive documentation
- [x] Ready for deployment
- [x] Ready for Udacity submission

**Evaluation Results:** 13/13 questions passed (100% success rate)  
**Response Time:** ~5 seconds average  
**Groundedness:** 4.96/5.0 (all responses based on context only)  
**System Status:** ✅ Production-ready

---

## 📞 Support

If you encounter issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Verify Azure resources: `python scripts/verify_setup.py`
3. Test individual components: `python scripts/test_copilot.py`
4. Check environment variables in `.env`

For Udacity-specific questions, refer to the project rubric and submission guidelines.
