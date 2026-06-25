"""
Input and Output Contracts for Assessment Rubric Agent v0.1
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from .intelligence_objects import (
    Board, Subject, AssessmentType, RubricType, BloomLevel,
    CurriculumIntelligence, ConceptIntelligence, LearningOutcomeIntelligence,
    KSAIntelligence, CompetencyIntelligence, AssessmentIntelligence,
    PedagogicalIntelligence, MisconceptionIntelligence, FullIntelligenceObject
)


# ============================================================================
# INPUT CONTRACT
# ============================================================================

class AssignmentInformation(BaseModel):
    """Assignment information provided by teacher"""
    board: Board
    grade: int = Field(ge=1, le=12)
    subject: Subject
    unit: Optional[str] = None
    chapter: str
    assignment_name: str
    project_type: Optional[str] = None
    assessment_type: AssessmentType = AssessmentType.PROJECT
    rubric_type: RubricType = RubricType.ANALYTICAL
    total_marks: int = Field(ge=1, le=100)
    performance_scale: list[str] = Field(
        default=["Exemplary", "Proficient", "Developing", "Beginning"]
    )
    
    @field_validator('performance_scale')
    @classmethod
    def validate_scale(cls, v):
        if len(v) < 2:
            raise ValueError('Performance scale must have at least 2 levels')
        return v


class ContextIntelligence(BaseModel):
    """Context intelligence for the assessment"""
    class_size: Optional[int] = Field(default=30, ge=1, le=200)
    student_profile: Optional[str] = None
    time_duration: Optional[str] = None  # e.g., "2 weeks"
    available_resources: list[str] = Field(default_factory=list)
    differentiation_required: bool = False
    inclusion_considerations: list[str] = Field(default_factory=list)


class RubricGenerationRequest(BaseModel):
    """Complete input contract for rubric generation"""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    assignment: AssignmentInformation
    context: ContextIntelligence = Field(default_factory=ContextIntelligence)
    
    # Optional pre-loaded intelligence (if not provided, will be loaded from CSV)
    curriculum_intelligence: Optional[CurriculumIntelligence] = None
    concept_intelligence: Optional[list[ConceptIntelligence]] = None
    learning_outcome_intelligence: Optional[list[LearningOutcomeIntelligence]] = None
    ksa_intelligence: Optional[KSAIntelligence] = None
    competency_intelligence: Optional[list[CompetencyIntelligence]] = None
    assessment_intelligence: Optional[AssessmentIntelligence] = None
    pedagogical_intelligence: Optional[PedagogicalIntelligence] = None
    misconception_intelligence: Optional[MisconceptionIntelligence] = None
    
    # Generation settings
    include_teacher_notes: bool = True
    include_student_checklist: bool = True
    generate_json: bool = True
    generate_pdf: bool = True
    language: str = "en"
    
    # CIO-centric flag - ensures all criteria trace to CIOs
    cio_centric_mode: bool = True
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


# ============================================================================
# OUTPUT CONTRACT - RUBRIC CRITERIA
# ============================================================================

class ObservableBehaviourDefinition(BaseModel):
    """Observable behaviour in generated rubric"""
    behaviour: str
    assessment_method: str
    evidence_required: str


class SuccessIndicator(BaseModel):
    """Success indicator for a criterion"""
    indicator: str
    description: str
    blooms_level: BloomLevel
    observable: bool = True


class PerformanceDescriptor(BaseModel):
    """Performance descriptor for a level"""
    level: str
    description: str
    marks_range: tuple[int, int]
    key_characteristics: list[str] = Field(default_factory=list)


class CriterionEvidence(BaseModel):
    """Evidence requirement for a criterion"""
    evidence_type: str
    description: str
    collection_method: str


class RubricCriterion(BaseModel):
    """Individual rubric criterion"""
    criterion_id: str
    criterion_name: str
    description: str
    
    # CIO Tracing
    concept_ids: list[str] = Field(default_factory=list)
    concept_names: list[str] = Field(default_factory=list)
    learning_outcome_ids: list[str] = Field(default_factory=list)
    learning_outcome_statements: list[str] = Field(default_factory=list)
    blooms_level: BloomLevel
    competency_ids: list[str] = Field(default_factory=list)
    
    # Criterion components
    observable_behaviours: list[ObservableBehaviourDefinition] = Field(default_factory=list)
    success_indicators: list[SuccessIndicator] = Field(default_factory=list)
    performance_descriptors: list[PerformanceDescriptor] = Field(default_factory=list)
    evidence_definitions: list[CriterionEvidence] = Field(default_factory=list)
    
    # Marks
    total_marks: int
    marks_percentage: float
    
    # Teacher-specific
    teacher_notes: Optional[str] = None
    common_misconceptions: list[str] = Field(default_factory=list)


class PerformanceLevel(BaseModel):
    """Performance level definition"""
    level: str
    description: str
    marks_range: tuple[int, int]
    colour_code: str  # For PDF formatting
    generic_characteristics: list[str] = Field(default_factory=list)


# ============================================================================
# OUTPUT CONTRACT - RUBRIC MATRIX
# ============================================================================

class LearningOutcomeAlignment(BaseModel):
    """Learning outcome alignment entry"""
    learning_outcome_id: str
    learning_outcome_statement: str
    concepts: list[str] = Field(default_factory=list)
    competencies: list[str] = Field(default_factory=list)
    assessment_criterion: str
    criterion_id: str
    performance_indicators: list[str] = Field(default_factory=list)
    evidence: str


class LearningOutcomeAlignmentMatrix(BaseModel):
    """Learning Outcome Alignment Matrix output"""
    alignments: list[LearningOutcomeAlignment] = Field(default_factory=list)
    coverage_percentage: float
    total_outcomes: int
    aligned_outcomes: int


class RubricMatrix(BaseModel):
    """Complete Rubric Matrix JSON output"""
    # Header info
    rubric_id: str = Field(default_factory=lambda: str(uuid4()))
    assessment_information: AssignmentInformation
    context: ContextIntelligence
    
    # Core rubric
    criteria: list[RubricCriterion] = Field(default_factory=list)
    performance_levels: list[PerformanceLevel] = Field(default_factory=list)
    
    # Alignment
    learning_outcome_alignment: LearningOutcomeAlignmentMatrix
    
    # Marks distribution
    marks_distribution: dict[str, float] = Field(default_factory=dict)
    total_marks: int
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    cio_centric: bool = True
    version: str = "1.0"
    
    class Config:
        use_enum_values = True


# ============================================================================
# OUTPUT CONTRACT - PDF CONTENT
# ============================================================================

class TeacherRubricContent(BaseModel):
    """Content for Teacher Rubric PDF"""
    # Header
    assignment_name: str
    board: str
    grade: int
    subject: str
    chapter: str
    total_marks: int
    assessment_type: str
    
    # Learning Outcomes Section
    learning_outcomes: list[dict] = Field(default_factory=list)
    
    # Concept Coverage
    concepts_covered: list[dict] = Field(default_factory=list)
    
    # Rubric Criteria
    criteria: list[RubricCriterion] = Field(default_factory=list)
    
    # Performance Levels
    performance_levels: list[PerformanceLevel] = Field(default_factory=list)
    
    # Marks Summary
    marks_summary: dict[str, int] = Field(default_factory=dict)
    
    # Teacher Notes
    teacher_notes: str = ""
    common_misconceptions: list[str] = Field(default_factory=list)
    
    # Footer
    generated_date: str = ""
    rubric_id: str = ""


class StudentRubricContent(BaseModel):
    """Content for Student Rubric PDF"""
    # Header
    assignment_name: str
    subject: str
    grade: int
    total_marks: int
    
    # Simplified criteria for students
    criteria: list[dict] = Field(default_factory=list)
    
    # Performance indicators (simplified)
    performance_indicators: list[dict] = Field(default_factory=list)
    
    # Success criteria (simplified)
    success_criteria: list[str] = Field(default_factory=list)
    
    # Self-assessment checklist
    self_assessment_checklist: list[dict] = Field(default_factory=list)
    
    # Footer
    generated_date: str = ""


# ============================================================================
# OUTPUT CONTRACT - COMPLETE RESPONSE
# ============================================================================

class RubricGenerationResponse(BaseModel):
    """Complete output contract for rubric generation"""
    request_id: str
    status: str  # success, partial, failed
    
    # Outputs
    rubric_matrix: Optional[RubricMatrix] = None
    teacher_rubric_pdf_path: Optional[str] = None
    student_rubric_pdf_path: Optional[str] = None
    
    # Content for custom rendering
    teacher_content: Optional[TeacherRubricContent] = None
    student_content: Optional[StudentRubricContent] = None
    
    # Alignment verification
    alignment_verified: bool = False
    alignment_coverage: float = 0.0
    
    # Metadata
    generation_time_seconds: float = 0.0
    cios_used: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
