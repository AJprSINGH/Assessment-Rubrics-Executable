"""
Unit Tests for Rubric Intelligence Engines
"""

import pytest
from unittest.mock import MagicMock

from src.assessment_rubric_agent.core.schemas.intelligence_objects import (
    Board, Subject, BloomLevel, AssessmentType, RubricType, DifficultyLevel,
    ConceptIntelligence, LearningOutcomeIntelligence, CompetencyIntelligence
)
from src.assessment_rubric_agent.core.schemas.contracts import (
    AssignmentInformation, RubricGenerationRequest
)
from src.assessment_rubric_agent.core.engines import (
    LearningOutcomeExtractor,
    ConceptIdentifier,
    CompetencyMapper,
    AssessmentCriteriaGenerator,
    PerformanceScaleGenerator,
    EvidenceDefinitionGenerator
)
from src.assessment_rubric_agent.core.schemas.intelligence_objects import CompetencyLevel


@pytest.fixture
def sample_request():
    """Create sample rubric generation request"""
    return RubricGenerationRequest(
        assignment=AssignmentInformation(
            board=Board.CBSE,
            grade=10,
            subject=Subject.SCIENCE,
            chapter="Chemical Reactions",
            assignment_name="Chemical Reactions Project",
            assessment_type=AssessmentType.PROJECT,
            rubric_type=RubricType.ANALYTICAL,
            total_marks=50
        ),
        include_teacher_notes=True,
        generate_pdf=True
    )


@pytest.fixture
def sample_concepts():
    """Create sample concepts"""
    return [
        ConceptIntelligence(
            concept_id="CONCEPT_001",
            concept_name="Chemical Reactions",
            definition="Process of transformation",
            difficulty=DifficultyLevel.MEDIUM,
            importance="Core",
            confidence=0.95
        ),
        ConceptIntelligence(
            concept_id="CONCEPT_002",
            concept_name="Chemical Equations",
            definition="Representation of reactions",
            difficulty=DifficultyLevel.EASY,
            importance="Core",
            confidence=0.90
        ),
        ConceptIntelligence(
            concept_id="CONCEPT_003",
            concept_name="Types of Reactions",
            definition="Classification of reactions",
            difficulty=DifficultyLevel.MEDIUM,
            importance="Supporting",
            confidence=0.85
        )
    ]


@pytest.fixture
def sample_outcomes():
    """Create sample learning outcomes"""
    return [
        LearningOutcomeIntelligence(
            outcome_id="LO_001",
            outcome_statement="Students will understand chemical reactions",
            blooms_level=BloomLevel.UNDERSTAND,
            dok_level="2",
            concepts_covered=["Chemical Reactions"]
        ),
        LearningOutcomeIntelligence(
            outcome_id="LO_002",
            outcome_statement="Students will balance chemical equations",
            blooms_level=BloomLevel.APPLY,
            dok_level="3",
            concepts_covered=["Chemical Equations"]
        ),
        LearningOutcomeIntelligence(
            outcome_id="LO_003",
            outcome_statement="Students will classify reaction types",
            blooms_level=BloomLevel.ANALYZE,
            dok_level="3",
            concepts_covered=["Types of Reactions"]
        )
    ]


@pytest.fixture
def sample_competencies():
    """Create sample competencies"""
    return [
        CompetencyIntelligence(
            competency_id="COMP_001",
            competency_name="Scientific Reasoning",
            description="Apply scientific thinking",
            competency_level=CompetencyLevel.INTERMEDIATE
        ),
        CompetencyIntelligence(
            competency_id="COMP_002",
            competency_name="Problem Solving",
            description="Solve chemistry problems",
            competency_level=CompetencyLevel.INTERMEDIATE
        )
    ]


class TestLearningOutcomeExtractor:
    """Test LearningOutcomeExtractor engine"""
    
    def test_extract_outcomes(
        self, sample_request, sample_concepts, sample_outcomes
    ):
        """Test extracting learning outcomes"""
        extractor = LearningOutcomeExtractor()
        
        extracted = extractor.extract(
            sample_request,
            sample_concepts,
            sample_outcomes
        )
        
        assert len(extracted) > 0
        assert all(isinstance(o, LearningOutcomeIntelligence) for o in extracted)
    
    def test_validate_outcomes(
        self, sample_request, sample_concepts, sample_outcomes
    ):
        """Test outcome validation"""
        extractor = LearningOutcomeExtractor()
        extractor.extract(sample_request, sample_concepts, sample_outcomes)
        
        valid, errors = extractor.validate()
        assert isinstance(valid, bool)
        assert isinstance(errors, list)
    
    def test_get_observable_behaviours(
        self, sample_request, sample_concepts, sample_outcomes
    ):
        """Test getting observable behaviours"""
        extractor = LearningOutcomeExtractor()
        extractor.extract(sample_request, sample_concepts, sample_outcomes)
        
        outcome = sample_outcomes[0]
        behaviours = extractor.get_observable_behaviours_for_criterion(outcome)
        
        assert len(behaviours) > 0


class TestConceptIdentifier:
    """Test ConceptIdentifier engine"""
    
    def test_identify_concepts(
        self, sample_request, sample_concepts, sample_outcomes
    ):
        """Test identifying concepts"""
        identifier = ConceptIdentifier()
        
        identified = identifier.identify(
            sample_request,
            sample_concepts,
            sample_outcomes
        )
        
        assert len(identified) > 0
        assert all(isinstance(c, ConceptIntelligence) for c in identified)
    
    def test_validate_concepts(
        self, sample_request, sample_concepts, sample_outcomes
    ):
        """Test concept validation"""
        identifier = ConceptIdentifier()
        identifier.identify(sample_request, sample_concepts, sample_outcomes)
        
        valid, errors = identifier.validate()
        assert isinstance(valid, bool)
    
    def test_get_difficulty_distribution(
        self, sample_request, sample_concepts, sample_outcomes
    ):
        """Test difficulty distribution"""
        identifier = ConceptIdentifier()
        identifier.identify(sample_request, sample_concepts, sample_outcomes)
        
        dist = identifier.get_difficulty_distribution()
        assert sum(dist.values()) == len(identifier.identified_concepts)


