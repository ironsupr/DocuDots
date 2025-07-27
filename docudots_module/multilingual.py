"""
Multi-lingual support utilities for DocuDots PDF Analysis Module
================================================================
"""

import re
import unicodedata
from typing import Dict, List, Optional, Any


class MultilingualProcessor:
    """
    Provides multi-lingual text processing capabilities for PDF extraction.
    Supports text normalization, script detection, and language-aware processing.
    """
    
    def __init__(self):
        """Initialize multilingual processor with language patterns."""
        
        # Common heading patterns across languages
        self.heading_patterns = {
            'english': [
                r'\b(chapter|section|part|introduction|conclusion|summary|overview|abstract)\b',
                r'\b(table of contents|contents|index|references|bibliography|appendix)\b',
                r'\b\d+\.\s*[A-Z]',  # Numbered sections like "1. Introduction"
            ],
            'spanish': [
                r'\b(capítulo|sección|parte|introducción|conclusión|resumen|índice)\b',
                r'\b(contenido|referencias|bibliografía|apéndice)\b',
            ],
            'french': [
                r'\b(chapitre|section|partie|introduction|conclusion|résumé|index)\b',
                r'\b(contenu|références|bibliographie|annexe)\b',
            ],
            'german': [
                r'\b(kapitel|abschnitt|teil|einführung|fazit|zusammenfassung|index)\b',
                r'\b(inhalt|verzeichnis|literatur|anhang)\b',
            ],
            'chinese': [
                r'第[一二三四五六七八九十\d]+章',  # Chapter markers
                r'[目录|索引|摘要|总结|结论|附录]',
            ],
            'japanese': [
                r'第[一二三四五六七八九十\d]+章',
                r'[目次|索引|要約|結論|付録]',
            ],
            'arabic': [
                r'الفصل\s+[\d\u0660-\u0669]+',  # Arabic numerals
                r'[المحتويات|الفهرس|الملخص|الخاتمة|المراجع]',
            ],
            'hindi': [
                r'अध्याय\s+[\d०-९]+',
                r'[सूची|सारांश|निष्कर्ष|संदर्भ]',
            ],
        }
        
        # Script detection patterns
        self.script_patterns = {
            'latin': r'[A-Za-z]',
            'cyrillic': r'[\u0400-\u04FF]',
            'arabic': r'[\u0600-\u06FF]',
            'chinese': r'[\u4e00-\u9fff]',
            'japanese_hiragana': r'[\u3040-\u309F]',
            'japanese_katakana': r'[\u30A0-\u30FF]',
            'korean': r'[\uAC00-\uD7AF]',
            'devanagari': r'[\u0900-\u097F]',  # Hindi and other Devanagari scripts
            'thai': r'[\u0E00-\u0E7F]',
            'hebrew': r'[\u0590-\u05FF]',
        }
        
        # Language-specific text normalization rules
        self.normalization_rules = {
            'arabic': {
                'direction': 'rtl',
                'remove_diacritics': True,
                'normalize_numbers': True
            },
            'hebrew': {
                'direction': 'rtl',
                'remove_diacritics': True
            },
            'chinese': {
                'simplify_traditional': True,
                'remove_spaces': True
            },
            'japanese': {
                'normalize_width': True,
                'remove_spaces': True
            }
        }
    
    def process_text_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process text blocks with multilingual support.
        
        Args:
            blocks: List of text blocks from PDF extraction
            
        Returns:
            List of processed text blocks
        """
        processed_blocks = []
        
        for block in blocks:
            processed_block = block.copy()
            
            # Normalize text
            normalized_text = self.normalize_text(block['text'])
            processed_block['text'] = normalized_text
            processed_block['original_text'] = block['text']  # Keep original
            
            # Detect script/language
            script = self.detect_script(normalized_text)
            processed_block['script'] = script
            
            # Check if text matches heading patterns
            heading_score = self.calculate_heading_score(normalized_text)
            processed_block['heading_score'] = heading_score
            
            processed_blocks.append(processed_block)
        
        return processed_blocks
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for better processing across languages.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return text
        
        # Unicode normalization
        normalized = unicodedata.normalize('NFKC', text)
        
        # Remove excessive whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Detect script and apply script-specific normalization
        script = self.detect_script(normalized)
        
        if script in ['arabic', 'hebrew']:
            # Remove diacritics for RTL languages
            normalized = self._remove_diacritics(normalized)
        elif script in ['chinese', 'japanese']:
            # Normalize width characters
            normalized = self._normalize_width(normalized)
        
        return normalized
    
    def detect_script(self, text: str) -> str:
        """
        Detect the primary script of the text.
        
        Args:
            text: Input text
            
        Returns:
            Detected script name
        """
        if not text:
            return 'unknown'
        
        script_scores = {}
        text_length = len(text)
        
        for script_name, pattern in self.script_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if text_length > 0:
                script_scores[script_name] = matches / text_length
        
        if not script_scores:
            return 'unknown'
        
        # Return script with highest score
        primary_script = max(script_scores, key=script_scores.get)
        
        # Map script to language family
        script_to_language = {
            'latin': 'latin',
            'cyrillic': 'cyrillic',
            'arabic': 'arabic',
            'chinese': 'chinese',
            'japanese_hiragana': 'japanese',
            'japanese_katakana': 'japanese',
            'korean': 'korean',
            'devanagari': 'hindi',
            'thai': 'thai',
            'hebrew': 'hebrew'
        }
        
        return script_to_language.get(primary_script, primary_script)
    
    def calculate_heading_score(self, text: str) -> int:
        """
        Calculate heading likelihood score for text.
        
        Args:
            text: Input text
            
        Returns:
            Heading score (0-100)
        """
        if not text:
            return 0
        
        score = 0
        text_lower = text.lower()
        
        # Check against language-specific heading patterns
        for language, patterns in self.heading_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 30
                    break  # Don't double-count for same language
        
        # Additional scoring factors
        if len(text.split()) <= 8:  # Short text
            score += 10
        
        if text.isupper() or text.istitle():  # Capitalization
            score += 15
        
        if re.match(r'^\d+[\.\)]\s', text):  # Numbered headings
            score += 20
        
        if re.match(r'^[•·▪▫◦‣⁃]\s', text):  # Bullet points
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove diacritics from text."""
        return ''.join(
            char for char in unicodedata.normalize('NFD', text)
            if unicodedata.category(char) != 'Mn'
        )
    
    def _normalize_width(self, text: str) -> str:
        """Normalize full-width and half-width characters."""
        # Convert full-width to half-width for ASCII characters
        normalized = ''
        for char in text:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:  # Full-width ASCII range
                normalized += chr(code - 0xFEE0)
            else:
                normalized += char
        return normalized
    
    def get_language_info(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive language information for text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with language information
        """
        script = self.detect_script(text)
        heading_score = self.calculate_heading_score(text)
        
        return {
            'script': script,
            'heading_score': heading_score,
            'is_rtl': script in ['arabic', 'hebrew'],
            'normalized_text': self.normalize_text(text),
            'character_count': len(text),
            'word_count': len(text.split()) if script in ['latin', 'cyrillic'] else None
        }
