"""
Intelligence Service
Service layer for loading and managing intelligence objects.
"""

from __future__ import annotations

import logging
from typing import Optional

from ..core.schemas.intelligence_objects import (
    FullIntelligenceObject, ConceptIntelligence, LearningOutcomeIntelligence,
    CompetencyIntelligence
)
from ..intelligence.data_loader import IntelligenceDataLoader

logger = logging.getLogger(__name__)


class IntelligenceService:
    """
    Service for loading and managing intelligence objects.
    """
    
    def __init__(self, csv_path: str):
        self.data_loader = IntelligenceDataLoader(csv_path)
        self._cache: dict[str, FullIntelligenceObject] = {}
    
    def load_for_assignment(
        self,
        grade: int,
        subject: str,
        chapter: str
    ) -> Optional[FullIntelligenceObject]:
        """
        Load intelligence for a specific assignment.
        
        Args:
            grade: Grade level
            subject: Subject name
            chapter: Chapter identifier
            
        Returns:
            FullIntelligenceObject or None
        """
        cache_key = f"{grade}_{subject}_{chapter}"
        
        # Check cache
        if cache_key in self._cache:
            logger.info(f"Cache hit for: {cache_key}")
            return self._cache[cache_key]
        
        try:
            # Try to load by chapter
            intelligence_list = self.data_loader.load_intelligence_by_chapter(chapter)
            
            # Filter by grade and subject if needed
            for intel in intelligence_list:
                if (intel.curriculum.grade == grade and 
                    intel.curriculum.subject.value.lower() == subject.lower()):
                    self._cache[cache_key] = intel
                    return intel
            
            # Return first match if exact match not found
            if intelligence_list:
                self._cache[cache_key] = intelligence_list[0]
                return intelligence_list[0]
            
            # Try loading by subject
            subject_intel = self.data_loader.load_intelligence_by_subject(subject)
            if subject_intel:
                self._cache[cache_key] = subject_intel[0]
                return subject_intel[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load intelligence: {e}")
            return None
    
    def load_all(self) -> list[FullIntelligenceObject]:
        """Load all intelligence objects"""
        try:
            return self.data_loader.load_all_intelligence()
        except Exception as e:
            logger.error(f"Failed to load all intelligence: {e}")
            return []
    
    def get_concepts_for_chapter(self, chapter: str) -> list[ConceptIntelligence]:
        """Get all concepts for a chapter"""
        intel = self.load_for_assignment(0, "", chapter)
        return intel.concepts if intel else []
    
    def get_outcomes_for_chapter(self, chapter: str) -> list[LearningOutcomeIntelligence]:
        """Get all learning outcomes for a chapter"""
        intel = self.load_for_assignment(0, "", chapter)
        return intel.learning_outcomes if intel else []
    
    def get_competencies_for_chapter(self, chapter: str) -> list[CompetencyIntelligence]:
        """Get all competencies for a chapter"""
        intel = self.load_for_assignment(0, "", chapter)
        return intel.competencies if intel else []
    
    def clear_cache(self) -> None:
        """Clear the intelligence cache"""
        self._cache.clear()
        logger.info("Intelligence cache cleared")
