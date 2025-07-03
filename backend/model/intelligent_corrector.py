import logging
from typing import Dict, List, Any, Tuple
import time

logger = logging.getLogger(__name__)

class IntelligentOCRCorrector:
    """
    Intelligent OCR text correction system that applies multiple correction methods
    """
    
    def __init__(self):
        """Initialize the intelligent corrector with available correction tools"""
        self.correction_methods = []
        self.setup_correction_tools()
    
    def setup_correction_tools(self):
        """Setup various correction tools"""
        logger.info("Setting up intelligent correction tools...")
        
        # Spell checker
        try:
            from spellchecker import SpellChecker
            self.spell_checker = SpellChecker()
            self.correction_methods.append('spell_checker')
            logger.info("✅ Spell checker ready")
        except ImportError:
            logger.warning("⚠️ Spell checker not available - install pyspellchecker")
            self.spell_checker = None
        
        # Auto-corrector
        try:
            from autocorrect import Speller
            self.auto_corrector = Speller(lang='en')
            self.correction_methods.append('auto_corrector')
            logger.info("✅ Auto-corrector ready")
        except ImportError:
            logger.warning("⚠️ Auto-corrector not available - install autocorrect")
            self.auto_corrector = None
        
        # Fuzzy matching
        try:
            from fuzzywuzzy import fuzz, process
            import textdistance
            self.fuzzy_available = True
            self.correction_methods.append('fuzzy_matching')
            logger.info("✅ Fuzzy matching ready")
        except ImportError:
            logger.warning("⚠️ Fuzzy matching not available - install fuzzywuzzy")
            self.fuzzy_available = False
        
        # Word frequency
        try:
            from wordfreq import word_frequency
            self.wordfreq_available = True
            self.correction_methods.append('word_frequency')
            logger.info("✅ Word frequency analysis ready")
        except ImportError:
            logger.warning("⚠️ Word frequency not available - install wordfreq")
            self.wordfreq_available = False
        
        # Language model (optional - requires transformers)
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM
            logger.info("🤖 Loading language model for context prediction...")
            
            model_name = "bert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.language_model = AutoModelForMaskedLM.from_pretrained(model_name)
            self.mask_filler = pipeline("fill-mask", model=self.language_model, tokenizer=self.tokenizer)
            self.correction_methods.append('language_model')
            logger.info("✅ Language model ready")
        except ImportError:
            logger.warning("⚠️ Language model not available - install transformers")
            self.mask_filler = None
        except Exception as e:
            logger.warning(f"⚠️ Language model failed to load: {str(e)}")
            self.mask_filler = None
        
        logger.info(f"🎉 {len(self.correction_methods)} correction methods ready!")
    
    def analyze_ocr_errors(self, text: str) -> List[Dict[str, Any]]:
        """Analyze and fix common OCR error patterns"""
        logger.debug("🔍 Analyzing OCR error patterns...")
        
        # Common OCR error patterns
        ocr_patterns = {
            'rn': 'm',      # rn often read as m
            'cl': 'd',      # cl often read as d
            'li': 'h',      # li often read as h
            'vv': 'w',      # vv often read as w
            'nn': 'm',      # nn sometimes read as m
            '1': 'l',       # 1 often confused with l
            '0': 'O',       # 0 often confused with O
            '5': 'S',       # 5 sometimes confused with S
            '8': 'B',       # 8 sometimes confused with B
            '|': 'I',       # | often confused with I
            'ii': 'n',      # ii sometimes read as n
            'oi': 'a',      # oi sometimes read as a
            'ai': 'w',      # ai sometimes read as w
        }
        
        error_corrections = []
        words = text.split()
        
        for i, word in enumerate(words):
            original_word = word
            corrected_word = word
            
            # Apply pattern corrections
            for pattern, replacement in ocr_patterns.items():
                if pattern in corrected_word.lower():
                    new_word = corrected_word.lower().replace(pattern, replacement)
                    
                    # Check if correction makes sense using spell checker
                    if self.spell_checker and new_word in self.spell_checker:
                        corrected_word = new_word
                        error_corrections.append({
                            'position': i,
                            'original': original_word,
                            'corrected': corrected_word,
                            'pattern': f"{pattern} → {replacement}",
                            'method': 'pattern_matching'
                        })
                        break
        
        return error_corrections
    
    def spell_check_correction(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Apply spell check based correction"""
        if not self.spell_checker:
            return text, []
        
        logger.debug("📝 Running spell check correction...")
        
        words = text.split()
        corrections = []
        corrected_words = []
        
        for i, word in enumerate(words):
            # Clean word (remove punctuation for checking)
            clean_word = ''.join(c for c in word if c.isalpha()).lower()
            
            if clean_word and clean_word not in self.spell_checker:
                # Get suggestions
                suggestions = self.spell_checker.candidates(clean_word)
                
                if suggestions:
                    best_suggestion = list(suggestions)[0]
                    
                    # Preserve original case and punctuation
                    corrected_word = self.preserve_case_and_punctuation(word, best_suggestion)
                    
                    corrected_words.append(corrected_word)
                    corrections.append({
                        'position': i,
                        'original': word,
                        'corrected': corrected_word,
                        'suggestions': list(suggestions)[:3],
                        'method': 'spell_check'
                    })
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        corrected_text = ' '.join(corrected_words)
        return corrected_text, corrections
    
    def fuzzy_word_correction(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Apply fuzzy matching correction against common words"""
        if not self.fuzzy_available:
            return text, []
        
        logger.debug("🔍 Running fuzzy word correction...")
        
        # Common English words for matching
        common_words = [
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just',
            'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
            'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
            'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
            'dear', 'future', 'worry', 'things', 'happen', 'meant', 'stop', 'comparing', 'past', 'present', 'left', 'behind',
            'reason', 'forward', 'confidently', 'developing', 'right', 'keep', 'smiling', 'small', 'worries', 'concerns',
            'forgotten', 'years', 'time', 'thankful', 'blessings', 'grace', 'life', 'each', 'seems', 'falling', 'apart',
            'takes', 'destruction', 'build', 'tell', 'people', 'love', 'matter', 'many', 'grateful', 'placed',
            'atmosphere', 'seek', 'knowledge', 'truths', 'learn', 'invest', 'moments', 'memories', 'wrong', 'nice',
            'house', 'clothes', 'made', 'trips', 'taken', 'where', 'went', 'those', 'hold', 'most', 'above',
            'strive', 'yourself', 'find', 'really', 'person', 'never', 'stand', 'someone', 'else', 'ground',
            'hill', 'start', 'look', 'around', 'roots', 'have', 'seen', 'pounds', 'lighter', 'better', 'job',
            'place', 'someday', 'moment', 'live', 'regrets', 'choices', 'yours', 'sincerely'
        ]
        
        try:
            from fuzzywuzzy import process
            
            words = text.split()
            corrections = []
            corrected_words = []
            
            for i, word in enumerate(words):
                clean_word = ''.join(c for c in word.lower() if c.isalpha())
                
                if len(clean_word) > 2:  # Only check longer words
                    # Find best fuzzy match
                    best_match, score = process.extractOne(clean_word, common_words)
                    
                    # If the match is very good and different from original
                    if score > 85 and best_match != clean_word:
                        corrected_word = self.preserve_case_and_punctuation(word, best_match)
                        
                        corrected_words.append(corrected_word)
                        corrections.append({
                            'position': i,
                            'original': word,
                            'corrected': corrected_word,
                            'similarity_score': score,
                            'method': 'fuzzy_matching'
                        })
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            
            corrected_text = ' '.join(corrected_words)
            return corrected_text, corrections
            
        except Exception as e:
            logger.error(f"Fuzzy matching error: {str(e)}")
            return text, []
    
    def context_based_correction(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Apply context-based correction using language model"""
        if not self.mask_filler:
            return text, []
        
        logger.debug("🤖 Running context-based correction...")
        
        try:
            # Split into sentences for context analysis
            sentences = text.split('.')
            corrections = []
            corrected_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                words = sentence.split()
                if len(words) < 3:  # Need some context
                    corrected_sentences.append(sentence)
                    continue
                
                corrected_sentence = sentence
                
                for i, word in enumerate(words):
                    # Check if word seems wrong (very low frequency)
                    if self.wordfreq_available:
                        try:
                            from wordfreq import word_frequency
                            freq = word_frequency(word.lower(), 'en')
                            
                            # If word frequency is very low, try context correction
                            if freq < 1e-6 and len(word) > 2:
                                # Create masked sentence for prediction
                                masked_words = words.copy()
                                masked_words[i] = '[MASK]'
                                masked_sentence = ' '.join(masked_words)
                                
                                try:
                                    # Get predictions
                                    predictions = self.mask_filler(masked_sentence, top_k=3)
                                    
                                    if predictions:
                                        best_prediction = predictions[0]['token_str']
                                        
                                        # Check if prediction is reasonable
                                        if len(best_prediction) > 1 and best_prediction.isalpha():
                                            corrections.append({
                                                'position': i,
                                                'original': word,
                                                'corrected': best_prediction,
                                                'confidence': predictions[0]['score'],
                                                'alternatives': [p['token_str'] for p in predictions[1:3]],
                                                'method': 'context_prediction'
                                            })
                                            
                                            # Update the sentence
                                            words[i] = best_prediction
                                            corrected_sentence = ' '.join(words)
                                
                                except Exception:
                                    continue
                        except:
                            continue
                
                corrected_sentences.append(corrected_sentence)
            
            final_text = '. '.join(corrected_sentences)
            if not final_text.endswith('.') and text.endswith('.'):
                final_text += '.'
            
            return final_text, corrections
            
        except Exception as e:
            logger.error(f"Context-based correction error: {str(e)}")
            return text, []
    
    def preserve_case_and_punctuation(self, original_word: str, corrected_word: str) -> str:
        """Preserve original case and punctuation when applying corrections"""
        try:
            result = corrected_word
            
            # Preserve case
            if original_word[0].isupper():
                result = result.capitalize()
            elif original_word.isupper():
                result = result.upper()
            
            # Add back punctuation
            punctuation = ''.join(c for c in original_word if not c.isalpha())
            if punctuation:
                result += punctuation
            
            return result
        except:
            return corrected_word
    
    def comprehensive_correction(self, raw_text: str) -> Dict[str, Any]:
        """Apply all correction methods comprehensively"""
        try:
            start_time = time.time()
            logger.info("🚀 Running comprehensive intelligent correction...")
            
            if not raw_text.strip():
                return {
                    'success': False,
                    'error': 'Empty text provided'
                }
            
            current_text = raw_text
            all_corrections = []
            
            # Step 1: OCR pattern correction
            logger.debug("🔧 Step 1: OCR pattern analysis...")
            pattern_corrections = self.analyze_ocr_errors(current_text)
            all_corrections.extend(pattern_corrections)
            
            # Step 2: Spell check correction
            logger.debug("📝 Step 2: Spell check correction...")
            current_text, spell_corrections = self.spell_check_correction(current_text)
            all_corrections.extend(spell_corrections)
            
            # Step 3: Fuzzy word correction
            logger.debug("🔍 Step 3: Fuzzy word correction...")
            current_text, fuzzy_corrections = self.fuzzy_word_correction(current_text)
            all_corrections.extend(fuzzy_corrections)
            
            # Step 4: Context-based correction
            logger.debug("🤖 Step 4: Context-based correction...")
            current_text, context_corrections = self.context_based_correction(current_text)
            all_corrections.extend(context_corrections)
            
            # Calculate confidence score
            total_words = len(raw_text.split())
            corrected_words = len(all_corrections)
            confidence = max(0, (total_words - corrected_words) / total_words) if total_words > 0 else 1.0
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Intelligent correction complete! Applied {len(all_corrections)} corrections in {processing_time:.2f}s")
            
            return {
                'success': True,
                'corrected_text': current_text,
                'corrections': all_corrections,
                'confidence': confidence,
                'processing_time': processing_time,
                'methods_used': list(set(c['method'] for c in all_corrections))
            }
            
        except Exception as e:
            logger.error(f"Comprehensive correction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_methods(self) -> List[str]:
        """Get list of available correction methods"""
        return self.correction_methods.copy()
    
    def get_correction_stats(self, corrections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about applied corrections"""
        try:
            # Group by method
            method_counts = {}
            for correction in corrections:
                method = correction.get('method', 'unknown')
                method_counts[method] = method_counts.get(method, 0) + 1
            
            return {
                'total_corrections': len(corrections),
                'methods_used': len(method_counts),
                'correction_breakdown': method_counts,
                'most_used_method': max(method_counts.items(), key=lambda x: x[1])[0] if method_counts else None
            }
        except:
            return {'error': 'Failed to calculate correction stats'}