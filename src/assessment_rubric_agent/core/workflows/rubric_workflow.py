"""
Workflow for Assessment Rubric Agent v0.1
Orchestrates the complete rubric generation pipeline.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TypedDict, Optional, Dict, Any, List

from ..schemas.intelligence_objects import (
    FullIntelligenceObject, ConceptIntelligence, LearningOutcomeIntelligence,
    CompetencyIntelligence, BloomLevel
)
from ..schemas.contracts import (
    RubricGenerationRequest, RubricGenerationResponse, RubricMatrix,
    TeacherRubricContent, StudentRubricContent, RubricCriterion, PerformanceLevel
)
from ..engines import (
    LearningOutcomeExtractor, ConceptIdentifier, CompetencyMapper,
    AssessmentCriteriaGenerator, PerformanceScaleGenerator,
    EvidenceDefinitionGenerator, RubricAssemblyEngine
)
from ...services.intelligence_service import IntelligenceService
from ...services.pdf_generation_service import PDFGenerationService
from ...services.json_output_service import JSONOutputService

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State passed through the workflow"""
    request: RubricGenerationRequest
    curriculum_intelligence: Optional[dict]
    concept_intelligence: List[Any]
    learning_outcome_intelligence: List[Any]
    ksa_intelligence: Optional[dict]
    competency_intelligence: List[Any]
    extracted_outcomes: List[Any]
    identified_concepts: List[Any]
    mapped_competencies: List[Any]
    generated_criteria: List[Any]
    performance_levels: List[Any]
    criterion_descriptors: Dict[str, Any]
    marks_distribution: Dict[str, float]
    rubric_matrix: Optional[RubricMatrix]
    teacher_content: Optional[TeacherRubricContent]
    student_content: Optional[StudentRubricContent]
    teacher_pdf_path: Optional[str]
    student_pdf_path: Optional[str]
    json_path: Optional[str]
    errors: List[str]
    warnings: List[str]
    start_time: float
    cios_used: List[str]
    validation_passed: bool
    alignment_coverage: float


