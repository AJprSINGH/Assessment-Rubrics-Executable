# Assessment Rubric Agent v0.1

## 🎯 Enterprise-Grade Teacher Copilot Agent for K12 PAL Platform

An intelligent agent that automatically generates pedagogically sound, curriculum-aligned assessment rubrics for teachers.

### Key Features

- **CIO-Centric Architecture**: Every criterion traces to Concepts, Learning Outcomes, Bloom's Taxonomy, KSAs, and Competencies
- **Multi-Output Generation**: Teacher Rubric PDF, Student Rubric PDF, Rubric Matrix JSON, Learning Outcome Alignment Matrix
- **LangGraph Workflow**: Deterministic 14-step reasoning pipeline
- **Production-Ready**: Logging, validation, error handling, comprehensive API documentation

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Input/Output Contracts](#inputoutput-contracts)
- [Example Usage](#example-usage)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)

---

## Architecture Overview

### System Position

```
CURRICULUM LAYER → CONCEPT INTELLIGENCE OBJECTS → ASSESSMENT RUBRIC AGENT → RUBRIC INTELLIGENCE ENGINE → TEACHER COPILOT
```

### CIO-Centric Design

Every generated rubric criterion is **traceable** to:

| Traceability Element | Description |
|---------------------|-------------|
| **Concepts** | Concept Intelligence Objects from curriculum |
| **Learning Outcomes** | Observable outcomes aligned to curriculum |
| **Bloom's Levels** | Cognitive taxonomy levels |
| **KSA Elements** | Knowledge, Skills, Abilities |
| **Competencies** | Performance competencies |
| **Observable Behaviours** | Measurable student actions |
| **Evidence of Learning** | Collection methods |

### Rubric Intelligence Engines

| Engine | Purpose |
|--------|---------|
| Learning Outcome Extractor | Extract relevant outcomes for assessment |
| Concept Identifier | Identify concepts with relevance scoring |
| Competency Mapper | Map competencies to criteria |
| Assessment Criteria Generator | Generate criteria with CIO traceability |
| Performance Scale Generator | Create performance levels and descriptors |
| Evidence Definition Generator | Define evidence requirements |
| Rubric Assembly Engine | Assemble final rubric structure |

---

## Quick Start

### Prerequisites

- Python 3.12+ (Python 3.13 recommended)
- pip package manager
- Docker (for containerized deployment)

### Local Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd Assessment-Rubrics-Executable

# 2. Create virtual environment (recommended)
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure semantic_intelligence.csv is in the project root
# (Download from your data source if not present)

# 5. Run the demo script
python run.py
```

### Windows PDF Generation Note

If you see errors about `gobject-2.0-0` when generating PDFs, this means WeasyPrint's GTK libraries aren't installed. The system will automatically generate HTML files instead, which you can open in any browser and print to PDF manually.

**For native PDF support on Windows**, install GTK3 from:
- Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

### Running the Demo

The simplest way to test the system:

```bash
# From the project root directory
python run.py
```

This will:
1. Initialize the workflow
2. Generate a sample rubric for "Chemical Reactions Investigation Project"
3. Output Teacher PDF, Student PDF, and JSON files to `outputs/` folder

### Alternative: Run from scripts folder

```bash
cd scripts
python demo.py
```

### API Server

Start the FastAPI server:

```bash
uvicorn src.assessment_rubric_agent.main:app --reload
```

Then access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run with Docker
docker build -t assessment-rubric-agent .
docker run -p 8000:8000 -v ./semantic_intelligence.csv:/app/data/intelligence.csv assessment-rubric-agent
```

### Access API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Reference

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### Generate Rubric

```http
POST /api/v1/rubric/generate
```

Generate a complete assessment rubric.

**Request Body:**

```json
{
  "request_id": "unique-request-id",
  "assignment": {
    "board": "CBSE",
    "grade": 10,
    "subject": "Science",
    "chapter": "Chemical Reactions",
    "assignment_name": "Chemical Reactions Project",
    "assessment_type": "Project",
    "rubric_type": "Analytical",
    "total_marks": 50,
    "performance_scale": ["Exemplary", "Proficient", "Developing", "Beginning"]
  },
  "context": {
    "class_size": 35,
    "student_profile": "Mixed ability",
    "time_duration": "2 weeks"
  },
  "include_teacher_notes": true,
  "include_student_checklist": true,
  "generate_json": true,
  "generate_pdf": true
}
```

**Response:**

```json
{
  "request_id": "unique-request-id",
  "status": "success",
  "rubric_matrix": { ... },
  "teacher_rubric_pdf_path": "outputs/pdfs/teacher_rubric_unique-request-id.pdf",
  "student_rubric_pdf_path": "outputs/pdfs/student_rubric_unique-request-id.pdf",
  "alignment_coverage": 95.5,
  "generation_time_seconds": 2.34
}
```

#### Download Rubric JSON

```http
GET /api/v1/rubric/{request_id}/json
```

#### Download Teacher Rubric PDF

```http
GET /api/v1/rubric/{request_id}/teacher-pdf
```

#### Download Student Rubric PDF

```http
GET /api/v1/rubric/{request_id}/student-pdf
```

#### Health Check

```http
GET /health
```

---

## Input/Output Contracts

### Input Contract: `RubricGenerationRequest`

```python
class RubricGenerationRequest(BaseModel):
    request_id: str                    # Unique request identifier
    assignment: AssignmentInformation   # Assignment details
    context: ContextIntelligence       # Context information
    include_teacher_notes: bool       # Include teacher notes
    include_student_checklist: bool   # Include student checklist
    generate_json: bool               # Generate JSON output
    generate_pdf: bool                # Generate PDF outputs
    cio_centric_mode: bool = True      # Ensure CIO traceability
```

### Assignment Information

```python
class AssignmentInformation(BaseModel):
    board: Board                      # CBSE, ICSE, State, IB, Cambridge
    grade: int                        # 1-12
    subject: Subject                  # Science, Mathematics, English, etc.
    chapter: str                      # Chapter name/number
    assignment_name: str              # Name of the assignment
    assessment_type: AssessmentType   # Project, Assignment, Lab Work, etc.
    rubric_type: RubricType           # Analytical, Holistic, etc.
    total_marks: int                  # Total marks (1-100)
    performance_scale: list[str]      # e.g., ["Exemplary", "Proficient", ...]
```

### Output Contract: `RubricGenerationResponse`

```python
class RubricGenerationResponse(BaseModel):
    request_id: str
    status: str                      # success, partial, failed
    rubric_matrix: RubricMatrix       # Complete rubric data
    teacher_rubric_pdf_path: str     # Path to teacher PDF
    student_rubric_pdf_path: str      # Path to student PDF
    alignment_coverage: float         # % of LOs covered
    generation_time_seconds: float
    cios_used: list[str]             # CIOs used in generation
    errors: list[str]                # Any errors encountered
    warnings: list[str]              # Warnings during generation
```

---

## Example Usage

### Python Client Example

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/rubric/generate"

# Request payload
payload = {
    "request_id": "example-001",
    "assignment": {
        "board": "CBSE",
        "grade": 6,
        "subject": "Science",
        "chapter": "Friction",
        "assignment_name": "Friction Model Project",
        "project_type": "Design Project",
        "assessment_type": "Project",
        "rubric_type": "Analytical",
        "total_marks": 50,
        "performance_scale": ["Exemplary", "Proficient", "Developing", "Beginning"]
    },
    "context": {
        "class_size": 35,
        "student_profile": "Mixed ability",
        "time_duration": "2 weeks",
        "available_resources": ["Textbook", "Lab equipment", "Internet"],
        "differentiation_required": True
    },
    "generate_json": True,
    "generate_pdf": True,
    "cio_centric_mode": True
}

# Make request
response = requests.post(url, json=payload)
result = response.json()

print(f"Status: {result['status']}")
print(f"Alignment Coverage: {result['alignment_coverage']}%")
print(f"Teacher PDF: {result['teacher_rubric_pdf_path']}")
print(f"Student PDF: {result['student_rubric_pdf_path']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/rubric/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "curl-test-001",
    "assignment": {
      "board": "CBSE",
      "grade": 10,
      "subject": "Science",
      "chapter": "Chemical Reactions",
      "assignment_name": "Chemical Reactions Research Project",
      "assessment_type": "Project",
      "total_marks": 50
    },
    "context": {
      "class_size": 30
    },
    "generate_pdf": true
  }'
```

### JavaScript/Node.js Example

```javascript
const response = await fetch('http://localhost:8000/api/v1/rubric/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    request_id: 'nodejs-example-001',
    assignment: {
      board: 'CBSE',
      grade: 6,
      subject: 'Science',
      chapter: 'Friction',
      assignment_name: 'Friction Investigation Project',
      assessment_type: 'Project',
      total_marks: 50
    },
    context: {
      class_size: 35
    },
    generate_pdf: true,
    generate_json: true
  })
});

