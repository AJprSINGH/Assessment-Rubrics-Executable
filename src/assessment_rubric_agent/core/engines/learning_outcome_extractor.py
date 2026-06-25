"""
Learning Outcome Extractor Engine
Extracts and identifies relevant learning outcomes for rubric generation.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..schemas.intelligence_objects import (
    LearningOutcomeIntelligence, ConceptIntelligence, BloomLevel
)
from ..schemas.contracts import (
    RubricGenerationRequest, RubricCriterion, ObservableBehaviourDefinition,
    SuccessIndicator
)

logger = logging.getLogger(__name__)


class LearningOutcomeExtractor:
    """
    Extracts and identifies relevant learning outcomes based on:
    - Assignment requirements
    - Concept coverage
    - Bloom's taxonomy levels
    """
    
    def __init__(self):
        self.extracted_outcomes: list[LearningOutcomeIntelligence] = []
        self.coverage_map: dict[str, list[str]] = {}  # outcome_id -> concept_ids
    
    def extract(
        self,
        request: RubricGenerationRequest,
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence]
    ) -> list[LearningOutcomeIntelligence]:
        """
        Extract relevant learning outcomes for the assignment.
        
        Args:
            request: The rubric generation request
            concepts: List of concept intelligences
            learning_outcomes: Available learning outcomes
            
        Returns:
            List of selected learning outcomes
        """
        logger.info(f"Extracting learning outcomes from {len(learning_outcomes)} available")
        
        self.extracted_outcomes = []
        self.coverage_map = {}
        
        # Filter by concepts covered
        concept_names = {c.concept_name.lower() for c in concepts}
        
        for outcome in learning_outcomes:
            # Check if outcome relates to covered concepts
            outcome_concepts = {c.lower() for c in outcome.concepts_covered}
            
            # Match outcomes to concepts
            if concept_names & outcome_concepts:  # Intersection
                self.extracted_outcomes.append(outcome)
                self.coverage_map[outcome.outcome_id] = list(concept_names & outcome_concepts)
            elif self._matches_assignment_type(outcome, request.assignment.assessment_type):
                # Include based on assessment type alignment
                self.extracted_outcomes.append(outcome)
                self.coverage_map[outcome.outcome_id] = []
        
        # If no outcomes matched, generate default outcomes based on concepts
        if not self.extracted_outcomes:
            logger.warning("No matching outcomes found, generating default outcomes")
            self.extracted_outcomes = self._generate_default_outcomes(concepts)
        
        logger.info(f"Extracted {len(self.extracted_outcomes)} learning outcomes")
        return self.extracted_outcomes
    
    def _matches_assignment_type(
        self,
        outcome: LearningOutcomeIntelligence,
        assessment_type: str
    ) -> bool:
        """Check if outcome matches the assignment type"""
        # Higher-order thinking outcomes match projects
        higher_order = [BloomLevel.ANALYZE, BloomLevel.EVALUATE, BloomLevel.CREATE]
        return outcome.blooms_level in higher_order
    
    def _generate_default_outcomes(
        self,
        concepts: list[ConceptIntelligence]
    ) -> list[LearningOutcomeIntelligence]:
        """Generate default learning outcomes based on concepts"""
        outcomes = []
        
        for i, concept in enumerate(concepts[:5]):  # Limit to 5 outcomes
            outcomes.append(LearningOutcomeIntelligence(
                outcome_id=f"LO_DEFAULT_{i+1}",
                outcome_statement=f"Students will demonstrate understanding of {concept.concept_name}",
                concepts_covered=[concept.concept_name],
                blooms_level=BloomLevel.UNDERSTAND,
                dok_level="2"
            ))
        
        return outcomes
    
    def get_outcome_coverage(self) -> dict[str, list[str]]:
        """Get coverage mapping of outcomes to concepts"""
        return self.coverage_map
    
    def get_outcome_by_id(self, outcome_id: str) -> Optional[LearningOutcomeIntelligence]:
        """Get a specific outcome by ID"""
        for outcome in self.extracted_outcomes:
            if outcome.outcome_id == outcome_id:
                return outcome
        return None
    
    def get_observable_behaviours_for_criterion(
        self,
        outcome: LearningOutcomeIntelligence
    ) -> list[ObservableBehaviourDefinition]:
        """Extract observable behaviours from learning outcome"""
        behaviours = []
        
        if outcome.observable_behaviours:
            for ob in outcome.observable_behaviours:
                behaviours.append(ObservableBehaviourDefinition(
                    behaviour=ob.behaviour,
                    assessment_method=", ".join(ob.assessment_method) if ob.assessment_method else "Direct observation",
                    evidence_required=f"Evidence of {ob.behaviour.lower()}"
                ))
        else:
            # Generate default observable behaviours
            behaviours.append(ObservableBehaviourDefinition(
                behaviour=f"Demonstrate {outcome.blooms_level.value.lower()} of content",
                assessment_method="Product analysis, Observation",
                evidence_required="Completed work sample"
            ))
        
        return behaviours
    
    def get_success_indicators(
        self,
        outcome: LearningOutcomeIntelligence
    ) -> list[SuccessIndicator]:
        """Extract success indicators from learning outcome"""
        indicators = []
        
        for obj in outcome.objectives:
            indicators.append(SuccessIndicator(
                indicator=obj.objective,
                description=f"Student can {obj.objective.lower()}",
                blooms_level=obj.blooms_level
            ))
        
        # Add default indicators if none exist
        if not indicators:
            indicators.append(SuccessIndicator(
                indicator="Content Knowledge",
                description=f"Accurately demonstrates understanding of {outcome.outcome_statement}",
                blooms_level=outcome.blooms_level
            ))
        
        return indicators
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate extracted outcomes"""
        errors = []
        
        if not self.extracted_outcomes:
            errors.append("No learning outcomes extracted")
        
        # Check for minimum outcome count
        if len(self.extracted_outcomes) < 2:
            errors.append("Insufficient learning outcomes (minimum 2 recommended)")
        
        # Check for Bloom's level diversity
        bloom_levels = {o.blooms_level for o in self.extracted_outcomes}
        if len(bloom_levels) < 2:
            errors.append("Limited Bloom's taxonomy level diversity")
        
        return len(errors) == 0, errors
