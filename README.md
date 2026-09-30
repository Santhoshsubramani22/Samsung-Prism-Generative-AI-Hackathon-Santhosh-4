
# 🚀 Streaming Live RAG — State-Preserving Answer Refinement

> **Samsung PRISM Generative AI Hackathon — 3rd Edition 2026–27**
> **Theme 4: Streaming Live RAG — State-Preserving Answer Refinement**

### **Don't Restart the Answer. Refine It.**






\

---

## 📌 Table of Contents

* [Project Overview](#-project-overview)
* [Problem Statement](#-problem-statement)
* [Our Solution](#-our-solution)
* [Key Innovation](#-key-innovation)
* [System Architecture](#-system-architecture)
* [How It Works](#-how-it-works)
* [Core Features](#-core-features)
* [Technology Stack](#-technology-stack)
* [Project Structure](#-project-structure)
* [Installation](#-installation)
* [Configuration](#-configuration)
* [Building the RAG Index](#-building-the-rag-index)
* [Running the Application](#-running-the-application)
* [Live Streaming API](#-live-streaming-api)
* [Demo Scenarios](#-demo-scenarios)
* [Evaluation](#-evaluation)
* [Testing](#-testing)
* [Docker Deployment](#-docker-deployment)
* [Innovation & Differentiation](#-innovation--differentiation)
* [Limitations](#-limitations)
* [Future Enhancements](#-future-enhancements)
* [Hackathon Submission Checklist](#-hackathon-submission-checklist)
* [Team](#-team)
* [License](#-license)

---

# 🎯 Project Overview

**Streaming Live RAG** is a state-aware Retrieval-Augmented Generation system designed to solve a key limitation of conventional RAG systems:

> **Traditional RAG treats every user query as a new request.**

Our system instead maintains the conversation state and continuously refines previous answers when the user adds new information or constraints.

The system combines:

* 🧠 Stateful conversation management
* ⚡ Incremental answer streaming
* 🔎 Hybrid semantic + keyword retrieval
* 🧩 Multi-intent query decomposition
* 🎯 Late-constraint refinement
* 🔗 Reciprocal Rank Fusion
* 📊 Reranking
* 🛡️ Evidence filtering
* ✅ Grounding and provenance verification
* 🔄 Answer version tracking
* 📈 Retrieval and latency telemetry

The result is a RAG system that can **understand, retrieve, stream, remember, and refine**.

---

# ❗ Problem Statement

Conventional RAG systems generally follow:

```text
User Query
    ↓
Retrieve Documents
    ↓
Generate Answer
    ↓
Return Response
```

This works well for independent questions but becomes inefficient when conversations evolve.

### Common problems

* Conversation context can be lost.
* New constraints may trigger unnecessary retrieval.
* Previous answers are not explicitly preserved.
* Multi-intent questions may be handled as one retrieval task.
* Keyword-only or semantic-only retrieval can miss relevant evidence.
* Retrieved content may contain irrelevant chunks.
* Users must wait for the complete generated response.
* There is limited visibility into how an answer changes over time.

### Example

```text
User:
"What is the reimbursement policy?"

Assistant:
Answer v1

User:
"The trip was international."

Traditional RAG:
Treat as a new query

Our system:
Preserve previous state
        ↓
Detect late constraint
        ↓
Combine original intent + new constraint
        ↓
Targeted retrieval
        ↓
Answer v2
```

---

# 💡 Our Solution

We introduce a state-preserving RAG pipeline:

```text
UNDERSTAND
     ↓
RETRIEVE
     ↓
STREAM
     ↓
REMEMBER
     ↓
REFINE
```

Instead of restarting the RAG pipeline for every message, the system maintains:

* Previous user intent
* Previous answer
* Conversation constraints
* Retrieved evidence
* Answer version
* Session state
* Grounding information

This allows the system to progressively improve its response.

---

# 🧠 Key Innovation

## State-Preserving Answer Refinement

The central idea of the project is:

> **A new user message should refine an existing answer when possible, rather than restarting the entire conversation.**

### Example

```text
Question 1
"What are the main modules of the Hotel Management System?"
                    ↓
                Answer v1
                    ↓
Question 2
"Tell me only about the booking module."
                    ↓
          Late Constraint Detected
                    ↓
    Previous State + New Constraint
                    ↓
          Targeted Retrieval
                    ↓
                Answer v2
```

The system therefore models the conversation as an evolving answer state.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      USER STREAM     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     CONTROLLER       │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
          WAIT                  PROCESS                RETRIEVE
                                                            │
                                                            ▼
                                                   ┌────────────────┐
                                                   │ Intent         │
                                                   │ Decomposer     │
                                                   └───────┬────────┘
                                                           │
                                      ┌────────────────────┼────────────────────┐
                                      ▼                                         ▼
                              ┌───────────────┐                         ┌───────────────┐
                              │ FAISS Dense   │                         │ BM25 Sparse   │
                              │ Retrieval     │                         │ Retrieval     │
                              └───────┬───────┘                         └───────┬───────┘
                                      │                                         │
                                      └────────────────┬────────────────────────┘
                                                       ▼
                                              ┌────────────────┐
                                              │ RRF Fusion     │
                                              └───────┬────────┘
                                                      ▼
                                              ┌────────────────┐
                                              │ Reranking      │
                                              └───────┬────────┘
                                                      ▼
                                              ┌────────────────┐
                                              │ Evidence       │
                                              │ Filtering      │
                                              └───────┬────────┘
                                                      ▼
                                              ┌────────────────┐
                                              │ Grounded       │
                                              │ Gemini         │
                                              └───────┬────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ SSE Live Stream  │
                                             └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Session State    │
                                             │ + Constraints    │
                                             │ + Answer Version │
                                             └────────┬─────────┘
                                                      │
                                                      ▼
                                                  USER
                                                      │
                                                      ▼
                                                  REFINE
```

---

# 🔄 How It Works

## 1. User Input

The user sends a natural-language request.

```text
"What are the main modules?"
```

---

## 2. Intelligent Controller

The controller classifies the interaction into states such as:

### WAIT

Used for conversational messages:

```text
"Hello"
"Hi"
"Thank you"
"Okay"
```

### PROCESS

Used when the user wants to transform or discuss the current answer:

```text
"Explain that simply."
"Summarize that."
"Tell me more."
```

### RETRIEVE

Used when new knowledge must be retrieved:

```text
"What is the booking module?"
```

### REFINE

Used when a new constraint modifies an existing request:

```text
"Only explain the booking module."
```

---

# 🧩 Multi-Intent Decomposition

The system can split complex questions into independent retrieval intents.

Example:

```text
"What is the reimbursement limit,
what documents are required,
and what is the policy for international travel?"
```

becomes:

```text
Intent 1 → Reimbursement limit
Intent 2 → Required documents
Intent 3 → International travel policy
```

Each intent can then perform targeted retrieval.

---

# 🔎 Hybrid Retrieval

The system combines complementary retrieval strategies.

### FAISS

Provides semantic similarity search.

Useful when:

```text
User wording ≠ document wording
```

### BM25

Provides keyword-based retrieval.

Useful for:

* Exact terminology
* Names
* Technical terms
* IDs
* Important keywords

### Reciprocal Rank Fusion

The results from both retrieval methods are combined using RRF.

```text
FAISS Results
      +
BM25 Results
      ↓
RRF Fusion
      ↓
Reranking
      ↓
Evidence Filtering
```

This provides a more robust retrieval pipeline than relying on only one method.

---

# 🛡️ Evidence-Aware Generation

Retrieved chunks are not blindly passed to the LLM.

The pipeline performs:

```text
Retrieve
   ↓
Fuse
   ↓
Rerank
   ↓
Filter Evidence
   ↓
Generate
   ↓
Verify Grounding
```

The verifier checks:

* Whether citations refer to available evidence
* Whether generated content is supported
* Whether unsupported content receives arbitrary citations
* Grounding/support telemetry

This helps reduce unsupported answers.

---

# ⚡ Live Streaming

The `/api/stream` endpoint uses **Server-Sent Events (SSE)**.

A typical response sequence is:

```text
controller
      ↓
retrieval
      ↓
answer_delta
      ↓
answer_delta
      ↓
answer_delta
      ↓
final
      ↓
[DONE]
```

When Gemini streaming is available, generated content is streamed incrementally.

When Gemini is unavailable, the application provides a deterministic fallback so the demonstration can still show incremental answer delivery.

---

# 🔄 Answer Versioning

Every refinement can produce a new answer version.

```text
Answer v1
    ↓
New constraint
    ↓
State preserved
    ↓
Targeted retrieval
    ↓
Answer v2
    ↓
Another constraint
    ↓
Answer v3
```

This makes the evolution of the answer visible and traceable.

---

# ✨ Core Features

| Feature                | Description                           |
| ---------------------- | ------------------------------------- |
| ⚡ Live Streaming       | Incremental responses through SSE     |
| 🧠 Stateful RAG        | Maintains conversation state          |
| 🔄 Refinement          | Updates answers using new constraints |
| 🧩 Multi-Intent        | Decomposes complex questions          |
| 🔎 Hybrid Retrieval    | FAISS + BM25                          |
| 🔗 RRF                 | Combines retrieval rankings           |
| 🎯 Reranking           | Improves evidence ordering            |
| 🛡️ Evidence Filtering | Removes weak/irrelevant evidence      |
| ✅ Grounding            | Checks answer support                 |
| 📌 Provenance          | Tracks evidence and citations         |
| 🔢 Answer Versioning   | Tracks v1, v2, v3...                  |
| 📊 Telemetry           | Tracks retrieval and latency metrics  |
| 📴 Fallback Mode       | Works without Gemini API              |

---

# 🛠️ Technology Stack

| Layer                | Technology                |
| -------------------- | ------------------------- |
| Programming Language | Python                    |
| Web Framework        | Flask                     |
| Generative AI        | Google Gemini API         |
| Dense Retrieval      | FAISS                     |
| Sparse Retrieval     | BM25                      |
| Ranking Fusion       | Reciprocal Rank Fusion    |
| Reranking            | Custom reranking pipeline |
| Streaming            | Server-Sent Events        |
| Frontend             | HTML, CSS, JavaScript     |
| Documents            | PDF / DOCX / TXT          |
| Testing              | Pytest                    |
| Containerization     | Docker                    |
| Orchestration        | Docker Compose            |
| Version Control      | Git / GitHub              |

---

# 📁 Project Structure

```text
Streaming-Live-RAG/
│
├── app.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
│
├── app/
│   ├── ai/
│   │   └── gemini.py
│   │
│   ├── intelligence/
│   │   ├── controller.py
│   │   └── decomposer.py
│   │
│   ├── rag/
│   │   ├── pipeline.py
│   │   ├── ingestion.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_search.py
│   │   ├── bm25_search.py
│   │   ├── fusion.py
│   │   ├── reranker.py
│   │   ├── evidence_filter.py
│   │   └── metadata.py
│   │
│   ├── session/
│   │   ├── state.py
│   │   └── refinement.py
│   │
│   ├── grounding/
│   │   └── verifier.py
│   │
│   └── telemetry/
│       └── logger.py
│
├── data/
│   └── documents/
│
├── indexes/
│
├── benchmark/
│   └── run_benchmark.py
│
├── scripts/
│   └── build_index.py
│
├── tests/
│
├── templates/
│
├── static/
│
├── docs/
│
└── README.md
```

---

# 💻 Installation

## Prerequisites

Install:

* Python 3.10+
* Git
* pip
* Optional: Docker Desktop
* Optional: Google Gemini API key

---

## Windows Setup

Clone the repository:

```powershell
git clone https://github.com/Santhoshsubramani22/Samsung-Prism-Generative-AI-Hackathon-Santhosh-4.git
cd Samsung-Prism-Generative-AI-Hackathon-Santhosh-4
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# ⚙️ Configuration

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The application can also operate using its deterministic fallback when a Gemini API key is unavailable.

---

# 📚 Add Documents

Place supported documents inside:

```text
data/
└── documents/
    ├── document.pdf
    ├── document.docx
    └── document.txt
```

The repository also contains sample policy documents for demonstration.

---

# 🏗️ Build the RAG Index

Run:

```powershell
py scripts\build_index.py
```

This prepares the retrieval indexes used by the application.

---

# ▶️ Run the Application

Start Flask:

```powershell
py app.py
```

Open:

```text
http://127.0.0.1:5000/chat
```

---

# 🧪 Testing

Run the complete test suite:

```powershell
pytest -q
```

Current updated project validation:

```text
12 passed
```

The tests cover areas including:

* Controller behavior
* Intent decomposition
* Metadata
* Retrieval
* Evidence filtering
* Grounding
* Refinement
* Streaming

---

# 📡 Live Streaming API

Endpoint:

```text
POST /api/stream
```

Example request:

```json
{
  "query": "What is the reimbursement policy?"
}
```

Conceptual SSE event sequence:

```text
event: controller

event: retrieval

event: answer_delta

event: answer_delta

event: answer_delta

event: final

[DONE]
```

The final event contains information such as:

* Answer
* Citations
* Answer version
* Grounding status
* Retrieval metrics
* Latency information

---

# 🎬 Hackathon Demo Scenarios

## Demo 1 — Single Intent

```text
What is the reimbursement policy?
```

Expected:

```text
Controller → RETRIEVE
      ↓
Retrieve evidence
      ↓
Generate grounded answer
      ↓
Stream answer
```

---

## Demo 2 — Multi-Intent

Ask:

```text
What is the reimbursement limit,
what documents are required,
and what is the policy for international travel?
```

Expected:

```text
Complex Query
      ↓
Intent Decomposition
      ↓
Intent 1 ──→ Retrieval
Intent 2 ──→ Retrieval
Intent 3 ──→ Retrieval
      ↓
Evidence Fusion
      ↓
Grounded Response
```

---

## Demo 3 — State-Preserving Refinement

First ask:

```text
What is the reimbursement policy?
```

Then:

```text
The trip was international.
```

Expected:

```text
Answer v1
   ↓
Late Constraint Detected
   ↓
Original Intent + New Constraint
   ↓
Targeted Retrieval
   ↓
Answer v2
```

---

## Demo 4 — Presentation-Only Refinement

Ask:

```text
Make the answer shorter.
```

Expected behavior:

```text
Current Answer
      ↓
Presentation Request
      ↓
No New Retrieval
      ↓
Reuse Current Answer
```

---

## Demo 5 — Unsupported Fact

Ask about information that does not exist in the supplied corpus.

Expected behavior:

```text
No Supporting Evidence
        ↓
No Fabricated Answer
        ↓
No Arbitrary Citation
```

---

# 📊 Evaluation

The system is designed to evaluate multiple dimensions of RAG performance.

### Retrieval Metrics

* Recall@K
* Precision@K
* MRR
* Retrieval relevance

### Generation Metrics

* Groundedness
* Evidence support
* Citation accuracy

### Streaming Metrics

* Time to First Response
* Retrieval latency
* Generation latency
* End-to-end latency

### Stateful RAG Metrics

* Constraint detection
* Evidence reuse
* New evidence retrieved
* Answer version changes
* Refinement effectiveness

### Retrieval Comparison

The evaluation can compare:

```text
Dense Retrieval
       vs
BM25
       vs
Hybrid RRF
       vs
Hybrid + Reranking + Evidence Filtering
```

> The repository does not claim fabricated benchmark values. Quantitative competition results should be generated using a labelled evaluation set.

---

# 🏆 Innovation & Differentiation

## Traditional RAG

```text
Query
  ↓
Retrieve
  ↓
Generate
  ↓
End
```

## Streaming Live RAG

```text
Understand
    ↓
Retrieve
    ↓
Stream
    ↓
Remember
    ↓
Refine
    ↓
Stream Again
```

### Our Differentiators

| Traditional RAG            | Streaming Live RAG         |
| -------------------------- | -------------------------- |
| One-shot response          | Continuous refinement      |
| Stateless request handling | Stateful conversation      |
| Retrieval restart          | Constraint-aware retrieval |
| Single retrieval approach  | FAISS + BM25               |
| Static response            | Versioned answers          |
| Complete response first    | Incremental streaming      |
| Weak evidence handling     | Evidence filtering         |
| Limited provenance         | Grounding verification     |
| Single-intent focus        | Multi-intent decomposition |

### Core Differentiation

> **Traditional RAG answers a question. Streaming Live RAG continuously improves the answer as the conversation evolves.**

---

# 📈 Impact & Use Cases

## 🏢 Enterprise Knowledge

Employees can progressively refine questions about:

* Policies
* Procedures
* Internal documentation
* Technical manuals

## 🎧 Customer Support

Customers can add constraints without restarting their support conversation.

## 🎓 Education

Students can ask:

```text
Explain the topic.
        ↓
Give only the important points.
        ↓
Explain the second concept.
        ↓
Give an example.
```

The system maintains context throughout the interaction.

## 💻 Technical Documentation

Developers can progressively narrow questions about:

* APIs
* Architecture
* Configuration
* Troubleshooting
* Software documentation

## 🔬 Research

Researchers can move from broad exploration to targeted evidence-based questions while preserving the research context.

---

# ⚠️ Limitations

The current prototype has several limitations:

1. **In-memory session state**
   Production deployment would require persistent/distributed state management.

2. **LLM dependency**
   Gemini API availability and latency can affect generation performance.

3. **Document complexity**
   Highly complex layouts, tables, and poorly structured documents can affect extraction and retrieval.

4. **Scale**
   Large-scale multi-user deployment would require distributed infrastructure.

5. **Evaluation dataset**
   A larger labelled benchmark is required for comprehensive quantitative evaluation.

6. **Grounding depth**
   Claim-level verification can be further improved.

---

# 🔮 Future Enhancements

### Phase 1 — Persistent State

Integrate:

```text
Redis / Distributed Session Store
```

for scalable multi-user conversations.

### Phase 2 — Advanced Document Intelligence

Improve processing of:

* Tables
* Scanned PDFs
* Images
* Complex layouts
* Structured documents

### Phase 3 — Adaptive Retrieval

Automatically determine:

```text
Query Complexity
       ↓
Required Retrieval Depth
       ↓
Dynamic Evidence Selection
```

### Phase 4 — Advanced Verification

Implement:

```text
Claim
  ↓
Evidence Matching
  ↓
Claim Verification
  ↓
Grounded Response
```

### Phase 5 — Scalable Streaming

Move toward production-grade:

```text
SSE / WebSocket
      +
Distributed Workers
      +
Persistent State
```

---

# 🐳 Docker Deployment

Build and start the application:

```powershell
docker compose up --build
```

Then open:

```text
http://127.0.0.1:5000/chat
```

Docker provides a reproducible environment for evaluation and deployment.

---

# 📊 Benchmark

Run the included benchmark:

```powershell
py benchmark\run_benchmark.py
```

The benchmark currently provides controller/decomposition smoke evaluation.

For competition-grade evaluation, extend the labelled query set with:

* Retrieval relevance
* Recall@K
* Precision@K
* MRR
* Groundedness
* Citation accuracy
* Streaming latency
* Refinement quality

---

# 📋 Hackathon Submission Checklist

### Samsung PRISM Submission

* [x] Working prototype
* [x] Public GitHub repository
* [x] Reproducible README
* [x] Installation instructions
* [x] Sample documents
* [x] RAG indexing pipeline
* [x] Hybrid retrieval
* [x] Stateful refinement
* [x] Live streaming
* [x] Grounding verification
* [x] Automated tests
* [x] Docker support
* [x] Architecture documentation
* [x] Benchmark framework
* [x] Presentation material
* [x] Final demo video link
* [x] Final submission tag

---

# 🏷️ Official Submission Tag

Before the final hackathon submission, create the required Git tag:

```bash
git tag PRISM_GENAI_HACKATHON_Y2026
git push origin PRISM_GENAI_HACKATHON_Y2026
```

The tagged commit should contain the complete version referenced by the presentation and demonstration.

---

# 👥 Team

### Samsung PRISM Generative AI Hackathon

**3rd Edition — 2026–27**

**Theme 4:** Streaming Live RAG — State-Preserving Answer Refinement

**Team:** Santhosh / Team

**Institution:** VIT Vellore

**Repository:**

[https://github.com/Santhoshsubramani22/Samsung-Prism-Generative-AI-Hackathon-Santhosh-4](https://github.com/Santhoshsubramani22/Samsung-Prism-Generative-AI-Hackathon-Santhosh-4)

[https://drive.google.com/file/d/1wRqeWR_73OF0UlTsOlgp88pMK-UJ6dD7/view?usp=drivesdk](https://drive.google.com/file/d/1wRqeWR_73OF0UlTsOlgp88pMK-UJ6dD7/view?usp=drivesdk)

---

# 🙏 Acknowledgements

We acknowledge:

* **Samsung PRISM** for providing the Generative AI Hackathon platform and challenge.
* **Google Gemini** for generative AI capabilities.
* **FAISS** for vector similarity search.
* **BM25** for sparse keyword retrieval.
* **Flask** for the web application framework.
* **Pytest** for automated testing and validation.

---

# 📄 License

This project is developed as a hackathon prototype.

Refer to the repository for the applicable project licensing and usage terms.

---

# ⭐ Final Takeaway

Traditional RAG follows:

```text
RETRIEVE → GENERATE → END
```

Our approach follows:

```text
UNDERSTAND
     ↓
RETRIEVE
     ↓
STREAM
     ↓
REMEMBER
     ↓
REFINE
     ↓
STREAM AGAIN
```

### **Streaming Live RAG**

> ### **Don't Restart the Answer. Refine It. 🚀**

---

**Samsung PRISM Generative AI Hackathon — 3rd Edition 2026–27**
**Theme 4 — Streaming Live RAG: State-Preserving Answer Refinement**


