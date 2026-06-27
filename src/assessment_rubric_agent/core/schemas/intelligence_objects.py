"""
Core Intelligence Objects (CIOs) for Assessment Rubric Agent v0.1
All Pydantic schemas representing the intelligence layer.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================

class Board(str, Enum):
    CBSE = "CBSE"
    ICSE = "ICSE"
    STATE = "State Board"
    IB = "IB"
    CAMBRIDGE = "Cambridge"


class Subject(str, Enum):
    SCIENCE = "Science"
    MATHEMATICS = "Mathematics"
    ENGLISH = "English"
    SOCIAL_STUDIES = "Social Studies"
    HINDI = "Hindi"


class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class DOKLevel(str, Enum):
    L1 = "1"
    L2 = "2"
    L3 = "3"
    L4 = "4"


class AssessmentType(str, Enum):
    PROJECT = "Project"
    ASSIGNMENT = "Assignment"
    LAB_WORK = "Lab Work"
    PRESENTATION = "Presentation"
    PORTFOLIO = "Portfolio"
    PERFORMANCE_TASK = "Performance Task"


class RubricType(str, Enum):
    ANALYTICAL = "Analytical"
    HOLISTIC = "Holistic"
    CHECKLIST = "Checklist"
    POINT_RUBRIC = "Point Rubric"


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class KnowledgeType(str, Enum):
    FACT = "Fact"
    CONCEPT = "Concept"
    PRINCIPLE = "Principle"
    UNDERSTANDING = "Understanding"
    DEFINITION = "Definition"


class CompetencyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


# ============================================================================
# CURRICULUM INTELLIGENCE
# ============================================================================

class CurriculumIntelligence(BaseModel):
    """Curriculum Intelligence - Board, Grade, Subject, Unit, Chapter"""
    board: Board
    grade: int = Field(ge=1, le=12)
    subject: Subject
    unit: Optional[str] = None
    chapter: str
    chapter_summary: Optional[str] = None
    standard: Optional[str] = None
    standard_id: Optional[str] = None


# ============================================================================
# CONCEPT INTELLIGENCE
# ============================================================================

class KnowledgeItem(BaseModel):
    """Individual knowledge item within a concept"""
    knowledge: str
    statement: str
    knowledge_type: KnowledgeType
    confidence: float = Field(ge=0.0, le=1.0)
    concept_name: str


class AbilityItem(BaseModel):
    """Ability associated with a concept"""
    ability: str
    verb: str
    description: str
    knowledge_refs: list[str] = Field(default_factory=list)
    concept_name: str
    blooms_level: Optional[BloomLevel] = None


class SkillItem(BaseModel):
    """Skill associated with a concept"""
    skill: str
    description: str
    concept_name: str
    related_concepts: list[str] = Field(default_factory=list)


class ConceptIntelligence(BaseModel):
    """Concept Intelligence Object"""
    concept_id: str
    concept_name: str
    concept_type: str = "Concept"
    definition: Optional[str] = None
    importance: str = "Core"  # Core, Supporting, Extended
    difficulty: DifficultyLevel
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list)
    abilities: list[AbilityItem] = Field(default_factory=list)
    skills: list[SkillItem] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    related_concepts: list[str] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)
    real_world_applications: list[str] = Field(default_factory=list)
    pedagogy_suggestions: list[str] = Field(default_factory=list)


# ============================================================================
# LEARNING OUTCOME INTELLIGENCE
# ============================================================================

class ObservableBehaviour(BaseModel):
    """Observable behaviour for assessment"""
    behaviour: str
    description: str
    blooms_level: BloomLevel
    assessment_method: list[str] = Field(default_factory=list)


class LearningObjective(BaseModel):
    """Learning objective"""
    objective: str
    blooms_level: BloomLevel
    dok_level: DOKLevel
    difficulty: DifficultyLevel


class LearningOutcomeIntelligence(BaseModel):
    """Learning Outcome Intelligence Object"""
    outcome_id: str
    outcome_statement: str
    objectives: list[LearningObjective] = Field(default_factory=list)
    observable_behaviours: list[ObservableBehaviour] = Field(default_factory=list)
    concepts_covered: list[str] = Field(default_factory=list)
    blooms_level: BloomLevel
    dok_level: DOKLevel


# ============================================================================
# BLOOM INTELLIGENCE
# ============================================================================

class CognitiveVerb(BaseModel):
    """Cognitive action verb for Bloom's level"""
    verb: str
    bloom_level: BloomLevel
    example_usage: Optional[str] = None


class BloomIntelligence(BaseModel):
    """Bloom Intelligence - cognitive verbs and complexity"""
    level: BloomLevel
    description: str
    cognitive_verbs: list[str]
    complexity_weight: float = Field(ge=0.0, le=1.0)


# ============================================================================
# KSA INTELLIGENCE
# ============================================================================

