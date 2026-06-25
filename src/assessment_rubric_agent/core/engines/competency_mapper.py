"""
Competency Mapper Engine
Maps competencies to rubric criteria and performance indicators.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..schemas.intelligence_objects import (
    CompetencyIntelligence, ConceptIntelligence, LearningOutcomeIntelligence,
    BloomLevel, CompetencyLevel, PerformanceIndicator
)
from ..schemas.contracts import RubricGenerationRequest

logger = logging.getLogger(__name__)


class CompetencyMapper:
    """
    Maps competencies to assessment criteria and generates
    performance indicators.
    """
    
    def __init__(self):
        self.mapped_competencies: list[CompetencyIntelligence] = []
        self.competency_criterion_map: dict[str, list[str]] = {}  # competency_id -> criterion_ids
    
    def map(
        self,
        request: RubricGenerationRequest,
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence],
        competencies: list[CompetencyIntelligence]
    ) -> list[CompetencyIntelligence]:
        """
        Map competencies to the assessment.
        
        Args:
            request: The rubric generation request
            concepts: Identified concepts
            learning_outcomes: Selected learning outcomes
            competencies: Available competencies
            
        Returns:
            List of mapped competencies
        """
        logger.info(f"Mapping competencies from {len(competencies)} available")
        
        self.mapped_competencies = []
        self.competency_criterion_map = {}
        
        # Match competencies to concepts and outcomes
        concept_names = {c.concept_name for c in concepts}
        outcome_ids = {o.outcome_id for o in learning_outcomes}
        
        for competency in competencies:
            # Check if competency relates to concepts or outcomes
            related_concepts = set(competency.related_concepts)
            related_outcomes = set(competency.related_outcomes)
            
            if concept_names & related_concepts or outcome_ids & related_outcomes:
                self.mapped_competencies.append(competency)
                self.competency_criterion_map[competency.competency_id] = []
        
        # If no competencies matched, generate default competencies
        if not self.mapped_competencies:
            logger.warning("No matching competencies found, generating defaults")
            self.mapped_competencies = self._generate_default_competencies(
                concepts, learning_outcomes
            )
        
        logger.info(f"Mapped {len(self.mapped_competencies)} competencies")
        return self.mapped_competencies
    
    def _generate_default_competencies(
        self,
        concepts: list[ConceptIntelligence],
        learning_outcomes: list[LearningOutcomeIntelligence]
    ) -> list[CompetencyIntelligence]:
        """Generate default competencies based on concepts and outcomes"""
        competencies = []
        
        # Generate competencies from concepts
        for i, concept in enumerate(concepts[:3]):
            competencies.append(CompetencyIntelligence(
                competency_id=f"COMP_DEFAULT_{i+1}",
                competency_name=f"{concept.concept_name} Competency",
                description=f"Demonstrate mastery of {concept.concept_name}",
                competency_level=CompetencyLevel.INTERMEDIATE,
                related_concepts=[concept.concept_name],
                related_outcomes=[lo.outcome_id for lo in learning_outcomes[:2]]
            ))
        
        # Add general competencies
        general_competencies = [
            ("Problem Solving", "Apply analytical thinking to solve problems"),
            ("Communication", "Effectively communicate understanding"),
            ("Critical Thinking", "Evaluate and analyze information critically")
        ]
        
        for name, desc in general_competencies:
            competencies.append(CompetencyIntelligence(
                competency_id=f"COMP_GEN_{name.replace(' ', '_')}",
                competency_name=name,
                description=desc,
                competency_level=CompetencyLevel.INTERMEDIATE,
                performance_indicators=[
                    PerformanceIndicator(
                        indicator=f"Demonstrates {name.lower()}",
                        description=desc,
                        competency_level=CompetencyLevel.INTERMEDIATE,
                        blooms_level=BloomLevel.ANALYZE
                    )
                ]
            ))
        
        return competencies
    
    def get_performance_indicators(
        self,
        competency: CompetencyIntelligence
    ) -> list[PerformanceIndicator]:
        """Get performance indicators for a competency"""
        if competency.performance_indicators:
            return competency.performance_indicators
        
        # Generate default indicators
        return [
            PerformanceIndicator(
                indicator=f"Demonstrates {competency.competency_name}",
                description=competency.description,
                competency_level=competency.competency_level,
                blooms_level=BloomLevel.UNDERSTAND
            ),
            PerformanceIndicator(
                indicator=f"Applies {competency.competency_name} effectively",
                description=f"Apply {competency.competency_name} in new situations",
                competency_level=CompetencyLevel.ADVANCED,
                blooms_level=BloomLevel.APPLY
            )
        ]
    
    def get_competency_level_descriptors(
        self,
        level: CompetencyLevel
    ) -> dict[str, str]:
        """Get descriptors for competency levels"""
        descriptors = {
            CompetencyLevel.BEGINNER: {
                "indicator": "Beginning",
                "description": "Shows basic understanding with guidance",
                "marks_percentage": 25
            },
            CompetencyLevel.INTERMEDIATE: {
                "indicator": "Proficient",
                "description": "Demonstrates competency independently",
                "marks_percentage": 50
            },
            CompetencyLevel.ADVANCED: {
                "indicator": "Advanced",
                "description": "Shows mastery and can teach others",
                "marks_percentage": 25
            }
        }
        return descriptors.get(level, descriptors[CompetencyLevel.INTERMEDIATE])
    
    def map_criterion_to_competency(
        self,
        criterion_id: str,
        competency_id: str
    ) -> None:
        """Map a criterion to a competency"""
        if competency_id not in self.competency_criterion_map:
            self.competency_criterion_map[competency_id] = []
        if criterion_id not in self.competency_criterion_map[competency_id]:
            self.competency_criterion_map[competency_id].append(criterion_id)
    
    def get_criterion_competencies(self, criterion_id: str) -> list[str]:
        """Get competency IDs mapped to a criterion"""
        return [
            comp_id for comp_id, crit_ids in self.competency_criterion_map.items()
            if criterion_id in crit_ids
        ]
    
    def get_competency_criteria_count(self) -> dict[str, int]:
        """Get count of criteria per competency"""
        return {
            comp_id: len(crit_ids)
            for comp_id, crit_ids in self.competency_criterion_map.items()
        }
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate mapped competencies"""
        errors = []
        
        if not self.mapped_competencies:
            errors.append("No competencies mapped")
        
        # Check for competency level diversity
        levels = {c.competency_level for c in self.mapped_competencies}
        if len(levels) < 2:
            errors.append("Limited competency level diversity")
        
        return len(errors) == 0, errors