const result = await response.json();
console.log('Rubric generated:', result);
```

---

## Generated Outputs

### 1. Teacher Rubric PDF

**Contains:**
- Assessment Information (Board, Grade, Subject, Chapter, Total Marks)
- Learning Outcomes Alignment
- Concept Coverage
- Rubric Criteria with Performance Descriptors
- Performance Levels
- Success Indicators
- Evidence of Learning
- Marks Allocation
- Teacher Notes
- Common Misconceptions

### 2. Student Rubric PDF

**Contains:**
- Expectations
- Performance Indicators
- Success Criteria
- Self-Assessment Checklist

### 3. Rubric Matrix JSON

```json
{
  "rubric_id": "RUBRIC_ABC123",
  "assessment_information": { ... },
  "criteria": [
    {
      "criterion_id": "CRIT_01",
      "criterion_name": "Concept Understanding",
      "concept_ids": ["CONCEPT_001"],
      "learning_outcome_ids": ["LO_001"],
      "blooms_level": "Understand",
      "total_marks": 10,
      "performance_descriptors": [ ... ]
    }
  ],
  "learning_outcome_alignment": { ... }
}
```

### 4. Learning Outcome Alignment Matrix

```
Learning Outcome → Concept → Competency → Assessment Criterion → Performance Indicator → Evidence
```

---

## Development

### Project Structure

```
Assessment-Rubrics-Executable/
├── src/
│   └── assessment_rubric_agent/
│       ├── core/
│       │   ├── schemas/          # Pydantic schemas
│       │   ├── engines/         # Rubric intelligence engines
│       │   ├── workflows/        # LangGraph workflows
│       │   └── utils/           # Utilities
│       ├── intelligence/        # Data loaders
│       └── services/            # Business logic services
├── templates/
│   └── pdf/                    # PDF templates
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/             # Integration tests
├── config/                     # Configuration
├── docs/                       # Documentation
└── outputs/                    # Generated outputs
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_engines.py