class KSAIntelligence(BaseModel):
    """Knowledge, Skills, and Abilities Intelligence"""
    # Knowledge
    knowledge: list[KnowledgeItem] = Field(default_factory=list)
    
    # Skills
    problem_solving: list[str] = Field(default_factory=list)
    communication: list[str] = Field(default_factory=list)
    collaboration: list[str] = Field(default_factory=list)
    creativity: list[str] = Field(default_factory=list)
    application: list[str] = Field(default_factory=list)
    
    # Abilities
    reasoning: list[str] = Field(default_factory=list)
    critical_thinking: list[str] = Field(default_factory=list)
    transfer_learning: list[str] = Field(default_factory=list)
    decision_making: list[str] = Field(default_factory=list)
    
    # Aggregated
    all_verbs: list[str] = Field(default_factory=list)
    all_abilities: list[str] = Field(default_factory=list)
    all_skills: list[str] = Field(default_factory=list)


# ============================================================================
# COMPETENCY INTELLIGENCE
# ============================================================================

class PerformanceIndicator(BaseModel):
    """Performance indicator for competency"""
    indicator: str
    description: str
    competency_level: CompetencyLevel
    blooms_level: BloomLevel
    observable: bool = True


class CompetencyIntelligence(BaseModel):
    """Competency Intelligence Object"""
    competency_id: str
    competency_name: str
    description: str
    performance_indicators: list[PerformanceIndicator] = Field(default_factory=list)
    competency_level: CompetencyLevel
    related_concepts: list[str] = Field(default_factory=list)
    related_outcomes: list[str] = Field(default_factory=list)


# ============================================================================
# ASSESSMENT INTELLIGENCE
# ============================================================================

class SuccessCriterion(BaseModel):
    """Success criterion for assessment"""
    criterion: str
    description: str
    blooms_level: BloomLevel
    marks_weightage: float
    evidence_required: list[str] = Field(default_factory=list)


class EvidenceOfLearning(BaseModel):
    """Evidence of learning definition"""
    evidence_type: str
    description: str
    collection_method: str
    rubric_alignment: Optional[str] = None


class AssessmentBlueprint(BaseModel):
    """Assessment blueprint from intelligence"""
    assessment_type: AssessmentType
    bloom_level: BloomLevel
    dok_level: DOKLevel
    difficulty: DifficultyLevel
    marks: int
    recommended_question: Optional[str] = None


class AssessmentIntelligence(BaseModel):
    """Assessment Intelligence Object"""
    assessment_types: list[AssessmentType] = Field(default_factory=list)
    rubric_type: RubricType
    assessment_weightage: dict[str, float] = Field(default_factory=dict)
    performance_scale: list[str] = Field(default_factory=list)
    success_criteria: list[SuccessCriterion] = Field(default_factory=list)
    evidence_of_learning: list[EvidenceOfLearning] = Field(default_factory=list)
    assessment_blueprints: list[AssessmentBlueprint] = Field(default_factory=list)


# ============================================================================
# PEDAGOGICAL & MISCONCEPTION INTELLIGENCE
# ============================================================================

class PedagogicalIntelligence(BaseModel):
    """Pedagogical Intelligence"""
    strategies: list[str] = Field(default_factory=list)
    assessment_modalities: list[str] = Field(default_factory=list)
    differentiation_strategies: list[str] = Field(default_factory=list)
    engagement_techniques: list[str] = Field(default_factory=list)


class MisconceptionIntelligence(BaseModel):
    """Misconception Intelligence"""
    common_errors: list[str] = Field(default_factory=list)
    learning_gaps: list[str] = Field(default_factory=list)
    misconception_indicators: list[str] = Field(default_factory=list)
    targeted_remediation: list[str] = Field(default_factory=list)


# ============================================================================
# FULL INTELLIGENCE OBJECT
# ============================================================================

class FullIntelligenceObject(BaseModel):
    """Aggregated Intelligence Object combining all CIOs"""
    curriculum: CurriculumIntelligence
    concepts: list[ConceptIntelligence] = Field(default_factory=list)
    learning_outcomes: list[LearningOutcomeIntelligence] = Field(default_factory=list)
    blooms: list[BloomIntelligence] = Field(default_factory=list)
    ksa: KSAIntelligence = Field(default_factory=KSAIntelligence)
    competencies: list[CompetencyIntelligence] = Field(default_factory=list)
    assessment: AssessmentIntelligence = Field(default_factory=AssessmentIntelligence)
    pedagogy: PedagogicalIntelligence = Field(default_factory=PedagogicalIntelligence)
    misconceptions: MisconceptionIntelligence = Field(default_factory=MisconceptionIntelligence)
    
    # Metadata
    extraction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    llm_model: Optional[str] = None
    
    class Config:
        use_enum_values = True