class RubricGenerationWorkflow:
    """
    Workflow orchestrating rubric generation.
    
    Steps:
    1. Receive Assessment Request
    2. Load Curriculum Intelligence
    3. Load CIOs
    4. Identify Learning Outcomes
    5. Identify Concepts
    6. Determine Bloom Levels
    7. Determine KSA Requirements
    8. Determine Competencies
    9. Generate Assessment Criteria
    10. Generate Success Indicators
    11. Generate Performance Levels
    12. Generate Evidence Definitions
    13. Generate Marks Distribution
    14. Produce Final Outputs
    """
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.intelligence_service = IntelligenceService(csv_path)
        self.pdf_service = PDFGenerationService()
        self.json_service = JSONOutputService()
        
        # Initialize engines
        self.outcome_extractor = LearningOutcomeExtractor()
        self.concept_identifier = ConceptIdentifier()
        self.competency_mapper = CompetencyMapper()
        self.criteria_generator = AssessmentCriteriaGenerator()
        self.scale_generator = PerformanceScaleGenerator()
        self.evidence_generator = EvidenceDefinitionGenerator()
        self.assembly_engine = RubricAssemblyEngine()
    
    async def execute(self, request: RubricGenerationRequest) -> RubricGenerationResponse:
        """
        Execute the complete workflow.
        
        Args:
            request: The rubric generation request
            
        Returns:
            Complete response with all outputs
        """
        start_time = time.time()
        logger.info(f"Starting rubric generation workflow for: {request.assignment.assignment_name}")
        
        # Initialize state
        state: WorkflowState = {
            "request": request,
            "curriculum_intelligence": None,
            "concept_intelligence": [],
            "learning_outcome_intelligence": [],
            "ksa_intelligence": None,
            "competency_intelligence": [],
            "extracted_outcomes": [],
            "identified_concepts": [],
            "mapped_competencies": [],
            "generated_criteria": [],
            "performance_levels": [],
            "criterion_descriptors": {},
            "marks_distribution": {},
            "rubric_matrix": None,
            "teacher_content": None,
            "student_content": None,
            "teacher_pdf_path": None,
            "student_pdf_path": None,
            "json_path": None,
            "errors": [],
            "warnings": [],
            "start_time": start_time,
            "cios_used": [],
            "validation_passed": False,
            "alignment_coverage": 0.0
        }
        
        # Execute workflow steps sequentially
        try:
            # Step 1-3: Load intelligence
            state = await self._load_intelligence(state)
            
            # Step 4: Extract outcomes
            state = await self._extract_outcomes(state)
            
            # Step 5: Identify concepts
            state = await self._identify_concepts(state)
            
            # Step 6-8: Map competencies
            state = await self._map_competencies(state)
            
            # Step 9: Generate criteria
            state = await self._generate_criteria(state)
            
            # Step 10-11: Generate performance scale
            state = await self._generate_performance_scale(state)
            
            # Step 12: Generate evidence
            state = await self._generate_evidence(state)
            
            # Step 13-14: Assemble rubric
            state = await self._assemble_rubric(state)
            
            # Generate outputs
            state = await self._generate_outputs(state)
            
            # Finalize
            state = await self._finalize(state)
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            state["errors"].append(str(e))
        
        # Build response
        response = RubricGenerationResponse(
            request_id=request.request_id,
            status="success" if state["validation_passed"] else ("partial" if state["rubric_matrix"] else "failed"),
            rubric_matrix=state["rubric_matrix"],
            teacher_rubric_pdf_path=state["teacher_pdf_path"],
            student_rubric_pdf_path=state["student_pdf_path"],
            teacher_content=state["teacher_content"],
            student_content=state["student_content"],
            alignment_verified=state["validation_passed"],
            alignment_coverage=state["alignment_coverage"],
            generation_time_seconds=time.time() - start_time,
            cios_used=state["cios_used"],
            errors=state["errors"],
            warnings=state["warnings"]
        )
        
        logger.info(f"Workflow completed in {time.time() - start_time:.2f}s")
        return response
    
    async def _load_intelligence(self, state: WorkflowState) -> WorkflowState:
        """Step 1-3: Load curriculum intelligence and CIOs"""
        logger.info("Step 1-3: Loading curriculum intelligence and CIOs")
        
        request = state["request"]
        
        try:
            intelligence = self.intelligence_service.load_for_assignment(
                grade=request.assignment.grade,
                subject=str(request.assignment.subject.value if request.assignment.subject else request.assignment.subject),
                chapter=request.assignment.chapter
            )
            
            if intelligence:
                state["curriculum_intelligence"] = intelligence.curriculum.model_dump()
                state["concept_intelligence"] = intelligence.concepts
                state["learning_outcome_intelligence"] = intelligence.learning_outcomes
                state["competency_intelligence"] = intelligence.competencies
                state["ksa_intelligence"] = intelligence.ksa.model_dump() if intelligence.ksa else {}
                
                state["cios_used"] = [
                    f"Concepts: {len(intelligence.concepts)}",
                    f"Learning Outcomes: {len(intelligence.learning_outcomes)}",
                    f"Competencies: {len(intelligence.competencies)}"
                ]
            else:
                state["concept_intelligence"] = request.concept_intelligence or []
                state["learning_outcome_intelligence"] = request.learning_outcome_intelligence or []
                state["competency_intelligence"] = request.competency_intelligence or []
                state["warnings"].append("Using default intelligence - CSV data not found")
            
            logger.info(f"Loaded intelligence: {len(state['concept_intelligence'])} concepts")
            
        except Exception as e:
            state["errors"].append(f"Failed to load intelligence: {str(e)}")
            logger.error(f"Intelligence loading failed: {e}")
        
        return state
    
    async def _extract_outcomes(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Extract relevant learning outcomes"""
        logger.info("Step 4: Extracting learning outcomes")
        
        try:
            outcomes = self.outcome_extractor.extract(
                state["request"],
                state["concept_intelligence"],
                state["learning_outcome_intelligence"]
            )
            state["extracted_outcomes"] = outcomes
            
            valid, errors_list = self.outcome_extractor.validate()
            if not valid:
                state["warnings"].extend(errors_list)
            
            logger.info(f"Extracted {len(outcomes)} learning outcomes")
            
        except Exception as e:
            state["errors"].append(f"Outcome extraction failed: {str(e)}")
        
        return state
    
    async def _identify_concepts(self, state: WorkflowState) -> WorkflowState:
        """Step 5: Identify relevant concepts"""
        logger.info("Step 5: Identifying concepts")
        
        try:
            concepts = self.concept_identifier.identify(
                state["request"],
                state["concept_intelligence"],
                state["extracted_outcomes"]
            )
            state["identified_concepts"] = concepts
            
            logger.info(f"Identified {len(concepts)} concepts")
            
        except Exception as e:
            state["errors"].append(f"Concept identification failed: {str(e)}")
        
        return state
    
    async def _map_competencies(self, state: WorkflowState) -> WorkflowState:
        """Step 6-8: Map competencies to assessment"""
        logger.info("Step 6-8: Mapping competencies")
        
        try:
            competencies = self.competency_mapper.map(
                state["request"],
                state["identified_concepts"],
                state["extracted_outcomes"],
                state["competency_intelligence"]
            )
            state["mapped_competencies"] = competencies
            
            logger.info(f"Mapped {len(competencies)} competencies")
            
        except Exception as e:
            state["errors"].append(f"Competency mapping failed: {str(e)}")
        
        return state
    
    async def _generate_criteria(self, state: WorkflowState) -> WorkflowState:
        """Step 9: Generate assessment criteria"""
        logger.info("Step 9: Generating assessment criteria")
        
        try:
            criteria = self.criteria_generator.generate(
                state["request"],
                state["identified_concepts"],
                state["extracted_outcomes"],
                state["mapped_competencies"]
            )
            state["generated_criteria"] = criteria
            
            valid, errors_list = self.criteria_generator.validate()
            if not valid:
                state["warnings"].extend(errors_list)
            
            logger.info(f"Generated {len(criteria)} criteria")
            
        except Exception as e:
            state["errors"].append(f"Criteria generation failed: {str(e)}")
        
        return state
    
    async def _generate_performance_scale(self, state: WorkflowState) -> WorkflowState:
        """Step 10-11: Generate performance levels and descriptors"""
        logger.info("Step 10-11: Generating performance scale")
        
        try:
            levels, descriptors = self.scale_generator.generate(
                state["request"],
                state["generated_criteria"]
            )
            state["performance_levels"] = levels
            state["criterion_descriptors"] = descriptors
            
            logger.info(f"Generated {len(levels)} performance levels")
            
        except Exception as e:
            state["errors"].append(f"Performance scale generation failed: {str(e)}")
        
        return state
    
    async def _generate_evidence(self, state: WorkflowState) -> WorkflowState:
        """Step 12: Generate evidence definitions"""
        logger.info("Step 12: Generating evidence definitions")
        
        try:
            evidence, success = self.evidence_generator.generate(
                state["request"],
                state["generated_criteria"]
            )
            
            # Update criteria with evidence
            for criterion in state["generated_criteria"]:
                if criterion.criterion_id in evidence:
                    criterion.evidence_definitions = evidence[criterion.criterion_id]
            
            logger.info("Evidence definitions generated")
            
        except Exception as e:
            state["errors"].append(f"Evidence generation failed: {str(e)}")
        
        return state
    
    async def _assemble_rubric(self, state: WorkflowState) -> WorkflowState:
        """Step 13-14: Assemble final rubric"""
        logger.info("Step 13-14: Assembling rubric")
        
        try:
            # Calculate marks distribution
            state["marks_distribution"] = {
                c.criterion_name: c.marks_percentage
                for c in state["generated_criteria"]
            }
            
            # Assemble rubric
            rubric_matrix, teacher_content, student_content = self.assembly_engine.assemble(
                state["request"],
                state["generated_criteria"],
                state["performance_levels"],
                state["criterion_descriptors"],
                state["identified_concepts"],
                state["extracted_outcomes"],
                state["mapped_competencies"],
                state["marks_distribution"]
            )
            
            state["rubric_matrix"] = rubric_matrix
            state["teacher_content"] = teacher_content
            state["student_content"] = student_content
            state["alignment_coverage"] = rubric_matrix.learning_outcome_alignment.coverage_percentage
            state["validation_passed"] = state["alignment_coverage"] >= 70.0
            
            logger.info("Rubric assembled successfully")
            
        except Exception as e:
            state["errors"].append(f"Rubric assembly failed: {str(e)}")
        
        return state
    
    async def _generate_outputs(self, state: WorkflowState) -> WorkflowState:
        """Generate final outputs (PDFs, JSON)"""
        logger.info("Generating outputs")
        
        try:
            # Generate JSON
            if state["request"].generate_json and state["rubric_matrix"]:
                json_path = self.json_service.generate_rubric_json(
                    state["rubric_matrix"],
                    state["request"].request_id
                )
                state["json_path"] = json_path
            
            # Generate Teacher PDF
            if state["request"].generate_pdf and state["teacher_content"]:
                teacher_path = self.pdf_service.generate_teacher_rubric(
                    state["teacher_content"],
                    state["request"].request_id
                )
                state["teacher_pdf_path"] = teacher_path
            
            # Generate Student PDF
            if state["request"].generate_pdf and state["student_content"]:
                student_path = self.pdf_service.generate_student_rubric(
                    state["student_content"],
                    state["request"].request_id
                )
                state["student_pdf_path"] = student_path
            
            logger.info("Outputs generated successfully")
            
        except Exception as e:
            state["errors"].append(f"Output generation failed: {str(e)}")
            state["warnings"].append("PDF/JSON generation failed - check logs")
        
        return state
    
    async def _finalize(self, state: WorkflowState) -> WorkflowState:
        """Finalize workflow"""
        logger.info("Workflow finalizing")
        
        if state["errors"]:
            logger.warning(f"Workflow completed with {len(state['errors'])} errors")
        
        return state
