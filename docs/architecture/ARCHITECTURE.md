# Assessment Rubric Agent v0.1 - Architecture Documentation

## Overview

Assessment Rubric Agent is an enterprise-grade Teacher Copilot Agent for the K12 Personalized Adaptive Learning (PAL) Platform. It automatically generates pedagogically sound, curriculum-aligned assessment rubrics.

## Architecture Principles

### CIO-Centric Design

Every generated rubric criterion is **traceable** to:
- **Concepts**: Concept Intelligence Objects
- **Learning Outcomes**: Learning Outcome Intelligence
- **Bloom's Levels**: Bloom Intelligence
- **KSA Elements**: Knowledge, Skills, Abilities Intelligence
- **Competencies**: Competency Intelligence
- **Observable Behaviours**: Evidence of Learning
- **Success Indicators**: Measurable criteria

### System Position

```
┌─────────────────────────────────────────────────────────────┐
│                     CURRICULUM LAYER                        │
│         (Board, Grade, Subject, Unit, Chapter)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CONCEPT INTELLIGENCE OBJECTS                   │
│    (Concepts, Prerequisites, Difficulty, Confidence)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               ASSESSMENT RUBRIC AGENT                       │
│              (Teacher Copilot Agent v0.1)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              RUBRIC INTELLIGENCE ENGINE                    │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐  │
│  │ LO Extractor│ │Concept ID    │ │Competency Mapper    │  │
│  └─────────────┘ └──────────────┘ └────────────────────┘  │
│  ┌─────────────────────┐ ┌───────────────────────────┐   │
│  │Criteria Generator   │ │Performance Scale Generator │   │
│  └─────────────────────┘ └───────────────────────────┘   │
│  ┌─────────────────────┐ ┌───────────────────────────┐   │
│  │Evidence Generator   │ │Rubric Assembly Engine      │   │
│  └─────────────────────┘ └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │Teacher PDF  │ │Student PDF   │ │Rubric Matrix JSON │    │
│  └──────────────┘ └──────────────┘ └──────────────────┘    │
│  ┌──────────────────────────────────────────────────┐      │
│  │     Learning Outcome Alignment Matrix             │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Intelligence Layer

#### 1.1 Intelligence Data Loader
- **Location**: `src/assessment_rubric_agent/intelligence/data_loader.py`
- **Purpose**: Load and parse semantic intelligence from CSV
- **Inputs**: CSV file path
- **Outputs**: `FullIntelligenceObject` containing all CIOs

#### 1.2 Intelligence Service
- **Location**: `src/assessment_rubric_agent/services/intelligence_service.py`
- **Purpose**: Service layer for managing intelligence objects
- **Features**: Caching, filtering, retrieval

### 2. Rubric Intelligence Engine

#### 2.1 Learning Outcome Extractor
- **Location**: `src/assessment_rubric_agent/core/engines/learning_outcome_extractor.py`
- **Purpose**: Extract relevant learning outcomes for assessment
- **Inputs**: Request, Concepts, Learning Outcomes
- **Outputs**: Filtered learning outcomes
- **Validation Rules**:
  - Minimum 2 outcomes
  - Bloom's level diversity

#### 2.2 Concept Identifier
- **Location**: `src/assessment_rubric_agent/core/engines/concept_identifier.py`
- **Purpose**: Identify concepts relevant to assessment
- **Inputs**: Request, Concepts, Learning Outcomes
- **Outputs**: Identified concepts with relevance scores
- **Validation Rules**:
  - Must include core concepts
  - Balanced difficulty distribution

#### 2.3 Competency Mapper
- **Location**: `src/assessment_rubric_agent/core/engines/competency_mapper.py`
- **Purpose**: Map competencies to criteria
- **Inputs**: Concepts, Learning Outcomes, Competencies
- **Outputs**: Mapped competencies with indicators

#### 2.4 Assessment Criteria Generator
- **Location**: `src/assessment_rubric_agent/core/engines/assessment_criteria_generator.py`
- **Purpose**: Generate rubric criteria with CIO traceability
- **Inputs**: Concepts, Outcomes, Competencies
- **Outputs**: `RubricCriterion` objects
- **Key Features**:
  - Standard criteria templates
  - Assessment-type-specific criteria
  - Marks allocation

#### 2.5 Performance Scale Generator
- **Location**: `src/assessment_rubric_agent/core/engines/performance_scale_generator.py`
- **Purpose**: Generate performance levels and descriptors
- **Inputs**: Request, Criteria
- **Outputs**: `PerformanceLevel` and `PerformanceDescriptor` objects

#### 2.6 Evidence Definition Generator
- **Location**: `src/assessment_rubric_agent/core/engines/evidence_definition_generator.py`
- **Purpose**: Generate evidence definitions
- **Inputs**: Request, Criteria
- **Outputs**: Evidence definitions and success criteria

#### 2.7 Rubric Assembly Engine
- **Location**: `src/assessment_rubric_agent/core/engines/rubric_assembly_engine.py`
- **Purpose**: Assemble final rubric structure
- **Inputs**: All engine outputs
- **Outputs**: `RubricMatrix`, `TeacherRubricContent`, `StudentRubricContent`

### 3. Workflow Layer

#### 3.1 LangGraph Workflow
- **Location**: `src/assessment_rubric_agent/core/workflows/rubric_workflow.py`
- **Purpose**: Orchestrate complete pipeline
- **State**: `WorkflowState` TypedDict
- **Nodes**:
  1. `load_intelligence` - Load CIOs
  2. `extract_outcomes` - Extract learning outcomes
  3. `identify_concepts` - Identify concepts
  4. `map_competencies` - Map competencies
  5. `generate_criteria` - Generate criteria
  6. `generate_performance_scale` - Generate scale
  7. `generate_evidence` - Generate evidence
  8. `assemble_rubric` - Assemble rubric
  9. `generate_outputs` - Generate PDFs/JSON
  10. `finalize` - Finalize

### 4. Service Layer

#### 4.1 PDF Generation Service
- **Location**: `src/assessment_rubric_agent/services/pdf_generation_service.py`
- **Technology**: WeasyPrint + Jinja2
- **Outputs**: Teacher PDF, Student PDF
- **Features**: Beautiful formatting, professional design

#### 4.2 JSON Output Service
- **Location**: `src/assessment_rubric_agent/services/json_output_service.py`
- **Outputs**: Rubric Matrix JSON, LO Alignment Matrix JSON

### 5. API Layer

#### 5.1 FastAPI Application
- **Location**: `src/assessment_rubric_agent/main.py`
- **Endpoints**:
  - `POST /api/v1/rubric/generate` - Generate rubric
  - `GET /api/v1/rubric/{request_id}` - Get status
  - `GET /api/v1/rubric/{request_id}/json` - Download JSON
  - `GET /api/v1/rubric/{request_id}/teacher-pdf` - Download teacher PDF
  - `GET /api/v1/rubric/{request_id}/student-pdf` - Download student PDF

## Data Flow

```
Request → Workflow → Intelligence Loader → CIOs
                    ↓
              LearningOutcomeExtractor
                    ↓
              ConceptIdentifier
                    ↓
              CompetencyMapper
                    ↓
              AssessmentCriteriaGenerator ──→ RubricCriterion (with CIO traceability)
                    ↓
              PerformanceScaleGenerator ──→ PerformanceLevel + Descriptors
                    ↓
              EvidenceGenerator ──→ Evidence Definitions
                    ↓
              RubricAssemblyEngine ──→ RubricMatrix + Contents
                    ↓
              PDF/JSON Services ──→ Final Outputs
