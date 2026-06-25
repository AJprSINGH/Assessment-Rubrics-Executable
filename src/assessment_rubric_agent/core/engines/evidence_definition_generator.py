"""
Evidence Definition Generator Engine
Generates evidence definitions and success criteria for rubric.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..schemas.intelligence_objects import BloomLevel
from ..schemas.contracts import (
    RubricGenerationRequest, RubricCriterion, CriterionEvidence, SuccessIndicator
)

logger = logging.getLogger(__name__)


class EvidenceDefinitionGenerator:
    """
    Generates evidence definitions and success criteria for rubric criteria.
    """
    
    def __init__(self):
        self.evidence_definitions: dict[str, list[CriterionEvidence]] = {}
        self.success_criteria: list[dict] = []
    
    def generate(
        self,
        request: RubricGenerationRequest,
        criteria: list[RubricCriterion]
    ) -> tuple[dict[str, list[CriterionEvidence]], list[dict]]:
        """
        Generate evidence definitions for criteria.
        
        Args:
            request: The rubric generation request
            criteria: Generated rubric criteria
            
        Returns:
            Tuple of (evidence_definitions, success_criteria)
        """
        logger.info("Generating evidence definitions")
        
        self.evidence_definitions = {}
        self.success_criteria = []
        
        for criterion in criteria:
            # Generate or enhance evidence for each criterion
            evidence = self._generate_evidence_for_criterion(criterion)
            self.evidence_definitions[criterion.criterion_id] = evidence
            
            # Generate success criteria
            success = self._generate_success_criteria(criterion)
            self.success_criteria.extend(success)
        
        logger.info(f"Generated evidence for {len(self.evidence_definitions)} criteria")
        return self.evidence_definitions, self.success_criteria
    
    def _generate_evidence_for_criterion(
        self,
        criterion: RubricCriterion
    ) -> list[CriterionEvidence]:
        """Generate evidence definitions for a criterion"""
        criterion_lower = criterion.criterion_name.lower()
        evidence = list(criterion.evidence_definitions)  # Keep existing
        
        # Add evidence based on criterion type
        if "understanding" in criterion_lower:
            evidence.extend([
                CriterionEvidence(
                    evidence_type="Verbal Explanation",
                    description="Oral or written explanation of concepts",
                    collection_method="Interview, Quiz, Written test"
                ),
                CriterionEvidence(
                    evidence_type="Diagram/Visual",
                    description="Accurate diagrams or visual representations",
                    collection_method="Assignment submission"
                )
            ])
        
        elif "application" in criterion_lower:
            evidence.extend([
                CriterionEvidence(
                    evidence_type="Problem Solution",
                    description="Completed problems showing application",
                    collection_method="Worksheet, Project submission"
                ),
                CriterionEvidence(
                    evidence_type="Practical Demonstration",
                    description="Hands-on demonstration of skills",
                    collection_method="Lab work, Performance task"
                )
            ])
        
        elif "creativity" in criterion_lower:
            evidence.extend([
                CriterionEvidence(
                    evidence_type="Original Product",
                    description="Created artifact or solution",
                    collection_method="Portfolio review"
                ),
                CriterionEvidence(
                    evidence_type="Design Process",
                    description="Evidence of creative process",
                    collection_method="Sketches, drafts, reflections"
                )
            ])
        
        elif "communication" in criterion_lower:
            evidence.extend([
                CriterionEvidence(
                    evidence_type="Written Work",
                    description="Clear, organized written communication",
                    collection_method="Report, Essay submission"
                ),
                CriterionEvidence(
                    evidence_type="Oral Presentation",
                    description="Effective verbal presentation",
                    collection_method="Presentation observation"
                ),
                CriterionEvidence(
                    evidence_type="Visual Aid",
                    description="Appropriate use of visual materials",
                    collection_method="Presentation materials"
                )
            ])
        
        elif "collaboration" in criterion_lower:
            evidence.extend([
                CriterionEvidence(
                    evidence_type="Group Contribution",
                    description="Documented contribution to group work",
                    collection_method="Peer evaluation, Log entries"
                ),
                CriterionEvidence(
                    evidence_type="Team Interaction",
                    description="Evidence of effective teamwork",
                    collection_method="Observation, Group reflection"
                )
            ])
        
        elif "real-world" in criterion_lower:
            evidence.extend([
                CriterionEvidence(
                    evidence_type="Real-World Application",
                    description="Connection to real-world context",
                    collection_method="Project report, Presentation"
                ),
                CriterionEvidence(
                    evidence_type="Practical Relevance",
                    description="Evidence of understanding practical use",
                    collection_method="Application examples"
                )
            ])
        
        # Ensure at least one evidence type exists
        if not evidence:
            evidence.append(CriterionEvidence(
                evidence_type="Work Sample",
                description=f"Sample of {criterion.criterion_name} work",
                collection_method="Submission review"
            ))
        
        return evidence
    
    def _generate_success_criteria(self, criterion: RubricCriterion) -> list[dict]:
        """Generate success criteria for a criterion"""
        criteria = []
        
        for indicator in criterion.success_indicators:
            criteria.append({
                "criterion_id": criterion.criterion_id,
                "criterion_name": criterion.criterion_name,
                "indicator": indicator.indicator,
                "description": indicator.description,
                "blooms_level": indicator.blooms_level.value if indicator.blooms_level else "Understand",
                "marks_allocation": f"{int(criterion.marks_percentage)}%"
            })
        
        return criteria
    
    def get_evidence_summary(self) -> dict:
        """Get summary of all evidence definitions"""
        summary = {}
        for crit_id, evidence_list in self.evidence_definitions.items():
            summary[crit_id] = {
                "count": len(evidence_list),
                "types": [e.evidence_type for e in evidence_list],
                "methods": list(set(e.collection_method for e in evidence_list))
            }
        return summary
