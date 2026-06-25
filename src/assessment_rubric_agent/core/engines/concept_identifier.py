"""
Concept Identifier Engine
Identifies and maps concepts to rubric criteria.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..schemas.intelligence_objects import (
    ConceptIntelligence, LearningOutcomeIntelligence, BloomLevel, DifficultyLevel
)
from ..schemas.contracts import RubricGenerationRequest

logger = logging.getLogger(__name__)


class ConceptIdentifier:
    """
    Identifies concepts relevant to the assessment and maps them
    to rubric criteria.
    """
    
    def __init__(self):
        self.identified_concepts: list[ConceptIntelligence] = []
        self.concept_criterion_map: dict[str, str] = {}  # concept_id -> criterion_name
    
    def identify(
        self,
        request: RubricGenerationRequest,
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence]
    ) -> list[ConceptIntelligence]:
        """
        Identify concepts relevant to the assignment.
        
        Args:
            request: The rubric generation request
            concepts: Available concept intelligences
            learning_outcomes: Selected learning outcomes
            
        Returns:
            List of identified concepts
        """
        logger.info(f"Identifying concepts from {len(concepts)} available")
        
        self.identified_concepts = []
        self.concept_criterion_map = {}
        
        # Match concepts to learning outcomes
        outcome_concepts = set()
        for outcome in learning_outcomes:
            outcome_concepts.update(outcome.concepts_covered)
        
        # Filter and rank concepts
        scored_concepts = []
        for concept in concepts:
            score = self._calculate_relevance_score(concept, request, outcome_concepts)
            scored_concepts.append((score, concept))
        
        # Sort by score descending
        scored_concepts.sort(key=lambda x: x[0], reverse=True)
        
        # Select top concepts (based on assignment type)
        max_concepts = self._get_max_concepts(request.assignment.assessment_type)
        selected = scored_concepts[:max_concepts]
        
        for score, concept in selected:
            self.identified_concepts.append(concept)
            logger.debug(f"Selected concept: {concept.concept_name} (score: {score:.2f})")
        
        logger.info(f"Identified {len(self.identified_concepts)} concepts")
        return self.identified_concepts
    
    def _calculate_relevance_score(
        self,
        concept: ConceptIntelligence,
        request: RubricGenerationRequest,
        outcome_concepts: set[str]
    ) -> float:
        """Calculate relevance score for a concept"""
        score = 0.0
        
        # Concept difficulty alignment
        difficulty_weights = {
            DifficultyLevel.EASY: 1.0,
            DifficultyLevel.MEDIUM: 1.2,
            DifficultyLevel.HARD: 0.8
        }
        score += difficulty_weights.get(concept.difficulty, 1.0) * 0.2
        
        # Importance weight
        importance_weights = {"Core": 1.0, "Supporting": 0.7, "Extended": 0.5}
        score += importance_weights.get(concept.importance, 0.7) * 0.3
        
        # Match with learning outcomes
        if concept.concept_name in outcome_concepts:
            score += 0.3
        
        # Confidence weight
        score += concept.confidence * 0.2
        
        return score
    
    def _get_max_concepts(self, assessment_type: str) -> int:
        """Get maximum concepts based on assessment type"""
        limits = {
            "Project": 7,
            "Assignment": 5,
            "Lab Work": 6,
            "Presentation": 5,
            "Portfolio": 8,
            "Performance Task": 6
        }
        return limits.get(assessment_type, 5)
    
    def map_concept_to_criterion(self, concept: ConceptIntelligence) -> str:
        """
        Map a concept to a criterion name.
        
        Returns criterion name based on concept type and importance.
        """
        criterion_mapping = {
            "Core": f"Understanding of {concept.concept_name}",
            "Supporting": f"Application of {concept.concept_name}",
            "Extended": f"Extended Analysis of {concept.concept_name}"
        }
        return criterion_mapping.get(concept.importance, f"{concept.concept_name} Mastery")
    
    def get_concept_prerequisites(self, concept: ConceptIntelligence) -> list[str]:
        """Get prerequisite concepts for a given concept"""
        return concept.prerequisites
    
    def get_concept_misconceptions(self, concept: ConceptIntelligence) -> list[str]:
        """Get common misconceptions for a given concept"""
        return concept.misconceptions
    
    def get_concept_applications(self, concept: ConceptIntelligence) -> list[str]:
        """Get real-world applications for a given concept"""
        return concept.real_world_applications
    
    def get_difficulty_distribution(self) -> dict[DifficultyLevel, int]:
        """Get distribution of concept difficulties"""
        distribution = {
            DifficultyLevel.EASY: 0,
            DifficultyLevel.MEDIUM: 0,
            DifficultyLevel.HARD: 0
        }
        for concept in self.identified_concepts:
            distribution[concept.difficulty] += 1
        return distribution
    
    def get_bloom_distribution(self) -> dict[BloomLevel, int]:
        """Get distribution of Bloom's levels across abilities"""
        distribution = {level: 0 for level in BloomLevel}
        
        for concept in self.identified_concepts:
            for ability in concept.abilities:
                if ability.blooms_level:
                    distribution[ability.blooms_level] += 1
        
        return distribution
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate identified concepts"""
        errors = []
        
        if not self.identified_concepts:
            errors.append("No concepts identified")
        
        # Check for core concepts
        core_concepts = [c for c in self.identified_concepts if c.importance == "Core"]
        if not core_concepts:
            errors.append("No core concepts identified")
        
        # Check difficulty balance
        difficulty_dist = self.get_difficulty_distribution()
        if difficulty_dist[DifficultyLevel.MEDIUM] == 0:
            errors.append("No medium difficulty concepts (may indicate imbalance)")
        
        return len(errors) == 0, errors
    
    def get_summary(self) -> dict:
        """Get summary of identified concepts"""
        return {
            "total_concepts": len(self.identified_concepts),
            "core_concepts": len([c for c in self.identified_concepts if c.importance == "Core"]),
            "difficulty_distribution": self.get_difficulty_distribution(),
            "bloom_distribution": self.get_bloom_distribution()
        }
