"""
Assessment Rubric Agent v0.1
Enterprise-grade Teacher Copilot Agent for K12 Assessment Rubric Generation

Architecture:
    Curriculum Layer → Concept Intelligence Objects → Assessment Rubric Agent → Rubric Intelligence Engine → Teacher Copilot

CIO-Centric Design:
    Every generated rubric criterion is traceable to:
    - Concepts
    - Learning Outcomes
    - Bloom's Taxonomy Levels
    - KSA Elements
    - Competencies
    - Observable Behaviours
    - Evidence of Learning
"""

__version__ = "0.1.0"
__author__ = "Assessment Rubric Agent Team"

from .main import app
from .core.schemas.contracts import (
    RubricGenerationRequest,
    RubricGenerationResponse,
    RubricMatrix,
    AssignmentInformation,
    ContextIntelligence
)
from .core.workflows.rubric_workflow import RubricGenerationWorkflow

__all__ = [
    "app",
    "RubricGenerationRequest",
    "RubricGenerationResponse",
    "RubricMatrix",
    "AssignmentInformation",
    "ContextIntelligence",
    "RubricGenerationWorkflow"
]