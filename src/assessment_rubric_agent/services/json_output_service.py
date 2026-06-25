"""
JSON Output Service
Generates JSON outputs for rubric data.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.schemas.contracts import RubricMatrix

logger = logging.getLogger(__name__)


class JSONOutputService:
    """
    Generates JSON outputs for rubric data.
    """
    
    def __init__(self, output_dir: str = "outputs/jsons"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_rubric_json(
        self,
        rubric_matrix: RubricMatrix,
        request_id: str
    ) -> str:
        """
        Generate Rubric Matrix JSON.
        
        Args:
            rubric_matrix: The rubric matrix to export
            request_id: Request identifier for filename
            
        Returns:
            Path to generated JSON file
        """
        logger.info(f"Generating rubric JSON for: {request_id}")
        
        try:
            # Convert to dict with serialization
            data = self._rubric_to_dict(rubric_matrix)
            
            # Write to file
            filename = f"rubric_matrix_{request_id}.json"
            output_path = self.output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Rubric JSON generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"JSON generation failed: {e}")
            raise
    
    def _rubric_to_dict(self, rubric: RubricMatrix) -> dict:
        """Convert RubricMatrix to dictionary"""
        return {
            "rubric_id": rubric.rubric_id,
            "version": rubric.version,
            "generated_at": str(rubric.generated_at),
            "cio_centric": rubric.cio_centric,
            
            # Assessment Information
            "assessment_information": {
                "board": rubric.assessment_information.board,
                "grade": rubric.assessment_information.grade,
                "subject": rubric.assessment_information.subject,
                "unit": rubric.assessment_information.unit,
                "chapter": rubric.assessment_information.chapter,
                "assignment_name": rubric.assessment_information.assignment_name,
                "project_type": rubric.assessment_information.project_type,
                "assessment_type": rubric.assessment_information.assessment_type,
                "rubric_type": rubric.assessment_information.rubric_type,
                "total_marks": rubric.assessment_information.total_marks,
                "performance_scale": rubric.assessment_information.performance_scale
            },
            
            # Context
            "context": {
                "class_size": rubric.context.class_size,
                "student_profile": rubric.context.student_profile,
                "time_duration": rubric.context.time_duration,
                "available_resources": rubric.context.available_resources,
                "differentiation_required": rubric.context.differentiation_required,
                "inclusion_considerations": rubric.context.inclusion_considerations
            },
            
            # Criteria
            "criteria": [
                self._criterion_to_dict(c) for c in rubric.criteria
            ],
            
            # Performance Levels
            "performance_levels": [
                {
                    "level": pl.level,
                    "description": pl.description,
                    "marks_range": {
                        "min": pl.marks_range[0],
                        "max": pl.marks_range[1]
                    },
                    "colour_code": pl.colour_code,
                    "generic_characteristics": pl.generic_characteristics
                }
                for pl in rubric.performance_levels
            ],
            
            # Learning Outcome Alignment
            "learning_outcome_alignment": {
                "alignments": [
                    {
                        "learning_outcome_id": a.learning_outcome_id,
                        "learning_outcome_statement": a.learning_outcome_statement,
                        "concepts": a.concepts,
                        "competencies": a.competencies,
                        "assessment_criterion": a.assessment_criterion,
                        "criterion_id": a.criterion_id,
                        "performance_indicators": a.performance_indicators,
                        "evidence": a.evidence
                    }
                    for a in rubric.learning_outcome_alignment.alignments
                ],
                "coverage_percentage": rubric.learning_outcome_alignment.coverage_percentage,
                "total_outcomes": rubric.learning_outcome_alignment.total_outcomes,
                "aligned_outcomes": rubric.learning_outcome_alignment.aligned_outcomes
            },
            
            # Marks Distribution
            "marks_distribution": rubric.marks_distribution,
            "total_marks": rubric.total_marks
        }
    
    def _criterion_to_dict(self, criterion) -> dict:
        """Convert RubricCriterion to dictionary"""
        return {
            "criterion_id": criterion.criterion_id,
            "criterion_name": criterion.criterion_name,
            "description": criterion.description,
            
            # CIO Traceability
            "concept_ids": criterion.concept_ids,
            "concept_names": criterion.concept_names,
            "learning_outcome_ids": criterion.learning_outcome_ids,
            "learning_outcome_statements": criterion.learning_outcome_statements,
            "blooms_level": criterion.blooms_level,
            "competency_ids": criterion.competency_ids,
            
            # Observable Behaviours
            "observable_behaviours": [
                {
                    "behaviour": ob.behaviour,
                    "assessment_method": ob.assessment_method,
                    "evidence_required": ob.evidence_required
                }
                for ob in criterion.observable_behaviours
            ],
            
            # Success Indicators
            "success_indicators": [
                {
                    "indicator": si.indicator,
                    "description": si.description,
                    "blooms_level": si.blooms_level,
                    "observable": si.observable
                }
                for si in criterion.success_indicators
            ],
            
            # Performance Descriptors
            "performance_descriptors": [
                {
                    "level": pd.level,
                    "description": pd.description,
                    "marks_range": {
                        "min": pd.marks_range[0],
                        "max": pd.marks_range[1]
                    },
                    "key_characteristics": pd.key_characteristics
                }
                for pd in criterion.performance_descriptors
            ],
            
            # Evidence Definitions
            "evidence_definitions": [
                {
                    "evidence_type": ed.evidence_type,
                    "description": ed.description,
                    "collection_method": ed.collection_method
                }
                for ed in criterion.evidence_definitions
            ],
            
            # Marks
            "total_marks": criterion.total_marks,
            "marks_percentage": criterion.marks_percentage,
            
            # Teacher-specific
            "teacher_notes": criterion.teacher_notes,
            "common_misconceptions": criterion.common_misconceptions
        }
    
    def generate_learning_outcome_matrix(
        self,
        rubric_matrix: RubricMatrix,
        request_id: str
    ) -> str:
        """
        Generate Learning Outcome Alignment Matrix JSON.
        
        Args:
            rubric_matrix: The rubric matrix
            request_id: Request identifier for filename
            
        Returns:
            Path to generated JSON file
        """
        logger.info(f"Generating LO matrix JSON for: {request_id}")
        
        data = {
            "generated_at": str(datetime.now()),
            "rubric_id": rubric_matrix.rubric_id,
            "alignment_matrix": [
                {
                    "learning_outcome": {
                        "id": a.learning_outcome_id,
                        "statement": a.learning_outcome_statement
                    },
                    "concepts": a.concepts,
                    "competencies": a.competencies,
                    "assessment_criterion": {
                        "id": a.criterion_id,
                        "name": a.assessment_criterion
                    },
                    "performance_indicators": a.performance_indicators,
                    "evidence": a.evidence
                }
                for a in rubric_matrix.learning_outcome_alignment.alignments
            ],
            "coverage_summary": {
                "total_outcomes": rubric_matrix.learning_outcome_alignment.total_outcomes,
                "aligned_outcomes": rubric_matrix.learning_outcome_alignment.aligned_outcomes,
                "coverage_percentage": rubric_matrix.learning_outcome_alignment.coverage_percentage
            }
        }
        
        filename = f"lo_matrix_{request_id}.json"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
