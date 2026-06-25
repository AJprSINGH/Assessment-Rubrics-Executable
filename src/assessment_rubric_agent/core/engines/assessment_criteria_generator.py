"""
Assessment Criteria Generator Engine
Generates assessment criteria based on CIOs.
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import uuid4

from ..schemas.intelligence_objects import (
    ConceptIntelligence, LearningOutcomeIntelligence, CompetencyIntelligence,
    BloomLevel, ObservableBehaviour, SuccessCriterion
)
from ..schemas.contracts import (
    RubricGenerationRequest, RubricCriterion, ObservableBehaviourDefinition,
    SuccessIndicator, CriterionEvidence
)

logger = logging.getLogger(__name__)


class AssessmentCriteriaGenerator:
    """
    Generates assessment criteria that are traceable to CIOs.
    Each criterion must be linked to:
    - Concepts
    - Learning Outcomes
    - Bloom's Levels
    - KSA Elements
    - Competencies
    """
    
    # Standard rubric criteria templates
    STANDARD_CRITERIA = [
        {
            "name": "Concept Understanding",
            "bloom": BloomLevel.UNDERSTAND,
            "description": "Demonstrates understanding of key concepts and definitions"
        },
        {
            "name": "Application of Knowledge",
            "bloom": BloomLevel.APPLY,
            "description": "Applies concepts to solve problems and complete tasks"
        },
        {
            "name": "Analysis and Evaluation",
            "bloom": BloomLevel.ANALYZE,
            "description": "Analyzes information and evaluates solutions"
        },
        {
            "name": "Creativity and Innovation",
            "bloom": BloomLevel.CREATE,
            "description": "Demonstrates creative thinking and innovative approaches"
        },
        {
            "name": "Communication and Presentation",
            "bloom": BloomLevel.UNDERSTAND,
            "description": "Effectively communicates understanding through various media"
        },
        {
            "name": "Collaboration and Teamwork",
            "bloom": BloomLevel.ANALYZE,
            "description": "Works effectively with others and contributes to group success"
        },
        {
            "name": "Real-World Connection",
            "bloom": BloomLevel.APPLY,
            "description": "Connects learning to real-world applications"
        },
        {
            "name": "Reflection and Metacognition",
            "bloom": BloomLevel.EVALUATE,
            "description": "Reflects on learning and demonstrates self-awareness"
        }
    ]
    
    def __init__(self):
        self.generated_criteria: list[RubricCriterion] = []
        self.criterion_concept_map: dict[str, list[str]] = {}
        self.criterion_outcome_map: dict[str, list[str]] = {}
    
    def generate(
        self,
        request: RubricGenerationRequest,
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence],
        competencies: list[CompetencyIntelligence]
    ) -> list[RubricCriterion]:
        """
        Generate assessment criteria based on CIOs.
        
        Args:
            request: The rubric generation request
            concepts: Identified concepts
            learning_outcomes: Selected learning outcomes
            competencies: Mapped competencies
            
        Returns:
            List of generated rubric criteria
        """
        logger.info("Generating assessment criteria")
        
        self.generated_criteria = []
        self.criterion_concept_map = {}
        self.criterion_outcome_map = {}
        
        # Determine criteria count based on total marks
        num_criteria = self._determine_criteria_count(request.assignment.total_marks)
        
        # Select criteria templates based on assessment type
        selected_templates = self._select_criteria_templates(
            request.assignment.assessment_type,
            num_criteria
        )
        
        # Generate criteria from templates
        for i, template in enumerate(selected_templates):
            criterion = self._create_criterion(
                template,
                i,
                concepts,
                learning_outcomes,
                competencies,
                request.assignment.total_marks
            )
            self.generated_criteria.append(criterion)
            self.criterion_concept_map[criterion.criterion_id] = criterion.concept_ids
            self.criterion_outcome_map[criterion.criterion_id] = criterion.learning_outcome_ids
        
        # Generate additional criteria from concepts if needed
        self._add_concept_based_criteria(
            concepts, learning_outcomes, request.assignment.total_marks
        )
        
        logger.info(f"Generated {len(self.generated_criteria)} criteria")
        return self.generated_criteria
    
    def _determine_criteria_count(self, total_marks: int) -> int:
        """Determine number of criteria based on total marks"""
        if total_marks <= 20:
            return 4
        elif total_marks <= 50:
            return 5
        elif total_marks <= 100:
            return 6
        else:
            return 7
    
    def _select_criteria_templates(
        self,
        assessment_type: str,
        count: int
    ) -> list[dict]:
        """Select criteria templates based on assessment type"""
        # Base templates that apply to most assessments
        base = [
            self.STANDARD_CRITERIA[0],  # Concept Understanding
            self.STANDARD_CRITERIA[1],  # Application
            self.STANDARD_CRITERIA[4],  # Communication
        ]
        
        # Assessment-specific additions
        if assessment_type == "Project":
            additions = [
                self.STANDARD_CRITERIA[3],  # Creativity
                self.STANDARD_CRITERIA[5],  # Collaboration
                self.STANDARD_CRITERIA[6],  # Real-World
            ]
        elif assessment_type == "Lab Work":
            additions = [
                self.STANDARD_CRITERIA[2],  # Analysis
                self.STANDARD_CRITERIA[6],  # Real-World
                self.STANDARD_CRITERIA[7],  # Reflection
            ]
        elif assessment_type == "Presentation":
            additions = [
                self.STANDARD_CRITERIA[3],  # Creativity
                self.STANDARD_CRITERIA[4],  # Communication
                self.STANDARD_CRITERIA[6],  # Real-World
            ]
        else:
            additions = [
                self.STANDARD_CRITERIA[2],  # Analysis
                self.STANDARD_CRITERIA[3],  # Creativity
            ]
        
        selected = base + additions
        return selected[:count]
    
    def _create_criterion(
        self,
        template: dict,
        index: int,
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence],
        competencies: list[CompetencyIntelligence],
        total_marks: int
    ) -> RubricCriterion:
        """Create a single rubric criterion"""
        criterion_id = f"CRIT_{index+1:02d}"
        
        # Determine marks allocation (higher for core criteria)
        marks = self._allocate_marks(template["name"], total_marks)
        marks_percentage = (marks / total_marks) * 100
        
        # Get linked concepts
        linked_concepts = self._get_linked_concepts(template, concepts)
        
        # Get linked learning outcomes
        linked_outcomes = self._get_linked_outcomes(template, learning_outcomes)
        
        # Get linked competencies
        linked_competencies = self._get_linked_competencies(template, competencies)
        
        # Generate observable behaviours
        behaviours = self._generate_behaviours(template, linked_outcomes)
        
        # Generate success indicators
        indicators = self._generate_indicators(template, linked_outcomes)
        
        # Generate evidence definitions
        evidence = self._generate_evidence(template)
        
        return RubricCriterion(
            criterion_id=criterion_id,
            criterion_name=template["name"],
            description=template["description"],
            concept_ids=[c.concept_id for c in linked_concepts],
            concept_names=[c.concept_name for c in linked_concepts],
            learning_outcome_ids=[o.outcome_id for o in linked_outcomes],
            learning_outcome_statements=[o.outcome_statement for o in linked_outcomes],
            blooms_level=template["bloom"],
            competency_ids=[c.competency_id for c in linked_competencies],
            observable_behaviours=behaviours,
            success_indicators=indicators,
            performance_descriptors=[],  # Generated by PerformanceScaleGenerator
            evidence_definitions=evidence,
            total_marks=marks,
            marks_percentage=marks_percentage
        )
    
    def _allocate_marks(self, criterion_name: str, total_marks: int) -> int:
        """Allocate marks based on criterion importance"""
        weights = {
            "Concept Understanding": 0.25,
            "Application of Knowledge": 0.25,
            "Analysis and Evaluation": 0.20,
            "Creativity and Innovation": 0.15,
            "Communication and Presentation": 0.15,
            "Collaboration and Teamwork": 0.10,
            "Real-World Connection": 0.10,
            "Reflection and Metacognition": 0.10
        }
        weight = weights.get(criterion_name, 0.15)
        marks = int(total_marks * weight)
        return max(marks, 2)  # Minimum 2 marks per criterion
    
    def _get_linked_concepts(
        self,
        template: dict,
        concepts: list[ConceptIntelligence]
    ) -> list[ConceptIntelligence]:
        """Get concepts linked to a criterion"""
        # Match based on Bloom level and difficulty
        bloom = template["bloom"]
        linked = []
        
        for concept in concepts:
            # Link core concepts to understanding
            if bloom == BloomLevel.UNDERSTAND and concept.importance == "Core":
                linked.append(concept)
            # Link all concepts to application
            elif bloom == BloomLevel.APPLY:
                linked.append(concept)
            # Link to analysis where applicable
            elif bloom == BloomLevel.ANALYZE and concept.abilities:
                linked.append(concept)
        
        return linked[:3]  # Limit to 3 concepts per criterion
    
    def _get_linked_outcomes(
        self,
        template: dict,
        outcomes: list[LearningOutcomeIntelligence]
    ) -> list[LearningOutcomeIntelligence]:
        """Get learning outcomes linked to a criterion"""
        bloom = template["bloom"]
        linked = []
        
        for outcome in outcomes:
            if outcome.blooms_level == bloom:
                linked.append(outcome)
            elif bloom in [BloomLevel.UNDERSTAND, BloomLevel.APPLY]:
                linked.append(outcome)
        
        return linked[:2]  # Limit to 2 outcomes per criterion
    
    def _get_linked_competencies(
        self,
        template: dict,
        competencies: list[CompetencyIntelligence]
    ) -> list[CompetencyIntelligence]:
        """Get competencies linked to a criterion"""
        # Match competency names to criterion names
        criterion_lower = template["name"].lower()
        linked = []
        
        for comp in competencies:
            comp_lower = comp.competency_name.lower()
            if any(word in comp_lower for word in criterion_lower.split()):
                linked.append(comp)
        
        return linked[:2]  # Limit to 2 competencies per criterion
    
    def _generate_behaviours(
        self,
        template: dict,
        outcomes: list[LearningOutcomeIntelligence]
    ) -> list[ObservableBehaviourDefinition]:
        """Generate observable behaviours for a criterion"""
        behaviours = []
        criterion_name = template["name"]
        bloom = template["bloom"]
        
        # Generate based on criterion type
        if "understanding" in criterion_name.lower():
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Accurately explains concepts",
                assessment_method="Verbal explanation, Written test",
                evidence_required="Explanation matches established definitions"
            ))
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Identifies key components",
                assessment_method="Diagram labeling, List creation",
                evidence_required="Correct identification of components"
            ))
        elif "application" in criterion_name.lower():
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Applies concepts correctly",
                assessment_method="Problem solving, Practical demonstration",
                evidence_required="Correct application with explanation"
            ))
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Selects appropriate methods",
                assessment_method="Solution presentation",
                evidence_required="Method matches problem requirements"
            ))
        elif "creativity" in criterion_name.lower():
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Generates original ideas",
                assessment_method="Portfolio review, Presentation",
                evidence_required="Original work with justification"
            ))
        elif "communication" in criterion_name.lower():
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Uses appropriate terminology",
                assessment_method="Written work, Oral presentation",
                evidence_required="Correct use of subject vocabulary"
            ))
            behaviours.append(ObservableBehaviourDefinition(
                behaviour="Organizes information clearly",
                assessment_method="Report review, Presentation",
                evidence_required="Logical structure and flow"
            ))
        
        # Add from learning outcomes if available
        for outcome in outcomes[:1]:
            for ob in outcome.observable_behaviours[:1]:
                behaviours.append(ObservableBehaviourDefinition(
                    behaviour=ob.behaviour,
                    assessment_method=", ".join(ob.assessment_method) if ob.assessment_method else "Observation",
                    evidence_required=f"Evidence of {ob.behaviour.lower()}"
                ))
        
        return behaviours
    
    def _generate_indicators(
        self,
        template: dict,
        outcomes: list[LearningOutcomeIntelligence]
    ) -> list[SuccessIndicator]:
        """Generate success indicators for a criterion"""
        indicators = []
        
        # Generate based on Bloom level
        bloom = template["bloom"]
        verb_map = {
            BloomLevel.REMEMBER: "Recalls",
            BloomLevel.UNDERSTAND: "Explains",
            BloomLevel.APPLY: "Applies",
            BloomLevel.ANALYZE: "Analyzes",
            BloomLevel.EVALUATE: "Evaluates",
            BloomLevel.CREATE: "Creates"
        }
        
        indicators.append(SuccessIndicator(
            indicator=f"{verb_map.get(bloom, 'Demonstrates')} core concepts accurately",
            description=template["description"],
            blooms_level=bloom
        ))
        
        # Add from learning outcomes
        for outcome in outcomes[:1]:
            for obj in outcome.objectives[:1]:
                indicators.append(SuccessIndicator(
                    indicator=obj.objective,
                    description=f"Student can {obj.objective.lower()}",
                    blooms_level=obj.blooms_level
                ))
        
        return indicators
    
    def _generate_evidence(self, template: dict) -> list[CriterionEvidence]:
        """Generate evidence definitions for a criterion"""
        criterion_name = template["name"]
        
        evidence_types = {
            "Concept Understanding": [
                CriterionEvidence(
                    evidence_type="Written explanation",
                    description="Written or verbal explanation of concepts",
                    collection_method="Quiz, Oral test, Written test"
                )
            ],
            "Application of Knowledge": [
                CriterionEvidence(
                    evidence_type="Problem solution",
                    description="Completed problems showing application",
                    collection_method="Worksheet, Project submission"
                )
            ],
            "Creativity and Innovation": [
                CriterionEvidence(
                    evidence_type="Original work product",
                    description="Novel solutions or creative products",
                    collection_method="Portfolio, Project submission"
                )
            ],
            "Communication": [
                CriterionEvidence(
                    evidence_type="Presentation",
                    description="Oral or written presentation",
                    collection_method="Presentation, Report submission"
                )
            ]
        }
        
        return evidence_types.get(criterion_name, [
            CriterionEvidence(
                evidence_type="Work sample",
                description="Sample of completed work",
                collection_method="Submission review"
            )
        ])
    
    def _add_concept_based_criteria(
        self,
        concepts: list[ConceptIntelligence],
        outcomes: list[LearningOutcomeIntelligence],
        total_marks: int
    ) -> None:
        """Add additional criteria based on specific concepts"""
        # Add criteria for major concepts if we have room
        for concept in concepts[:2]:
            if len(self.generated_criteria) >= 7:
                break
            
            criterion = RubricCriterion(
                criterion_id=f"CRIT_{len(self.generated_criteria)+1:02d}",
                criterion_name=f"{concept.concept_name} Mastery",
                description=f"Demonstrates thorough understanding of {concept.concept_name}",
                concept_ids=[concept.concept_id],
                concept_names=[concept.concept_name],
                learning_outcome_ids=[],
                learning_outcome_statements=[],
                blooms_level=BloomLevel.UNDERSTAND,
                competency_ids=[],
                observable_behaviours=[],
                success_indicators=[],
                performance_descriptors=[],
                evidence_definitions=[
                    CriterionEvidence(
                        evidence_type="Concept demonstration",
                        description=f"Shows understanding of {concept.concept_name}",
                        collection_method="Direct observation, Product review"
                    )
                ],
                total_marks=5,
                marks_percentage=(5 / total_marks) * 100
            )
            self.generated_criteria.append(criterion)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate generated criteria"""
        errors = []
        
        if not self.generated_criteria:
            errors.append("No criteria generated")
            return False, errors
        
        # Check total marks
        total = sum(c.total_marks for c in self.generated_criteria)
        if total != 100:  # Expect 100% allocation
            # Normalize if needed
            pass
        
        # Check for CIO traceability
        untraceable = [
            c for c in self.generated_criteria
            if not c.concept_ids and not c.learning_outcome_ids
        ]
        if untraceable:
            errors.append(f"{len(untraceable)} criteria lack CIO traceability")
        
        return len(errors) == 0, errors
