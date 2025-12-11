"""
Production-grade translation manager with fallback chain, retry logic, and caching.

Fallback Chain:
1. Google Cloud Translation API (primary)
2. googletrans (fallback)
3. Translation cache (offline)
4. Original text (last resort)

Features:
- Retry logic with exponential backoff
- File-based caching (.translation_cache.json)
- Comprehensive logging
- Configurable via config.py + .env
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TranslationManager:
    """
    Manages translations with fallback chain and caching.
    
    Try in order:
    1. Cache (fastest)
    2. Google Cloud Translation API (primary)
    3. googletrans (fallback)
    4. Return original text (last resort)
    """
    
    def __init__(self, config=None):
        """
        Initialize translation manager.
        
        Parameters:
            config: Config module (optional). If None, imports from config.py
        """
        try:
            # Import config if not provided
            if config is None:
                from config import (
                    USE_GOOGLE_CLOUD_API, GOOGLE_CLOUD_PROJECT_ID,
                    GOOGLE_CLOUD_CREDENTIALS, USE_GOOGLETRANS_FALLBACK,
                    TRANSLATION_MAX_RETRIES, TRANSLATION_RETRY_BACKOFF,
                    ENABLE_TRANSLATION_CACHE, CACHE_FILE_PATH, CACHE_SIZE_LIMIT,
                    TRANSLATION_API_TIMEOUT, SOURCE_LANGUAGE, TARGET_LANGUAGE
                )
                self.config = {
                    'use_google_cloud': USE_GOOGLE_CLOUD_API,
                    'project_id': GOOGLE_CLOUD_PROJECT_ID,
                    'credentials': GOOGLE_CLOUD_CREDENTIALS,
                    'fallback_enabled': USE_GOOGLETRANS_FALLBACK,
                    'max_retries': TRANSLATION_MAX_RETRIES,
                    'backoff': TRANSLATION_RETRY_BACKOFF,
                    'cache_enabled': ENABLE_TRANSLATION_CACHE,
                    'cache_file': CACHE_FILE_PATH,
                    'cache_limit': CACHE_SIZE_LIMIT,
                    'timeout': TRANSLATION_API_TIMEOUT,
                    'source_lang': SOURCE_LANGUAGE,
                    'target_lang': TARGET_LANGUAGE,
                }
            else:
                self.config = self._parse_config(config)
            
            # Initialize APIs
            self.google_cloud_client = None
            self.googletrans_translator = None
            
            if self.config['use_google_cloud']:
                self._init_google_cloud()
            
            if self.config['fallback_enabled']:
                self._init_googletrans()
            
            # Load cache
            self.cache = {}
            self.cache_stats = {'hits': 0, 'misses': 0}
            if self.config['cache_enabled']:
                self._load_cache()
            
            logger.info("TranslationManager initialized successfully")
            logger.info(f"Fallback chain: Cache → GoogleCloud → googletrans → Original")
            
        except Exception as e:
            logger.error(f"Failed to initialize TranslationManager: {e}")
            # Don't raise - allow graceful degradation
            self.config['use_google_cloud'] = False
            self.config['fallback_enabled'] = True
            self.cache = {}
            self.cache_stats = {'hits': 0, 'misses': 0}
    
    def translate(self, text: str, src: str = "ja", dest: str = "vi") -> 'TranslationResult':
        """
        Translate text using fallback chain.
        
        Parameters:
            text: Text to translate
            src: Source language (default: ja)
            dest: Destination language (default: vi)
            
        Returns:
            TranslationResult: Object with .text property (compatible with googletrans)
                  Example: obj.text == "translated text"
        """
        try:
            if not text or not isinstance(text, str):
                return TranslationResult("")
            
            # Check cache first (fastest)
            cached = self._get_cached_translation(text, src, dest)
            if cached is not None:
                self.cache_stats['hits'] += 1
                logger.debug(f"Cache hit: '{text[:50]}...' → '{cached[:50]}...'")
                return TranslationResult(cached)
            
            self.cache_stats['misses'] += 1
            
            # Try Google Cloud API (primary)
            if self.config['use_google_cloud'] and self.google_cloud_client:
                try:
                    result = self._translate_with_google_cloud(text, src, dest)
                    if result:
                        self._cache_translation(text, result, src, dest)
                        logger.debug(f"Google Cloud translated: '{text[:50]}...'")
                        return TranslationResult(result)
                except Exception as e:
                    logger.warning(f"Google Cloud API failed: {e}. Trying fallback...")
            
            # Try googletrans (fallback)
            if self.config['fallback_enabled'] and self.googletrans_translator:
                try:
                    result = self._translate_with_googletrans(text, src, dest)
                    if result:
                        self._cache_translation(text, result, src, dest)
                        logger.debug(f"googletrans translated: '{text[:50]}...'")
                        return TranslationResult(result)
                except Exception as e:
                    logger.warning(f"googletrans failed: {e}")
            
            # Try cache again (offline mode)
            logger.warning(f"All APIs failed for '{text[:50]}...'. Using original text.")
            return TranslationResult(text)
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return TranslationResult(text)
    
    def batch_translate(self, texts: list, src: str = "ja", dest: str = "vi") -> list:
        """
        Translate list of texts. Returns list of TranslationResult objects.
        
        Parameters:
            texts: List of text strings
            src: Source language
            dest: Destination language
            
        Returns:
            list: List of TranslationResult objects
        """
        return [self.translate(text, src, dest) for text in texts]
    
    def _translate_with_google_cloud(self, text: str, src: str, dest: str) -> Optional[str]:
        """
        Translate using Google Cloud Translation API.
        
        Parameters:
            text: Text to translate
            src: Source language
            dest: Destination language
            
        Returns:
            str: Translated text or None if failed
        """
        if not self.google_cloud_client:
            return None
        
        try:
            # Use retry logic for Google Cloud API
            return self._translate_with_retry(
                self._do_google_cloud_translation,
                text, src, dest
            )
        except Exception as e:
            logger.error(f"Google Cloud translation error: {e}")
            return None
    
    def _do_google_cloud_translation(self, text: str, src: str, dest: str) -> str:
        """Actual Google Cloud translation call."""
        from google.cloud import translate
        
        result = self.google_cloud_client.translate_text(
            text=text,
            source_language_code=self._map_language_code(src),
            target_language_code=self._map_language_code(dest),
        )
        return result['translatedText']
    
    def _translate_with_googletrans(self, text: str, src: str, dest: str) -> Optional[str]:
        """
        Translate using googletrans (fallback).
        
        Parameters:
            text: Text to translate
            src: Source language
            dest: Destination language
            
        Returns:
            str: Translated text or None if failed
        """
        if not self.googletrans_translator:
            return None
        
        try:
            return self._translate_with_retry(
                self._do_googletrans_translation,
                text, src, dest
            )
        except Exception as e:
            logger.error(f"googletrans translation error: {e}")
            return None
    
    def _do_googletrans_translation(self, text: str, src: str, dest: str) -> str:
        """Actual googletrans translation call."""
        result = self.googletrans_translator.translate(text, src_lang=src, dest_lang=dest)
        return result['text']
    
    def _translate_with_retry(self, method, text: str, src: str, dest: str) -> str:
        """
        Wrapper to add retry logic with exponential backoff.
        
        Retries with backoff:
        - Attempt 1: Immediate
        - Attempt 2: Wait 1s
        - Attempt 3: Wait 2s
        - Attempt 4: Wait 4s (if max_retries=3, stops after attempt 3)
        """
        max_retries = self.config.get('max_retries', 3)
        backoff = self.config.get('backoff', 1.0)
        
        for attempt in range(1, max_retries + 1):
            try:
                return method(text, src, dest)
            except Exception as e:
                if attempt < max_retries:
                    wait_time = backoff * (2 ** (attempt - 1))
                    logger.warning(
                        f"Translation attempt {attempt} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Translation failed after {max_retries} attempts")
                    raise
    
    def _init_google_cloud(self):
        """Initialize Google Cloud Translation client."""
        try:
            from google.cloud import translate
            
            if self.config['project_id']:
                self.google_cloud_client = translate.TranslationServiceClient()
                logger.info("Google Cloud Translation client initialized")
            else:
                logger.warning("GOOGLE_CLOUD_PROJECT_ID not set. Skipping Google Cloud API.")
                self.config['use_google_cloud'] = False
                
        except ImportError:
            logger.warning("google-cloud-translate not installed. Install with: pip install google-cloud-translate")
            self.config['use_google_cloud'] = False
        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud: {e}")
            self.config['use_google_cloud'] = False
    
    def _init_googletrans(self):
        """Initialize googletrans as fallback."""
        try:
            from googletrans import Translator
            self.googletrans_translator = Translator()
            logger.info("googletrans fallback initialized")
        except ImportError:
            logger.error("googletrans not installed!")
            self.config['fallback_enabled'] = False
        except Exception as e:
            logger.warning(f"Failed to initialize googletrans: {e}")
            self.config['fallback_enabled'] = False
    
    def _get_cached_translation(self, text: str, src: str, dest: str) -> Optional[str]:
        """Get translation from cache."""
        if not self.config['cache_enabled']:
            return None
        
        lang_key = f"{src}->{dest}"
        if lang_key not in self.cache:
            return None
        
        return self.cache[lang_key].get(text)
    
    def _cache_translation(self, text: str, result: str, src: str, dest: str):
        """Add translation to cache."""
        if not self.config['cache_enabled']:
            return
        
        lang_key = f"{src}->{dest}"
        if lang_key not in self.cache:
            self.cache[lang_key] = {}
        
        # Limit cache size
        if len(self.cache[lang_key]) < self.config['cache_limit']:
            self.cache[lang_key][text] = result
            self._save_cache()
    
    def _load_cache(self):
        """Load cache from file."""
        try:
            cache_file = Path(self.config['cache_file'])
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = {k: v for k, v in data.items() if k != 'stats'}
                    self.cache_stats = data.get('stats', {'hits': 0, 'misses': 0})
                logger.info(f"Loaded cache with {sum(len(v) for v in self.cache.values())} entries")
            else:
                logger.info("No existing cache file")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            cache_file = Path(self.config['cache_file'])
            data = dict(self.cache)
            data['stats'] = self.cache_stats
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _map_language_code(self, lang: str) -> str:
        """Map language codes from googletrans format to Google Cloud format."""
        mapping = {
            'ja': 'ja',
            'vi': 'vi',
            'en': 'en',
        }
        return mapping.get(lang, lang)
    
    def _parse_config(self, config_module) -> Dict:
        """Parse config module into dictionary."""
        return {
            'use_google_cloud': getattr(config_module, 'USE_GOOGLE_CLOUD_API', False),
            'project_id': getattr(config_module, 'GOOGLE_CLOUD_PROJECT_ID'),
            'credentials': getattr(config_module, 'GOOGLE_CLOUD_CREDENTIALS'),
            'fallback_enabled': getattr(config_module, 'USE_GOOGLETRANS_FALLBACK', True),
            'max_retries': getattr(config_module, 'TRANSLATION_MAX_RETRIES', 3),
            'backoff': getattr(config_module, 'TRANSLATION_RETRY_BACKOFF', 1.0),
            'cache_enabled': getattr(config_module, 'ENABLE_TRANSLATION_CACHE', True),
            'cache_file': getattr(config_module, 'CACHE_FILE_PATH', '.translation_cache.json'),
            'cache_limit': getattr(config_module, 'CACHE_SIZE_LIMIT', 10000),
            'timeout': getattr(config_module, 'TRANSLATION_API_TIMEOUT', 30),
            'source_lang': getattr(config_module, 'SOURCE_LANGUAGE', 'ja'),
            'target_lang': getattr(config_module, 'TARGET_LANGUAGE', 'vi'),
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_translations = sum(len(v) for v in self.cache.values())
        hit_rate = self.cache_stats['hits'] / max(1, self.cache_stats['hits'] + self.cache_stats['misses'])
        return {
            'total_entries': total_translations,
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate': hit_rate
        }


class TranslationResult:
    """
    Wrapper to maintain compatibility with googletrans API.
    googletrans returns object with .text property.
    """
    
    def __init__(self, text: str):
        self.text = text
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"TranslationResult('{self.text[:50]}...')"