# Run with verbose output
pytest -v
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t assessment-rubric-agent:v0.1 .

# Run container
docker run -d \
  -p 8000:8000 \
  -v ./semantic_intelligence.csv:/app/data/intelligence.csv \
  --name rubric-agent \
  assessment-rubric-agent:v0.1
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Kubernetes (Production)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: assessment-rubric-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: assessment-rubric-agent
  template:
    spec:
      containers:
      - name: agent
        image: assessment-rubric-agent:v0.1
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

---

## Testing

### Unit Tests

```bash
pytest tests/unit/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### API Tests

```bash
# Start server in background
uvicorn src.assessment_rubric_agent.main:app &
sleep 3

# Run API tests
pytest tests/ -k api -v

# Kill server
pkill uvicorn
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INTELLIGENCE_CSV_PATH` | `/workspace/semantic_intelligence.csv` | Path to intelligence data CSV |
| `REDIS_URL` | - | Redis connection URL for caching |
| `DATABASE_URL` | - | PostgreSQL connection URL |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LLM_MODEL` | `gpt-4` | LLM model for optional enhancements |

---

## Troubleshooting

### Common Issues

**1. CSV file not found**
```
Error: FileNotFoundError: [Errno 2] No such file: 'semantic_intelligence.csv'
```
**Solution**: Set `INTELLIGENCE_CSV_PATH` environment variable to the correct path.

**2. WeasyPrint not installed**
```
ModuleNotFoundError: No module named 'weasyprint'
```
**Solution**: Install dependencies with `pip install weasyprint` or use Docker.

**3. PDF generation fails**
```
Error: PDF generation failed
```
**Solution**: Check logs for details. Ensure fonts are installed (see Dockerfile).

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

---

## License

MIT License - See LICENSE file for details.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-06-25 | Initial release |

---

## Support

For issues and questions:
- Create an issue on the repository
- Contact the development team

---

**Built with ❤️ for K12 Education**