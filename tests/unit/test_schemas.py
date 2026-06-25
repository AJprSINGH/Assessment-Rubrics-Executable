"""
Unit Tests for Pydantic Schemas
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.assessment_rubric_agent.core.schemas.intelligence_objects import (
    Board, Subject, BloomLevel, AssessmentType, RubricType,
    CurriculumIntelligence, ConceptIntelligence, LearningOutcomeIntelligence,
    KSAIntelligence, DifficultyLevel, KnowledgeType
)
from src.assessment_rubric_agent.core.schemas.contracts import (
    AssignmentInformation, RubricGenerationRequest, ContextIntelligence,
    RubricCriterion, PerformanceLevel, RubricMatrix
)


class TestIntelligenceObjects:
    """Test intelligence object schemas"""
    
    def test_curriculum_intelligence(self):
        """Test CurriculumIntelligence creation"""
        curriculum = CurriculumIntelligence(
            board=Board.CBSE,
            grade=10,
            subject=Subject.SCIENCE,
            chapter="Chemical Reactions",
            standard="Class 10 Science"
        )
        
        assert curriculum.board == Board.CBSE
        assert curriculum.grade == 10
        assert curriculum.subject == Subject.SCIENCE
        assert curriculum.chapter == "Chemical Reactions"
    
    def test_concept_intelligence(self):
        """Test ConceptIntelligence creation"""
        concept = ConceptIntelligence(
            concept_id="CHEM_001",
            concept_name="Chemical Reactions",
            definition="Process of transformation",
            difficulty=DifficultyLevel.MEDIUM,
            confidence=0.95
        )
        
        assert concept.concept_id == "CHEM_001"
        assert concept.concept_name == "Chemical Reactions"
        assert concept.difficulty == DifficultyLevel.MEDIUM
        assert concept.confidence == 0.95
    
    def test_learning_outcome_intelligence(self):
        """Test LearningOutcomeIntelligence creation"""
        outcome = LearningOutcomeIntelligence(
            outcome_id="LO_001",
            outcome_statement="Students will understand chemical reactions",
            blooms_level=BloomLevel.UNDERSTAND,
            dok_level="2"
        )
        
        assert outcome.outcome_id == "LO_001"
        assert outcome.blooms_level == BloomLevel.UNDERSTAND
    
    def test_ksa_intelligence(self):
        """Test KSAIntelligence creation"""
        ksa = KSAIntelligence(
            problem_solving=["Analyze problems", "Apply solutions"],
            reasoning=["Logical reasoning"],
            critical_thinking=["Evaluate evidence"]
        )
        
        assert len(ksa.problem_solving) == 2
        assert "Logical reasoning" in ksa.reasoning


class TestContracts:
    """Test contract schemas"""
    
    def test_assignment_information_valid(self):
        """Test valid AssignmentInformation"""
        assignment = AssignmentInformation(
            board=Board.CBSE,
            grade=6,
            subject=Subject.SCIENCE,
            chapter="Friction",
            assignment_name="Friction Project",
            assessment_type=AssessmentType.PROJECT,
            rubric_type=RubricType.ANALYTICAL,
            total_marks=50,
            performance_scale=["Exemplary", "Proficient", "Developing", "Beginning"]
        )
        
        assert assignment.grade == 6
        assert assignment.total_marks == 50
        assert len(assignment.performance_scale) == 4
    
    def test_assignment_information_invalid_marks(self):
        """Test AssignmentInformation with invalid marks"""
        with pytest.raises(ValidationError):
            AssignmentInformation(
                board=Board.CBSE,
                grade=6,
                subject=Subject.SCIENCE,
                chapter="Friction",
                assignment_name="Friction Project",
                total_marks=0  # Invalid: must be >= 1
            )
    
    def test_assignment_information_invalid_scale(self):
        """Test AssignmentInformation with invalid performance scale"""
        with pytest.raises(ValidationError):
            AssignmentInformation(
                board=Board.CBSE,
                grade=6,
                subject=Subject.SCIENCE,
                chapter="Friction",
                assignment_name="Friction Project",
                total_marks=50,
                performance_scale=["Only One"]  # Invalid: must have at least 2
            )
    
    def test_context_intelligence(self):
        """Test ContextIntelligence creation"""
        context = ContextIntelligence(
            class_size=35,
            student_profile="Mixed ability",
            time_duration="2 weeks",
            available_resources=["Textbook", "Lab equipment"]
        )
        
        assert context.class_size == 35
        assert len(context.available_resources) == 2
    
    def test_rubric_generation_request(self):
        """Test RubricGenerationRequest creation"""
        request = RubricGenerationRequest(
            assignment=AssignmentInformation(
                board=Board.CBSE,
                grade=6,
                subject=Subject.SCIENCE,
                chapter="Friction",
                assignment_name="Friction Project",
                total_marks=50
            ),
            include_teacher_notes=True,
            generate_pdf=True
        )
        
        assert request.cio_centric_mode is True  # Default
        assert request.generate_pdf is True


class TestRubricCriterion:
    """Test RubricCriterion schema"""
    
    def test_criterion_creation(self):
        """Test RubricCriterion creation"""
        criterion = RubricCriterion(
            criterion_id="CRIT_001",
            criterion_name="Concept Understanding",
            description="Demonstrates understanding of key concepts",
            blooms_level=BloomLevel.UNDERSTAND,
            total_marks=10,
            marks_percentage=20.0
        )
        
        assert criterion.criterion_id == "CRIT_001"
        assert criterion.total_marks == 10
        assert criterion.blooms_level == BloomLevel.UNDERSTAND


class TestPerformanceLevel:
    """Test PerformanceLevel schema"""
    
    def test_performance_level_creation(self):
        """Test PerformanceLevel creation"""
        level = PerformanceLevel(
            level="Exemplary",
            description="Exceeds expectations",
            marks_range=(90, 100),
            colour_code="#2E7D32"
        )
        
        assert level.level == "Exemplary"
        assert level.marks_range == (90, 100)
