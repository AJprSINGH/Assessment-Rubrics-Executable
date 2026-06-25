"""
FastAPI Application for Assessment Rubric Agent v0.1
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .core.schemas.contracts import RubricGenerationRequest, RubricGenerationResponse
from .core.workflows.rubric_workflow import RubricGenerationWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get CSV path from environment or use default
DEFAULT_CSV_PATH = os.environ.get(
    "INTELLIGENCE_CSV_PATH",
    "/workspace/semantic_intelligence.csv"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Assessment Rubric Agent v0.1")
    
    # Initialize workflow
    csv_path = DEFAULT_CSV_PATH
    if not Path(csv_path).exists():
        logger.warning(f"Intelligence CSV not found at {csv_path}, using empty data")
        csv_path = "/workspace/semantic_intelligence.csv"
    
    app.state.workflow = RubricGenerationWorkflow(csv_path)
    logger.info("Workflow initialized")
    
    yield
    
    logger.info("Shutting down Assessment Rubric Agent")


# Create FastAPI app
app = FastAPI(
    title="Assessment Rubric Agent v0.1",
    description="""
    ## Assessment Rubric Agent v0.1
    
    Enterprise-grade Teacher Copilot Agent for K12 Personalized Adaptive Learning (PAL) Platform.
    
    ### Features
    
    * **CIO-Centric Architecture**: Every criterion traces to Concepts, Learning Outcomes, Bloom Levels, KSAs, and Competencies
    * **Multi-Output Generation**: Teacher Rubric PDF, Student Rubric PDF, Rubric Matrix JSON, Learning Outcome Alignment Matrix
    * **LangGraph Workflow**: Deterministic 14-step reasoning pipeline
    * **Production-Ready**: Logging, validation, error handling, API documentation
    
    ### Architecture
    
    ```
    Curriculum Layer → Concept Intelligence Objects → Assessment Rubric Agent → Rubric Intelligence Engine → Teacher Copilot
    ```
    
    ### Generated Outputs
    
    1. **Teacher Rubric PDF**: Full assessment rubric with learning outcomes, criteria, performance descriptors, teacher notes
    2. **Student Rubric PDF**: Simplified rubric with expectations, success indicators, self-assessment checklist
    3. **Rubric Matrix JSON**: Complete rubric data in structured JSON format
    4. **Learning Outcome Alignment Matrix**: Traceability from LOs to criteria
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Assessment Rubric Agent v0.1",
        "version": "0.1.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Assessment Rubric Agent v0.1",
        "description": "Teacher Copilot Agent for K12 Assessment Rubric Generation",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


# Generate rubric endpoint
@app.post(
    "/api/v1/rubric/generate",
    response_model=RubricGenerationResponse,
    tags=["Rubric Generation"],
    summary="Generate Assessment Rubric",
    description="""
    Generate a complete assessment rubric based on curriculum intelligence.
    
    ### Input Contract
    
    The request must include:
    * **Assignment Information**: Board, grade, subject, chapter, assignment details
    * **Assessment Configuration**: Type, rubric type, total marks, performance scale
    
    ### Output Contract
    
    The response includes:
    * **Rubric Matrix**: Complete rubric data structure
    * **Teacher PDF**: Full rubric for teacher use
    * **Student PDF**: Simplified rubric for students
    * **Alignment Matrix**: Learning outcome traceability
    
    ### CIO-Centric Traceability
    
    Every criterion is traced to:
    * Concepts
    * Learning Outcomes  
    * Bloom's Taxonomy Levels
    * KSA Elements
    * Competencies
    * Observable Behaviours
    * Evidence of Learning
    """
)
async def generate_rubric(request: RubricGenerationRequest):
    """Generate assessment rubric"""
    try:
        logger.info(f"Received rubric generation request: {request.request_id}")
        
        # Execute workflow
        response = await app.state.workflow.execute(request)
        
        logger.info(f"Rubric generation completed: {response.status}")
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Rubric generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get rubric status endpoint
@app.get(
    "/api/v1/rubric/{request_id}",
    tags=["Rubric Generation"],
    summary="Get Rubric Status",
    description="Get the status of a rubric generation request"
)
async def get_rubric_status(request_id: str):
    """Get rubric generation status"""
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Rubric generation is synchronous - check /api/v1/rubric/generate"
    }


# Download rubric JSON endpoint
@app.get(
    "/api/v1/rubric/{request_id}/json",
    tags=["Downloads"],
    summary="Download Rubric JSON",
    description="Download the rubric matrix as JSON"
)
async def download_rubric_json(request_id: str):
    """Download rubric JSON"""
    json_path = Path("outputs/jsons") / f"rubric_matrix_{request_id}.json"
    
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Rubric JSON not found")
    
    return FileResponse(
        path=json_path,
        filename=f"rubric_{request_id}.json",
        media_type="application/json"
    )


# Download teacher rubric PDF endpoint
@app.get(
    "/api/v1/rubric/{request_id}/teacher-pdf",
    tags=["Downloads"],
    summary="Download Teacher Rubric PDF",
    description="Download the teacher rubric as PDF"
)
async def download_teacher_pdf(request_id: str):
    """Download teacher rubric PDF"""
    pdf_path = Path("outputs/pdfs") / f"teacher_rubric_{request_id}.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Teacher PDF not found")
    
    return FileResponse(
        path=pdf_path,
        filename=f"teacher_rubric_{request_id}.pdf",
        media_type="application/pdf"
    )


# Download student rubric PDF endpoint
@app.get(
    "/api/v1/rubric/{request_id}/student-pdf",
    tags=["Downloads"],
    summary="Download Student Rubric PDF",
    description="Download the student rubric as PDF"
)
async def download_student_pdf(request_id: str):
    """Download student rubric PDF"""
    pdf_path = Path("outputs/pdfs") / f"student_rubric_{request_id}.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Student PDF not found")
    
    return FileResponse(
        path=pdf_path,
        filename=f"student_rubric_{request_id}.pdf",
        media_type="application/pdf"
    )


# Example request endpoint
@app.get(
    "/api/v1/examples/generate-request",
    tags=["Examples"],
    summary="Get Example Request",
    description="Get an example rubric generation request"
)
async def get_example_request():
    """Get example rubric generation request"""
    return {
        "request_id": "example-001",
        "assignment": {
            "board": "CBSE",
            "grade": 10,
            "subject": "Science",
            "unit": "Chemical Reactions",
            "chapter": "1",
            "assignment_name": "Chemical Reactions Project",
            "project_type": "Research Project",
            "assessment_type": "Project",
            "rubric_type": "Analytical",
            "total_marks": 50,
            "performance_scale": ["Exemplary", "Proficient", "Developing", "Beginning"]
        },
        "context": {
            "class_size": 35,
            "student_profile": "Mixed ability",
            "time_duration": "2 weeks",
            "available_resources": ["Textbook", "Internet", "Lab equipment"],
            "differentiation_required": True
        },
        "include_teacher_notes": True,
        "include_student_checklist": True,
        "generate_json": True,
        "generate_pdf": True,
        "language": "en",
        "cio_centric_mode": True
    }


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "message": str(exc)
        }
    )


# Mount static files for outputs
outputs_path = Path("outputs")
if not outputs_path.exists():
    outputs_path.mkdir(parents=True, exist_ok=True)

try:
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
except Exception:
    pass


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
