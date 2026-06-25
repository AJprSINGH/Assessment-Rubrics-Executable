"""
Intelligence Data Loader - Load and parse semantic intelligence from CSV
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from ..core.schemas.intelligence_objects import (
    Board, Subject, BloomLevel, DOKLevel, DifficultyLevel, KnowledgeType,
    CurriculumIntelligence, ConceptIntelligence, LearningOutcomeIntelligence,
    KnowledgeItem, AbilityItem, SkillItem, ObservableBehaviour, LearningObjective,
    BloomIntelligence, KSAIntelligence, CompetencyIntelligence, PerformanceIndicator,
    AssessmentIntelligence, AssessmentBlueprint, PedagogicalIntelligence,
    MisconceptionIntelligence, FullIntelligenceObject, CompetencyLevel
)

logger = logging.getLogger(__name__)


class IntelligenceDataLoader:
    """
    Loads and parses semantic intelligence data from CSV files.
    Transforms raw CSV data into structured CIOs.
    """
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df: Optional[pd.DataFrame] = None
        
        # Bloom's taxonomy cognitive verbs mapping
        self.bloom_verbs = {
            "Remember": ["list", "define", "identify", "recall", "name", "state", "describe", "recognize"],
            "Understand": ["explain", "summarize", "interpret", "classify", "compare", "discuss", "describe"],
            "Apply": ["use", "apply", "demonstrate", "solve", "execute", "implement", "compute"],
            "Analyze": ["analyze", "differentiate", "examine", "investigate", "categorize", "distinguish"],
            "Evaluate": ["evaluate", "assess", "judge", "critique", "justify", "argue", "defend"],
            "Create": ["create", "design", "develop", "construct", "formulate", "compose", "produce"]
        }
    
    def load(self) -> pd.DataFrame:
        """Load CSV file into DataFrame"""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} records from {self.csv_path}")
            return self.df
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise
    
    def parse_curriculum_intelligence(self, row: dict) -> CurriculumIntelligence:
        """Parse curriculum intelligence from CSV row"""
        # Determine board from standard
        standard = str(row.get('standard', ''))
        board = Board.CBSE  # Default
        if 'ICSE' in standard.upper():
            board = Board.ICSE
        elif 'IB' in standard.upper():
            board = Board.IB
        elif 'Cambridge' in standard.upper():
            board = Board.CAMBRIDGE
            
        return CurriculumIntelligence(
            board=board,
            grade=int(row.get('grade_level', row.get('grade', 10))),
            subject=Subject(row.get('subject_name', 'Science').title()),
            unit=row.get('unit_name'),
            chapter=str(row.get('chapter_number', '')),
            chapter_summary=self._extract_chapter_summary(row),
            standard=standard,
            standard_id=str(row.get('standard_id', ''))
        )
    
    def _extract_chapter_summary(self, row: dict) -> Optional[str]:
        """Extract chapter summary from full_intelligence_json"""
        full_json = row.get('full_intelegance_json', '{}')
        try:
            data = json.loads(full_json) if isinstance(full_json, str) else full_json
            return data.get('chapter_summary')
        except:
            return None
    
    def parse_concept_intelligence(self, row: dict) -> list[ConceptIntelligence]:
        """Parse concept intelligence from CSV row"""
        full_json = row.get('full_intelegance_json', '{}')
        try:
            data = json.loads(full_json) if isinstance(full_json, str) else full_json
            concepts_data = data.get('concepts', [])
        except:
            concepts_data = []
        
        concepts = []
        total_concepts = int(row.get('total_concepts', 1))
        
        if not concepts_data:
            # Generate a default concept based on chapter
            concepts.append(ConceptIntelligence(
                concept_id=f"CONCEPT_{row.get('id', 1)}",
                concept_name=row.get('chapter_name', row.get('chapter', 'General')),
                definition=f"Core concepts from {row.get('chapter_name', 'chapter')}",
                difficulty=DifficultyLevel.MEDIUM,
                confidence=0.8
            ))
        else:
            for concept_data in concepts_data[:total_concepts]:
                concept = concept_data.get('concept', {})
                
                # Safely parse list fields - handle both strings and dicts
                prerequisites = self._parse_string_list(concept_data.get('prerequisites', []))
                misconceptions = self._parse_string_list(concept_data.get('misconceptions', []))
                real_world_applications = self._parse_string_list(concept_data.get('real_world_applications', []))
                pedagogy_suggestions = self._parse_string_list(concept_data.get('pedagogy_suggestions', []))
                
                concepts.append(ConceptIntelligence(
                    concept_id=concept.get('concept_id', f"CONCEPT_{len(concepts)}"),
                    concept_name=concept.get('concept_name', 'Unknown'),
                    concept_type=concept.get('concept_type', 'Concept'),
                    definition=concept.get('definition'),
                    importance=concept.get('importance', 'Core'),
                    difficulty=DifficultyLevel(concept.get('difficulty', 'Medium')),
                    confidence=concept.get('confidence', 0.9),
                    knowledge_items=self._parse_knowledge_items(concept_data.get('knowledge_items', [])),
                    abilities=self._parse_abilities(concept_data.get('abilities', [])),
                    skills=self._parse_skills(concept_data.get('skills', [])),
                    prerequisites=prerequisites,
                    misconceptions=misconceptions,
                    real_world_applications=real_world_applications,
                    pedagogy_suggestions=pedagogy_suggestions
                ))
        
        return concepts
    
    def _parse_string_list(self, items) -> list[str]:
        """Parse a list that might contain strings or dicts"""
        result = []
        for item in items:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Try to extract string value from dict
                for key in ['name', 'value', 'text', 'statement']:
                    if key in item:
                        result.append(str(item[key]))
                        break
                else:
                    # Use first string value found
                    for v in item.values():
                        if isinstance(v, str):
                            result.append(v)
                            break
        return result
    
    def _parse_knowledge_items(self, items: list) -> list[KnowledgeItem]:
        """Parse knowledge items from concept data"""
        return [
            KnowledgeItem(
                knowledge=item.get('knowledge', ''),
                statement=item.get('statement', ''),
                knowledge_type=KnowledgeType(item.get('knowledge_type', 'Fact')),
                confidence=item.get('confidence', 0.9),
                concept_name=item.get('concept_name', '')
            )
            for item in items
        ]
    
    def _parse_abilities(self, items: list) -> list[AbilityItem]:
        """Parse ability items from concept data"""
        return [
            AbilityItem(
                ability=item.get('ability', ''),
                verb=item.get('verb', ''),
                description=item.get('description', ''),
                knowledge_refs=item.get('knowledge_refs', []),
                concept_name=item.get('concept_name', ''),
                blooms_level=BloomLevel(item.get('blooms_level', 'Understand'))
            )
            for item in items
        ]
    
    def _parse_skills(self, items: list) -> list[SkillItem]:
        """Parse skill items from concept data"""
        return [
            SkillItem(
                skill=item.get('skill', ''),
                description=item.get('description', ''),
                concept_name=item.get('concept_name', ''),
                related_concepts=item.get('related_concepts', [])
            )
            for item in items
        ]
    
    def parse_learning_outcomes(self, row: dict) -> list[LearningOutcomeIntelligence]:
        """Parse learning outcomes from CSV row"""
        full_json = row.get('full_intelegance_json', '{}')
        try:
            data = json.loads(full_json) if isinstance(full_json, str) else full_json
            outcomes_data = data.get('learning_outcomes', [])
        except:
            outcomes_data = []
        
        outcomes = []
        
        if not outcomes_data:
            # Generate default outcomes from learning_objectives
            learning_obj = row.get('learning_objectives', row.get('learning_objective', ''))
            if learning_obj:
                objectives = [o.strip() for o in str(learning_obj).split('.') if o.strip()]
                for i, obj in enumerate(objectives[:5]):  # Limit to 5
                    outcomes.append(LearningOutcomeIntelligence(
                        outcome_id=f"LO_{row.get('id', 1)}_{i+1}",
                        outcome_statement=obj,
                        blooms_level=self._infer_bloom_level(obj),
                        dok_level=DOKLevel.L2
                    ))
        else:
            for outcome_data in outcomes_data:
                objectives = [
                    LearningObjective(
                        objective=obj.get('objective', ''),
                        blooms_level=BloomLevel(obj.get('blooms_level', 'Understand')),
                        dok_level=DOKLevel(obj.get('dok_level', '2')),
                        difficulty=DifficultyLevel(obj.get('difficulty', 'Medium'))
                    )
                    for obj in outcome_data.get('objectives', [])
                ]
                
                behaviours = [
                    ObservableBehaviour(
                        behaviour=beh.get('behaviour', ''),
                        description=beh.get('description', ''),
                        blooms_level=BloomLevel(beh.get('blooms_level', 'Understand')),
                        assessment_method=beh.get('assessment_method', [])
                    )
                    for beh in outcome_data.get('observable_behaviours', [])
                ]
                
                outcomes.append(LearningOutcomeIntelligence(
                    outcome_id=outcome_data.get('outcome_id', f"LO_{len(outcomes)}"),
                    outcome_statement=outcome_data.get('outcome_statement', ''),
                    objectives=objectives,
                    observable_behaviours=behaviours,
                    concepts_covered=outcome_data.get('concepts_covered', []),
                    blooms_level=BloomLevel(outcome_data.get('blooms_level', 'Understand')),
                    dok_level=DOKLevel(outcome_data.get('dok_level', '2'))
                ))
        
        return outcomes
    
    def _infer_bloom_level(self, text: str) -> BloomLevel:
        """Infer Bloom's level from text using verbs"""
        text_lower = text.lower()
        for level, verbs in self.bloom_verbs.items():
            if any(verb in text_lower for verb in verbs):
                return BloomLevel(level)
        return BloomLevel.UNDERSTAND
    
    def parse_bloom_intelligence(self) -> list[BloomIntelligence]:
        """Parse Bloom's taxonomy intelligence"""
        blooms = []
        for level, verbs in self.bloom_verbs.items():
            level_num = list(self.bloom_verbs.keys()).index(level) + 1
            blooms.append(BloomIntelligence(
                level=BloomLevel(level),
                description=self._get_bloom_description(level),
                cognitive_verbs=verbs,
                complexity_weight=level_num / 6.0
            ))
        return blooms
    
    def _get_bloom_description(self, level: str) -> str:
        """Get description for Bloom's level"""
        descriptions = {
            "Remember": "Recall facts and basic concepts",
            "Understand": "Explain ideas or concepts",
            "Apply": "Use information in new situations",
            "Analyze": "Draw connections among ideas",
            "Evaluate": "Justify a decision or action",
            "Create": "Produce new or original work"
        }
        return descriptions.get(level, "")
    
    def parse_ksa_intelligence(self, row: dict) -> KSAIntelligence:
        """Parse KSA intelligence from CSV row"""
        return KSAIntelligence(
            knowledge=[
                KnowledgeItem(
                    knowledge=item,
                    statement=item,
                    knowledge_type=KnowledgeType.FACT,
                    confidence=0.9,
                    concept_name=""
                )
                for item in self._split_list(row.get('knowledge', ''))
            ],
            problem_solving=self._split_list(row.get('skill', '')),
            reasoning=self._split_list(row.get('ability', '')),
            all_verbs=self._get_all_verbs(row)
        )
    
    def _split_list(self, value: str) -> list[str]:
        """Split comma-separated values"""
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [v.strip() for v in str(value).split(',') if v.strip()]
    
    def _get_all_verbs(self, row: dict) -> list[str]:
        """Extract all cognitive verbs from row"""
        verbs = set()
        for level, level_verbs in self.bloom_verbs.items():
            verbs.update(level_verbs)
        return list(verbs)
    
    def parse_competency_intelligence(self, row: dict) -> list[CompetencyIntelligence]:
        """Parse competency intelligence from CSV row"""
        competencies = []
        competency_str = row.get('competency', '')
        
        if competency_str:
            comps = self._split_list(competency_str)
            for i, comp in enumerate(comps):
                competencies.append(CompetencyIntelligence(
                    competency_id=f"COMP_{row.get('id', 1)}_{i+1}",
                    competency_name=comp,
                    description=f"Demonstrate proficiency in {comp}",
                    competency_level=CompetencyLevel.INTERMEDIATE,
                    related_concepts=[row.get('chapter_name', '')]
                ))
        
        return competencies
    
    def parse_assessment_intelligence(self, row: dict) -> AssessmentIntelligence:
        """Parse assessment intelligence from CSV row"""
        full_json = row.get('full_intelegance_json', '{}')
        try:
            data = json.loads(full_json) if isinstance(full_json, str) else full_json
            blueprints = data.get('assessment_blueprints', [])
        except:
            blueprints = []
        
        assessment_blueprints = []
        for bp in blueprints:
            assessment_blueprints.append(AssessmentBlueprint(
                assessment_type=bp.get('assessment_type', 'Project'),
                bloom_level=BloomLevel(bp.get('bloom_level', 'Apply')),
                dok_level=DOKLevel(bp.get('dok_level', '3')),
                difficulty=DifficultyLevel(bp.get('difficulty', 'Medium')),
                marks=bp.get('marks', 5),
                recommended_question=bp.get('recommended_question')
            ))
        
        return AssessmentIntelligence(
            assessment_types=["Project"],  # Default for rubric generation
            rubric_type="Analytical",
            assessment_weightage={"Knowledge": 0.3, "Application": 0.4, "Analysis": 0.3},
            performance_scale=["Exemplary", "Proficient", "Developing", "Beginning"],
            assessment_blueprints=assessment_blueprints
        )
    
    def parse_pedagogical_intelligence(self, row: dict) -> PedagogicalIntelligence:
        """Parse pedagogical intelligence from CSV row"""
        full_json = row.get('full_intelegance_json', '{}')
        try:
            data = json.loads(full_json) if isinstance(full_json, str) else full_json
            pedagogy = data.get('pedagogy', [])
        except:
            pedagogy = []
        
        return PedagogicalIntelligence(
            strategies=pedagogy if pedagogy else ["Direct Instruction", "Inquiry-Based Learning"],
            assessment_modalities=["Project", "Portfolio", "Presentation"],
            differentiation_strategies=["Scaffolding", "Multiple Intelligences"],
            engagement_techniques=["Real-World Connections", "Collaborative Learning"]
        )
    
    def parse_misconception_intelligence(self, row: dict) -> MisconceptionIntelligence:
        """Parse misconception intelligence from CSV row"""
        misconceptions = self._split_list(row.get('misconceptions', ''))
        applications = self._split_list(row.get('real_world_applications', ''))
        
        return MisconceptionIntelligence(
            common_errors=misconceptions[:5] if misconceptions else [],
            learning_gaps=["Conceptual understanding gaps"],
            misconception_indicators=["Incorrect application", "Misidentified processes"],
            targeted_remediation=["Explicit instruction", "Practice with feedback"]
        )
    
    def parse_full_intelligence(self, row: dict) -> FullIntelligenceObject:
        """Parse complete intelligence object from CSV row"""
        curriculum = self.parse_curriculum_intelligence(row)
        
        return FullIntelligenceObject(
            curriculum=curriculum,
            concepts=self.parse_concept_intelligence(row),
            learning_outcomes=self.parse_learning_outcomes(row),
            blooms=self.parse_bloom_intelligence(),
            ksa=self.parse_ksa_intelligence(row),
            competencies=self.parse_competency_intelligence(row),
            assessment=self.parse_assessment_intelligence(row),
            pedagogy=self.parse_pedagogical_intelligence(row),
            misconceptions=self.parse_misconception_intelligence(row),
            extraction_id=str(row.get('id', '')),
            llm_model=row.get('llm_model', 'deepseek-v4-pro')
        )
    
    def load_intelligence_by_chapter(self, chapter_identifier: str) -> list[FullIntelligenceObject]:
        """Load intelligence objects filtered by chapter"""
        if self.df is None:
            self.load()
        
        # Filter by chapter number or name
        filtered = self.df[
            (self.df['chapter_id'].astype(str) == str(chapter_identifier)) |
            (self.df['chapter_number'].astype(str).str.contains(str(chapter_identifier), na=False))
        ]
        
        logger.info(f"Found {len(filtered)} records for chapter: {chapter_identifier}")
        
        return [self.parse_full_intelligence(row.to_dict()) for _, row in filtered.iterrows()]
    
    def load_intelligence_by_subject(self, subject: str) -> list[FullIntelligenceObject]:
        """Load intelligence objects filtered by subject"""
        if self.df is None:
            self.load()
        
        filtered = self.df[
            self.df['subject_name'].str.lower() == subject.lower()
        ]
        
        logger.info(f"Found {len(filtered)} records for subject: {subject}")
        
        return [self.parse_full_intelligence(row.to_dict()) for _, row in filtered.iterrows()]
    
    def load_all_intelligence(self) -> list[FullIntelligenceObject]:
        """Load all intelligence objects from CSV"""
        if self.df is None:
            self.load()
        
        return [self.parse_full_intelligence(row.to_dict()) for _, row in self.df.iterrows()]