```

## Schema Design

### Input Contract
```python
RubricGenerationRequest:
  - request_id: UUID
  - assignment: AssignmentInformation
  - context: ContextIntelligence
  - [Optional] Pre-loaded CIOs
  - Generation settings
```

### Output Contract
```python
RubricGenerationResponse:
  - request_id: UUID
  - status: str (success/partial/failed)
  - rubric_matrix: RubricMatrix
  - teacher_rubric_pdf_path: str
  - student_rubric_pdf_path: str
  - alignment_coverage: float
  - cios_used: list[str]
```

### Core Intelligence Objects
- `CurriculumIntelligence`: Board, Grade, Subject, Chapter
- `ConceptIntelligence`: Concepts with prerequisites, difficulty
- `LearningOutcomeIntelligence`: Outcomes with Bloom's levels
- `KSAIntelligence`: Knowledge, Skills, Abilities
- `CompetencyIntelligence`: Competencies with indicators
- `AssessmentIntelligence`: Assessment types, blueprints

## Sequence Diagram

```
┌────────┐     ┌─────────────┐     ┌──────────┐     ┌────────────┐
│ Teacher│     │ FastAPI     │     │ Workflow │     │ Engines    │
└───┬────┘     └──────┬──────┘     └─────┬────┘     └─────┬──────┘
    │ POST /generate  │                  │                 │
    │────────────────>│                  │                 │
    │                 │                  │                 │
    │                 │ load_intelligence│                 │
    │                 │────────────────>│                 │
    │                 │                 │────────>load()  │
    │                 │                 │<───────────────│
    │                 │                 │                 │
    │                 │ extract_outcomes│                 │
    │                 │────────────────>│                 │
    │                 │                 │────────────────>│
    │                 │                 │<────────────────│
    │                 │                 │                 │
    │                 │ identify_concepts│                │
    │                 │────────────────>│                 │
    │                 │                 │────────────────>│
    │                 │                 │<────────────────│
    │                 │                 │                 │
    │                 │    [Continue through all engines]│
    │                 │                 │                 │
    │                 │  assemble_rubric│                 │
    │                 │────────────────>│                 │
    │                 │                 │────> RubricMatrix│
    │                 │                 │<──── Teacher/Student│
    │                 │                 │    Content       │
    │                 │                 │                 │
    │                 │ generate_outputs│                 │
    │                 │────────────────>│                 │
    │                 │                 │────> PDF Gen    │
    │                 │                 │────> JSON Gen   │
    │                 │                 │                 │
    │ Response        │                  │                 │
    │<────────────────│                  │                 │
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
│                    (Nginx/AWS ALB)                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   API Pod 1   │   │   API Pod 2   │   │   API Pod 3   │
│  Assessment   │   │  Assessment   │   │  Assessment   │
│ Rubric Agent  │   │ Rubric Agent  │   │ Rubric Agent  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│    Redis      │   │  PostgreSQL   │   │   Outputs     │
│   (Cache)     │   │  (Persist)    │   │   (S3/GCS)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Python 3.12 | Runtime |
| API | FastAPI | REST API |
| Workflow | LangGraph | Orchestration |
| Validation | Pydantic | Schema validation |
| PDF | WeasyPrint | PDF generation |
| Caching | Redis | Response caching |
| Database | PostgreSQL | Persistence (optional) |
| Container | Docker | Deployment |
| Orchestration | Kubernetes/Docker Compose | Scaling |

## Error Handling

Each engine implements:
- Input validation
- Error catching and logging
- Warning generation
- Partial result handling

```
Engine.validate() → tuple[bool, list[str]]
  - Returns (is_valid, error_messages)
```

## Testing Strategy

- **Unit Tests**: Each engine module
- **Integration Tests**: Workflow execution
- **API Tests**: Endpoint validation
- **E2E Tests**: Full generation flow

## Security Considerations

- Input sanitization
- Rate limiting
- Authentication (future)
- Audit logging
