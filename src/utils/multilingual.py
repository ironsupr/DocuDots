"""
Multi-lingual support utilities for DocuDots PDF structure extraction.
Handles text extraction and normalization across different languages.
"""

import re
from typing import Dict, List, Set, Optional
import unicodedata


class MultilingualSupport:
    """
    Provides multi-lingual text processing capabilities for PDF extraction.
    Supports text normalization, script detection, and language-aware processing.
    """
    
    def __init__(self):
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
            'japanese_hiragana': r'[\u3040-\u309f]',
            'japanese_katakana': r'[\u30a0-\u30ff]',
            'korean': r'[\uac00-\ud7af]',
            'thai': r'[\u0e00-\u0e7f]',
            'devanagari': r'[\u0900-\u097f]',
        }
        
        # Common stop words across languages (for better title detection)
        self.stop_words = {
            'english': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'},
            'spanish': {'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'pero', 'en', 'de', 'con', 'para'},
            'french': {'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'mais', 'en', 'de', 'avec', 'pour'},
            'german': {'der', 'die', 'das', 'ein', 'eine', 'und', 'oder', 'aber', 'in', 'von', 'mit', 'für'},
            'chinese': {'的', '了', '在', '是', '和', '有', '也', '不', '这', '那'},
            'japanese': {'の', 'に', 'は', 'を', 'が', 'で', 'と', 'から', 'まで', 'より'},
            'arabic': {'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك'},
            'hindi': {'का', 'की', 'के', 'में', 'से', 'को', 'पर', 'और', 'है', 'हैं'},
        }
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing across languages.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
        
        # Unicode normalization (NFC form)
        text = unicodedata.normalize('NFC', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Handle right-to-left languages (Arabic, Hebrew)
        if self.detect_script(text) == 'arabic':
            # Remove Arabic diacritics for better matching
            text = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', text)
        
        return text
    
    def detect_script(self, text: str) -> str:
        """
        Detect the primary script used in the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected script name
        """
        if not text:
            return 'unknown'
        
        script_counts = {}
        
        for script, pattern in self.script_patterns.items():
            matches = len(re.findall(pattern, text))
            if matches > 0:
                script_counts[script] = matches
        
        if not script_counts:
            return 'unknown'
        
        # Return script with highest count
        return max(script_counts, key=script_counts.get)
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on script and patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code
        """
        script = self.detect_script(text)
        
        # Script-based language mapping
        script_language_map = {
            'latin': 'english',  # Default to English for Latin script
            'cyrillic': 'russian',
            'arabic': 'arabic',
            'chinese': 'chinese',
            'japanese_hiragana': 'japanese',
            'japanese_katakana': 'japanese',
            'korean': 'korean',
            'thai': 'thai',
            'devanagari': 'hindi',
        }
        
        base_language = script_language_map.get(script, 'english')
        
        # For Latin script, try to detect specific language
        if script == 'latin':
            text_lower = text.lower()
            
            # Check for language-specific patterns
            for lang, patterns in self.heading_patterns.items():
                if lang in ['spanish', 'french', 'german']:
                    for pattern in patterns:
                        if re.search(pattern, text_lower, re.IGNORECASE):
                            return lang
        
        return base_language
    
    def is_heading_text(self, text: str, language: str = None) -> bool:
        """
        Check if text appears to be a heading based on language patterns.
        
        Args:
            text: Text to check
            language: Language to use for pattern matching
            
        Returns:
            True if text appears to be a heading
        """
        if not text:
            return False
        
        if not language:
            language = self.detect_language(text)
        
        text_lower = text.lower()
        
        # Check language-specific heading patterns
        patterns = self.heading_patterns.get(language, self.heading_patterns['english'])
        
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        # Universal heading indicators
        universal_patterns = [
            r'^\d+\.?\s*[A-Z\u00C0-\u017F\u0400-\u04FF\u4e00-\u9fff]',  # Numbered sections
            r'^[IVX]+\.?\s*[A-Z\u00C0-\u017F\u0400-\u04FF\u4e00-\u9fff]',  # Roman numerals
            r'^[A-Z\u00C0-\u017F\u0400-\u04FF\u4e00-\u9fff][A-Z\u00C0-\u017F\u0400-\u04FF\u4e00-\u9fff\s]{2,}$',  # All caps
        ]
        
        for pattern in universal_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def enhance_text_extraction(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        Enhance text blocks with language-aware processing.
        
        Args:
            text_blocks: List of text block dictionaries
            
        Returns:
            Enhanced text blocks with language information
        """
        enhanced_blocks = []
        
        for block in text_blocks:
            text = block.get('text', '')
            
            # Normalize text
            normalized_text = self.normalize_text(text)
            
            # Detect language and script
            language = self.detect_language(normalized_text)
            script = self.detect_script(normalized_text)
            
            # Check if it's likely a heading
            is_heading_candidate = self.is_heading_text(normalized_text, language)
            
            # Create enhanced block
            enhanced_block = block.copy()
            enhanced_block.update({
                'text': text,  # Keep original text
                'normalized_text': normalized_text,
                'detected_language': language,
                'detected_script': script,
                'is_heading_candidate': is_heading_candidate,
            })
            
            enhanced_blocks.append(enhanced_block)
        
        return enhanced_blocks
    
    def get_language_config(self, language: str) -> Dict:
        """
        Get language-specific configuration for text processing.
        
        Args:
            language: Language code
            
        Returns:
            Configuration dictionary
        """
        configs = {
            'english': {
                'reading_direction': 'ltr',
                'word_separator': ' ',
                'punctuation': r'[.!?;:]',
                'case_sensitive': False,
            },
            'arabic': {
                'reading_direction': 'rtl',
                'word_separator': ' ',
                'punctuation': r'[.!?؟;:]',
                'case_sensitive': False,
            },
            'chinese': {
                'reading_direction': 'ltr',
                'word_separator': '',
                'punctuation': r'[。！？；：]',
                'case_sensitive': False,
            },
            'japanese': {
                'reading_direction': 'ltr',
                'word_separator': '',
                'punctuation': r'[。！？；：]',
                'case_sensitive': False,
            },
        }
        
        return configs.get(language, configs['english'])
