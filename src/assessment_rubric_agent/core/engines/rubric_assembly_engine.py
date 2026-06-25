"""
Rubric Assembly Engine
Assembles all components into final rubric structure.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..schemas.intelligence_objects import (
    ConceptIntelligence, LearningOutcomeIntelligence, CompetencyIntelligence,
    BloomLevel
)
from ..schemas.contracts import PerformanceLevel
from ..schemas.contracts import (
    RubricGenerationRequest, RubricCriterion, PerformanceDescriptor,
    RubricMatrix, LearningOutcomeAlignment, LearningOutcomeAlignmentMatrix,
    TeacherRubricContent, StudentRubricContent
)

logger = logging.getLogger(__name__)


class RubricAssemblyEngine:
    """
    Assembles all rubric components into final outputs:
    - Rubric Matrix JSON
    - Teacher Rubric Content
    - Student Rubric Content
    """
    
    def __init__(self):
        self.rubric_matrix: Optional[RubricMatrix] = None
        self.teacher_content: Optional[TeacherRubricContent] = None
        self.student_content: Optional[StudentRubricContent] = None
    
    def assemble(
        self,
        request: RubricGenerationRequest,
        criteria: list[RubricCriterion],
        performance_levels: list[PerformanceLevel],
        criterion_descriptors: dict[str, list[PerformanceDescriptor]],
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence],
        competencies: list[CompetencyIntelligence],
        marks_distribution: dict[str, float]
    ) -> tuple[RubricMatrix, TeacherRubricContent, StudentRubricContent]:
        """
        Assemble all components into final rubric structures.
        
        Args:
            request: The rubric generation request
            criteria: Generated rubric criteria
            performance_levels: Performance level definitions
            criterion_descriptors: Performance descriptors per criterion
            concepts: Identified concepts
            learning_outcomes: Selected learning outcomes
            competencies: Mapped competencies
            marks_distribution: Marks distribution across criteria
            
        Returns:
            Tuple of (rubric_matrix, teacher_content, student_content)
        """
        logger.info("Assembling final rubric")
        
        # Assign descriptors to criteria
        for criterion in criteria:
            criterion.performance_descriptors = criterion_descriptors.get(
                criterion.criterion_id, []
            )
        
        # Generate alignment matrix
        alignment_matrix = self._generate_alignment_matrix(
            criteria, learning_outcomes, concepts, competencies
        )
        
        # Create rubric matrix
        self.rubric_matrix = RubricMatrix(
            rubric_id=f"RUBRIC_{uuid4().hex[:8].upper()}",
            assessment_information=request.assignment,
            context=request.context,
            criteria=criteria,
            performance_levels=performance_levels,
            learning_outcome_alignment=alignment_matrix,
            marks_distribution=marks_distribution,
            total_marks=request.assignment.total_marks,
            cio_centric=request.cio_centric_mode
        )
        
        # Create teacher content
        self.teacher_content = self._create_teacher_content(
            request, criteria, performance_levels, 
            criterion_descriptors, concepts, learning_outcomes
        )
        
        # Create student content
        self.student_content = self._create_student_content(
            request, criteria, performance_levels, criterion_descriptors
        )
        
        logger.info("Rubric assembly complete")
        return self.rubric_matrix, self.teacher_content, self.student_content
    
    def _generate_alignment_matrix(
        self,
        criteria: list[RubricCriterion],
        learning_outcomes: list[LearningOutcomeIntelligence],
        concepts: list[ConceptIntelligence],
        competencies: list[CompetencyIntelligence]
    ) -> LearningOutcomeAlignmentMatrix:
        """Generate learning outcome alignment matrix"""
        alignments = []
        
        concept_map = {c.concept_name: c for c in concepts}
        competency_map = {c.competency_id: c for c in competencies}
        
        for outcome in learning_outcomes:
            # Find criteria that align with this outcome
            aligned_criteria = [
                c for c in criteria
                if outcome.outcome_id in c.learning_outcome_ids
            ]
            
            # If no direct alignment, find related criteria
            if not aligned_criteria:
                outcome_concepts = set(outcome.concepts_covered)
                aligned_criteria = [
                    c for c in criteria
                    if set(c.concept_names) & outcome_concepts
                ]
            
            # Get aligned concepts
            aligned_concepts = list(set(
                concept for c in aligned_criteria for concept in c.concept_names
            ))
            
            # Get aligned competencies
            aligned_comp_ids = list(set(
                comp_id for c in aligned_criteria for comp_id in c.competency_ids
            ))
            aligned_comps = [
                competency_map.get(cid, None) 
                for cid in aligned_comp_ids
                if cid in competency_map
            ]
            
            # Get performance indicators
            indicators = []
            for criterion in aligned_criteria[:1]:
                for indicator in criterion.success_indicators[:2]:
                    indicators.append(indicator.indicator)
            
            alignments.append(LearningOutcomeAlignment(
                learning_outcome_id=outcome.outcome_id,
                learning_outcome_statement=outcome.outcome_statement,
                concepts=aligned_concepts,
                competencies=[c.competency_name for c in aligned_comps if c],
                assessment_criterion=aligned_criteria[0].criterion_name if aligned_criteria else "General Assessment",
                criterion_id=aligned_criteria[0].criterion_id if aligned_criteria else "",
                performance_indicators=indicators,
                evidence=", ".join([
                    e.evidence_type 
                    for c in aligned_criteria 
                    for e in c.evidence_definitions[:1]
                ]) or "Work sample submission"
            ))
        
        # Calculate coverage
        total_outcomes = len(learning_outcomes)
        aligned_outcomes = len([a for a in alignments if a.criterion_id])
        coverage = (aligned_outcomes / total_outcomes * 100) if total_outcomes > 0 else 100.0
        
        return LearningOutcomeAlignmentMatrix(
            alignments=alignments,
            coverage_percentage=coverage,
            total_outcomes=total_outcomes,
            aligned_outcomes=aligned_outcomes
        )
    
    def _create_teacher_content(
        self,
        request: RubricGenerationRequest,
        criteria: list[RubricCriterion],
        performance_levels: list[PerformanceLevel],
        criterion_descriptors: dict[str, list[PerformanceDescriptor]],
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence]
    ) -> TeacherRubricContent:
        """Create content for teacher rubric PDF"""
        
        # Format learning outcomes
        learning_outcomes_formatted = [
            {
                "id": lo.outcome_id,
                "statement": lo.outcome_statement,
                "blooms_level": lo.blooms_level.value if lo.blooms_level else "Understand"
            }
            for lo in learning_outcomes
        ]
        
        # Format concepts
        concepts_formatted = [
            {
                "name": c.concept_name,
                "difficulty": c.difficulty.value if c.difficulty else "Medium",
                "importance": c.importance
            }
            for c in concepts
        ]
        
        # Marks summary
        marks_summary = {
            c.criterion_name: c.total_marks
            for c in criteria
        }
        
        # Collect teacher notes
        teacher_notes = self._generate_teacher_notes(criteria, concepts)
        
        # Collect misconceptions
        all_misconceptions = []
        for concept in concepts:
            all_misconceptions.extend(concept.misconceptions[:2])
        
        return TeacherRubricContent(
            assignment_name=request.assignment.assignment_name,
            board=request.assignment.board.value if request.assignment.board else "CBSE",
            grade=request.assignment.grade,
            subject=request.assignment.subject.value if request.assignment.subject else "Science",
            chapter=request.assignment.chapter,
            total_marks=request.assignment.total_marks,
            assessment_type=request.assignment.assessment_type.value if request.assignment.assessment_type else "Project",
            learning_outcomes=learning_outcomes_formatted,
            concepts_covered=concepts_formatted,
            criteria=criteria,
            performance_levels=performance_levels,
            marks_summary=marks_summary,
            teacher_notes=teacher_notes,
            common_misconceptions=all_misconceptions[:5],
            generated_date=datetime.now().strftime("%B %d, %Y"),
            rubric_id=self.rubric_matrix.rubric_id if self.rubric_matrix else ""
        )
    
    def _create_student_content(
        self,
        request: RubricGenerationRequest,
        criteria: list[RubricCriterion],
        performance_levels: list[PerformanceLevel],
        criterion_descriptors: dict[str, list[PerformanceDescriptor]]
    ) -> StudentRubricContent:
        """Create content for student rubric PDF"""
        
        # Simplified criteria for students
        student_criteria = []
        for criterion in criteria:
            # Get the best descriptor for each criterion
            descriptors = criterion_descriptors.get(criterion.criterion_id, [])
            best_descriptor = descriptors[0] if descriptors else None
            
            student_criteria.append({
                "name": criterion.criterion_name,
                "description": criterion.description,
                "total_marks": criterion.total_marks,
                "key_expectation": best_descriptor.description if best_descriptor else criterion.description,
                "levels": [
                    {
                        "level": d.level,
                        "description": d.description,
                        "marks_range": f"{d.marks_range[0]}-{d.marks_range[1]}"
                    }
                    for d in descriptors
                ]
            })
        
        # Performance indicators (simplified)
        performance_indicators = [
            {
                "criterion": c.criterion_name,
                "indicators": [ind.indicator for ind in c.success_indicators[:3]]
            }
            for c in criteria
        ]
        
        # Success criteria (simplified statements)
        success_criteria = [
            f"✓ I can {c.success_indicators[0].indicator.lower() if c.success_indicators else c.description.lower()}"
            for c in criteria
        ]
        
        # Self-assessment checklist
        self_assessment = []
        for i, criterion in enumerate(criteria):
            self_assessment.append({
                "number": i + 1,
                "criterion": criterion.criterion_name,
                "checklist_items": [
                    f"I understand what \"{criterion.criterion_name}\" means",
                    f"I can explain the key concepts",
                    f"I have evidence of my learning"
                ]
            })
        
        return StudentRubricContent(
            assignment_name=request.assignment.assignment_name,
            subject=request.assignment.subject.value if request.assignment.subject else "Science",
            grade=request.assignment.grade,
            total_marks=request.assignment.total_marks,
            criteria=student_criteria,
            performance_indicators=performance_indicators,
            success_criteria=success_criteria,
            self_assessment_checklist=self_assessment,
            generated_date=datetime.now().strftime("%B %d, %Y")
        )
    
    def _generate_teacher_notes(
        self,
        criteria: list[RubricCriterion],
        concepts: list[ConceptIntelligence]
    ) -> str:
        """Generate teacher notes for the rubric"""
        notes = []
        
        notes.append("General Instructions:")
        notes.append("• Use this rubric as a guide for assessment, not a rigid checklist")
        notes.append("• Consider overall performance across criteria")
        notes.append("• Provide specific feedback for each criterion")
        notes.append("")
        
        notes.append("Assessment Tips:")
        notes.append("• Observe students during the process, not just the final product")
        notes.append("• Use the evidence requirements to guide your evaluation")
        notes.append("• Note any misconceptions and address them in feedback")
        notes.append("")
        
        notes.append("Differentiation Suggestions:")
        notes.append("• For struggling students: Focus on core concepts first")
        notes.append("• For advanced students: Encourage extension activities")
        
        return "\n".join(notes)
    
    def get_rubric_matrix(self) -> Optional[RubricMatrix]:
        """Get the assembled rubric matrix"""
        return self.rubric_matrix
    
    def get_teacher_content(self) -> Optional[TeacherRubricContent]:
        """Get teacher rubric content"""
        return self.teacher_content
    
    def get_student_content(self) -> Optional[StudentRubricContent]:
        """Get student rubric content"""
        return self.student_content
