"""
Performance Scale Generator Engine
Generates performance levels and descriptors for rubric criteria.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..schemas.intelligence_objects import BloomLevel
from ..schemas.contracts import (
    RubricGenerationRequest, RubricCriterion, PerformanceLevel, PerformanceDescriptor
)

logger = logging.getLogger(__name__)


class PerformanceScaleGenerator:
    """
    Generates performance levels and descriptors for rubric criteria.
    """
    
    # Default performance levels
    DEFAULT_SCALES = {
        4: [
            {"level": "Exemplary", "range": (90, 100), "colour": "#2E7D32", "description": "Exceeds expectations"},
            {"level": "Proficient", "range": (75, 89), "colour": "#1976D2", "description": "Meets expectations"},
            {"level": "Developing", "range": (60, 74), "colour": "#FFA000", "description": "Approaching expectations"},
            {"level": "Beginning", "range": (0, 59), "colour": "#D32F2F", "description": "Below expectations"}
        ],
        5: [
            {"level": "Exemplary", "range": (90, 100), "colour": "#2E7D32", "description": "Exceeds expectations"},
            {"level": "Proficient", "range": (75, 89), "colour": "#1976D2", "description": "Meets expectations"},
            {"level": "Competent", "range": (60, 74), "colour": "#7B1FA2", "description": "Developing towards expectations"},
            {"level": "Developing", "range": (40, 59), "colour": "#FFA000", "description": "Approaching expectations"},
            {"level": "Beginning", "range": (0, 39), "colour": "#D32F2F", "description": "Below expectations"}
        ],
        3: [
            {"level": "Proficient", "range": (70, 100), "colour": "#2E7D32", "description": "Meets expectations"},
            {"level": "Partially Proficient", "range": (40, 69), "colour": "#FFA000", "description": "Approaching expectations"},
            {"level": "Novice", "range": (0, 39), "colour": "#D32F2F", "description": "Below expectations"}
        ]
    }
    
    # Bloom's level descriptors for each performance level
    BLOOM_DESCRIPTORS = {
        BloomLevel.REMEMBER: {
            "Exemplary": "Recalls and organizes all relevant facts with precision",
            "Proficient": "Recalls most relevant facts accurately",
            "Developing": "Recalls some facts with occasional errors",
            "Beginning": "Struggles to recall basic facts"
        },
        BloomLevel.UNDERSTAND: {
            "Exemplary": "Explains concepts clearly with multiple representations",
            "Proficient": "Explains concepts accurately",
            "Developing": "Explains concepts with some confusion",
            "Beginning": "Unable to explain concepts"
        },
        BloomLevel.APPLY: {
            "Exemplary": "Applies concepts flexibly to novel situations",
            "Proficient": "Applies concepts to standard situations correctly",
            "Developing": "Applies concepts with guidance",
            "Beginning": "Cannot apply concepts independently"
        },
        BloomLevel.ANALYZE: {
            "Exemplary": "Provides thorough analysis with multiple perspectives",
            "Proficient": "Analyzes situations accurately",
            "Developing": "Identifies some elements but incomplete analysis",
            "Beginning": "Unable to analyze situations"
        },
        BloomLevel.EVALUATE: {
            "Exemplary": "Presents well-reasoned evaluation with evidence",
            "Proficient": "Evaluates appropriately with some justification",
            "Developing": "Evaluates with limited reasoning",
            "Beginning": "Unable to evaluate critically"
        },
        BloomLevel.CREATE: {
            "Exemplary": "Creates original, coherent solutions",
            "Proficient": "Creates functional solutions",
            "Developing": "Creates partial solutions with guidance",
            "Beginning": "Unable to create solutions"
        }
    }
    
    def __init__(self):
        self.performance_levels: list[PerformanceLevel] = []
        self.criterion_descriptors: dict[str, list[PerformanceDescriptor]] = {}
    
    def generate(
        self,
        request: RubricGenerationRequest,
        criteria: list[RubricCriterion]
    ) -> tuple[list[PerformanceLevel], dict[str, list[PerformanceDescriptor]]]:
        """
        Generate performance levels and descriptors.
        
        Args:
            request: The rubric generation request
            criteria: Generated rubric criteria
            
        Returns:
            Tuple of (performance_levels, criterion_descriptors)
        """
        logger.info("Generating performance scale")
        
        scale_size = len(request.assignment.performance_scale)
        scale_config = self.DEFAULT_SCALES.get(
            scale_size, 
            self.DEFAULT_SCALES[4]
        )
        
        # Adjust to match requested scale names
        if scale_size != len(scale_config):
            scale_config = self._adjust_scale(request.assignment.performance_scale)
        
        # Generate global performance levels
        self.performance_levels = [
            PerformanceLevel(
                level=level["level"],
                description=level["description"],
                marks_range=(level["range"][0], level["range"][1]),
                colour_code=level["colour"],
                generic_characteristics=[]
            )
            for level in scale_config
        ]
        
        # Generate descriptors for each criterion
        self.criterion_descriptors = {}
        for criterion in criteria:
            self.criterion_descriptors[criterion.criterion_id] = \
                self._generate_criterion_descriptors(criterion, scale_config)
        
        logger.info(f"Generated {len(self.performance_levels)} performance levels")
        return self.performance_levels, self.criterion_descriptors
    
    def _adjust_scale(self, scale_names: list[str]) -> list[dict]:
        """Adjust default scale to match requested names"""
        colours = ["#2E7D32", "#1976D2", "#FFA000", "#D32F2F", "#7B1FA2"]
        
        if len(scale_names) == 3:
            ranges = [(70, 100), (40, 69), (0, 39)]
        elif len(scale_names) == 5:
            ranges = [(90, 100), (75, 89), (60, 74), (40, 59), (0, 39)]
        else:
            ranges = [(75, 100), (50, 74), (0, 49)]
        
        return [
            {
                "level": name,
                "range": ranges[i] if i < len(ranges) else (0, 50),
                "colour": colours[i] if i < len(colours) else "#757575",
                "description": f"Performance at {name} level"
            }
            for i, name in enumerate(scale_names)
        ]
    
    def _generate_criterion_descriptors(
        self,
        criterion: RubricCriterion,
        scale_config: list[dict]
    ) -> list[PerformanceDescriptor]:
        """Generate performance descriptors for a specific criterion"""
        descriptors = []
        bloom = criterion.blooms_level
        criterion_lower = criterion.criterion_name.lower()
        
        # Get bloom-specific descriptors
        bloom_descs = self.BLOOM_DESCRIPTORS.get(bloom, self.BLOOM_DESCRIPTORS[BloomLevel.UNDERSTAND])
        
        for level_config in scale_config:
            level_name = level_config["level"]
            
            # Get base descriptor from Bloom mapping
            base_desc = bloom_descs.get(level_name, f"Demonstrates {level_name} level of {criterion.criterion_name}")
            
            # Customize based on criterion type
            specific_desc = self._customize_descriptor(
                criterion, level_name, base_desc
            )
            
            # Calculate marks range for this criterion
            marks_min = int(level_config["range"][0] * criterion.total_marks / 100)
            marks_max = int(level_config["range"][1] * criterion.total_marks / 100)
            
            descriptors.append(PerformanceDescriptor(
                level=level_name,
                description=specific_desc,
                marks_range=(marks_min, marks_max),
                key_characteristics=self._get_key_characteristics(criterion, level_name)
            ))
        
        return descriptors
    
    def _customize_descriptor(
        self,
        criterion: RubricCriterion,
        level: str,
        base_desc: str
    ) -> str:
        """Customize descriptor based on criterion specifics"""
        criterion_lower = criterion.criterion_name.lower()
        
        templates = {
            "concept understanding": {
                "Exemplary": "Demonstrates comprehensive understanding with precise definitions and examples",
                "Proficient": "Demonstrates clear understanding of core concepts",
                "Developing": "Shows partial understanding with some misconceptions",
                "Beginning": "Shows significant gaps in understanding"
            },
            "application": {
                "Exemplary": "Applies concepts creatively to solve novel problems",
                "Proficient": "Applies concepts correctly to standard problems",
                "Developing": "Applies concepts with errors or inconsistencies",
                "Beginning": "Unable to apply concepts without extensive support"
            },
            "creativity": {
                "Exemplary": "Produces highly original and innovative work",
                "Proficient": "Demonstrates creative thinking in work",
                "Developing": "Shows some creative elements",
                "Beginning": "Work lacks creative elements"
            },
            "communication": {
                "Exemplary": "Communicates with exceptional clarity and professionalism",
                "Proficient": "Communicates clearly using appropriate terminology",
                "Developing": "Communication has some clarity issues",
                "Beginning": "Communication is unclear or inappropriate"
            }
        }
        
        # Find matching template
        for key, level_descs in templates.items():
            if key in criterion_lower:
                return level_descs.get(level, base_desc)
        
        return base_desc
    
    def _get_key_characteristics(
        self,
        criterion: RubricCriterion,
        level: str
    ) -> list[str]:
        """Get key characteristics for a performance level"""
        criterion_lower = criterion.criterion_name.lower()
        
        characteristics = {
            "Exemplary": [
                "Consistently demonstrates mastery",
                "Exceeds requirements",
                "Shows deep understanding",
                "Work is polished and complete"
            ],
            "Proficient": [
                "Meets all requirements",
                "Demonstrates solid understanding",
                "Work is complete and accurate",
                "Minor improvements possible"
            ],
            "Developing": [
                "Meets some requirements",
                "Shows basic understanding",
                "Some errors present",
                "Additional work needed"
            ],
            "Beginning": [
                "Few requirements met",
                "Significant gaps in understanding",
                "Multiple errors present",
                "Extensive revision needed"
            ]
        }
        
        return characteristics.get(level, characteristics["Developing"])
    
    def get_marks_for_level(
        self,
        criterion: RubricCriterion,
        level: str
    ) -> tuple[int, int]:
        """Get marks range for a specific level"""
        descriptors = self.criterion_descriptors.get(criterion.criterion_id, [])
        for desc in descriptors:
            if desc.level == level:
                return desc.marks_range
        return (0, criterion.total_marks)