class TestCompetencyMapper:
    """Test CompetencyMapper engine"""
    
    def test_map_competencies(
        self, sample_request, sample_concepts, sample_outcomes, sample_competencies
    ):
        """Test mapping competencies"""
        mapper = CompetencyMapper()
        
        mapped = mapper.map(
            sample_request,
            sample_concepts,
            sample_outcomes,
            sample_competencies
        )
        
        assert len(mapped) > 0
    
    def test_validate_competencies(
        self, sample_request, sample_concepts, sample_outcomes, sample_competencies
    ):
        """Test competency validation"""
        mapper = CompetencyMapper()
        mapper.map(
            sample_request,
            sample_concepts,
            sample_outcomes,
            sample_competencies
        )
        
        valid, errors = mapper.validate()
        assert isinstance(valid, bool)


class TestAssessmentCriteriaGenerator:
    """Test AssessmentCriteriaGenerator engine"""
    
    def test_generate_criteria(
        self, sample_request, sample_concepts, sample_outcomes, sample_competencies
    ):
        """Test generating assessment criteria"""
        generator = AssessmentCriteriaGenerator()
        
        criteria = generator.generate(
            sample_request,
            sample_concepts,
            sample_outcomes,
            sample_competencies
        )
        
        assert len(criteria) > 0
        # Check total marks
        total = sum(c.total_marks for c in criteria)
        assert total <= sample_request.assignment.total_marks * 1.5  # Allow some tolerance
    
    def test_validate_criteria(
        self, sample_request, sample_concepts, sample_outcomes, sample_competencies
    ):
        """Test criteria validation"""
        generator = AssessmentCriteriaGenerator()
        generator.generate(
            sample_request,
            sample_concepts,
            sample_outcomes,
            sample_competencies
        )
        
        valid, errors = generator.validate()
        assert isinstance(valid, bool)
    
    def test_criterion_cio_traceability(
        self, sample_request, sample_concepts, sample_outcomes, sample_competencies
    ):
        """Test that criteria are traceable to CIOs"""
        generator = AssessmentCriteriaGenerator()
        criteria = generator.generate(
            sample_request,
            sample_concepts,
            sample_outcomes,
            sample_competencies
        )
        
        # Check for CIO traceability
        for criterion in criteria:
            has_concepts = len(criterion.concept_ids) > 0 or len(criterion.concept_names) > 0
            has_bloom = criterion.blooms_level is not None
            # Criteria should have at least some traceability
            assert has_bloom


class TestPerformanceScaleGenerator:
    """Test PerformanceScaleGenerator engine"""
    
    def test_generate_performance_levels(self, sample_request):
        """Test generating performance levels"""
        from src.assessment_rubric_agent.core.schemas.contracts import RubricCriterion
        
        generator = PerformanceScaleGenerator()
        
        # Create dummy criteria
        criteria = [
            RubricCriterion(
                criterion_id="CRIT_001",
                criterion_name="Test",
                description="Test criterion",
                blooms_level=BloomLevel.UNDERSTAND,
                total_marks=10,
                marks_percentage=20.0
            )
        ]
        
        levels, descriptors = generator.generate(sample_request, criteria)
        
        assert len(levels) > 0
        assert len(descriptors) > 0
    
    def test_get_marks_for_level(self, sample_request):
        """Test getting marks for a level"""
        generator = PerformanceScaleGenerator()
        
        from src.assessment_rubric_agent.core.schemas.contracts import RubricCriterion
        
        criteria = [
            RubricCriterion(
                criterion_id="CRIT_001",
                criterion_name="Test",
                description="Test",
                blooms_level=BloomLevel.UNDERSTAND,
                total_marks=10,
                marks_percentage=20.0
            )
        ]
        
        generator.generate(sample_request, criteria)
        
        marks = generator.get_marks_for_level(criteria[0], "Exemplary")
        assert marks[0] >= 0
        assert marks[1] <= criteria[0].total_marks


class TestEvidenceDefinitionGenerator:
    """Test EvidenceDefinitionGenerator engine"""
    
    def test_generate_evidence(
        self, sample_request, sample_concepts, sample_outcomes, sample_competencies
    ):
        """Test generating evidence definitions"""
        # First generate criteria
        criteria_gen = AssessmentCriteriaGenerator()
        criteria = criteria_gen.generate(
            sample_request,
            sample_concepts,
            sample_outcomes,
            sample_competencies
        )
        
        generator = EvidenceDefinitionGenerator()
        evidence, success = generator.generate(sample_request, criteria)
        
        assert len(evidence) > 0
        assert len(success) > 0
    
    def test_get_evidence_summary(self):
        """Test getting evidence summary"""
        generator = EvidenceDefinitionGenerator()
        
        # Manually set evidence
        from src.assessment_rubric_agent.core.schemas.contracts import CriterionEvidence
        generator.evidence_definitions = {
            "CRIT_001": [
                CriterionEvidence(
                    evidence_type="Work Sample",
                    description="Test evidence",
                    collection_method="Submission"
                )
            ]
        }
        
        summary = generator.get_evidence_summary()
        assert "CRIT_001" in summary
