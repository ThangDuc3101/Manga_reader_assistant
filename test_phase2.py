"""
Test suite for Phase 2: Stability Improvements
Tests for deep-translator integration and error handling
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deep_translator_import():
    """Test 1: deep-translator library import"""
    try:
        from deep_translator import GoogleTranslator
        logger.info("✅ Test 1 PASS: deep-translator imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Test 1 FAIL: Cannot import deep-translator: {e}")
        return False

def test_tenacity_import():
    """Test 2: tenacity library import"""
    try:
        from tenacity import retry, stop_after_attempt, wait_exponential
        logger.info("✅ Test 2 PASS: tenacity imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Test 2 FAIL: Cannot import tenacity: {e}")
        return False

def test_translator_initialization():
    """Test 3: Google Translator initialization"""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='ja', target='vi')
        logger.info("✅ Test 3 PASS: GoogleTranslator initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Test 3 FAIL: Cannot initialize GoogleTranslator: {e}")
        return False

def test_translation_basic():
    """Test 4: Basic translation Japanese -> Vietnamese"""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='ja', target='vi')
        
        # Test with simple Japanese text
        test_text = "こんにちは"  # "Hello" in Japanese
        result = translator.translate(test_text)
        
        if result and len(result) > 0:
            logger.info(f"✅ Test 4 PASS: Translation successful")
            logger.info(f"   Input: {test_text} -> Output: {result}")
            return True
        else:
            logger.error("❌ Test 4 FAIL: Translation returned empty result")
            return False
    except Exception as e:
        logger.error(f"❌ Test 4 FAIL: Translation error: {e}")
        return False

def test_error_handling_in_reader():
    """Test 5: Error handling in reader.py"""
    try:
        from reader import Manga_Reader
        
        # Should initialize without errors
        reader = Manga_Reader()
        logger.info("✅ Test 5 PASS: Manga_Reader initialized with error handling")
        return True
    except Exception as e:
        logger.error(f"❌ Test 5 FAIL: Manga_Reader initialization error: {e}")
        return False

def test_font_path_handling():
    """Test 6: Font path handling"""
    try:
        import os
        from pathlib import Path
        
        font_path = os.path.join(os.path.dirname(__file__), "font", "arial.ttf")
        
        if os.path.exists(font_path):
            logger.info(f"✅ Test 6 PASS: Font file found at {font_path}")
            return True
        else:
            logger.warning(f"⚠️  Test 6 WARN: Font file not found at {font_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 6 FAIL: Font path handling error: {e}")
        return False

def test_translated_directory():
    """Test 7: Translated directory creation"""
    try:
        import os
        
        translated_dir = "translated"
        os.makedirs(translated_dir, exist_ok=True)
        
        if os.path.exists(translated_dir):
            logger.info(f"✅ Test 7 PASS: 'translated' directory exists")
            return True
        else:
            logger.error(f"❌ Test 7 FAIL: Cannot create 'translated' directory")
            return False
    except Exception as e:
        logger.error(f"❌ Test 7 FAIL: Directory creation error: {e}")
        return False

def test_env_file():
    """Test 8: .env file and API key"""
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        api_key = os.getenv("ROBOFLOW_API_KEY", "")
        
        if api_key:
            logger.info("✅ Test 8 PASS: ROBOFLOW_API_KEY found in .env")
            return True
        else:
            logger.warning("⚠️  Test 8 WARN: ROBOFLOW_API_KEY not found in .env")
            return False
    except Exception as e:
        logger.error(f"❌ Test 8 FAIL: .env loading error: {e}")
        return False

def test_logging_setup():
    """Test 9: Logging configuration"""
    try:
        import logging
        
        logger_test = logging.getLogger("test")
        handler = logging.StreamHandler()
        logger_test.addHandler(handler)
        logger_test.setLevel(logging.INFO)
        
        logger.info("✅ Test 9 PASS: Logging configured successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Test 9 FAIL: Logging setup error: {e}")
        return False

def test_ocr_with_test_image():
    """Test 10: OCR with actual test image"""
    try:
        from PIL import Image
        from manga_ocr import MangaOcr
        
        test_images = [
            "test/jjk2.png",
            "test/jjk4.png",
            "test/jjk5.png"
        ]
        
        # Find first existing test image
        test_img_path = None
        for img_path in test_images:
            if os.path.exists(img_path):
                test_img_path = img_path
                break
        
        if not test_img_path:
            logger.warning("⚠️  Test 10 WARN: No test images found")
            return False
        
        # Initialize OCR
        ocr = MangaOcr()
        
        # Open and process image
        image = Image.open(test_img_path)
        
        # Crop a small region for quick test
        cropped = image.crop((50, 50, 150, 150))
        result = ocr(cropped)
        
        logger.info(f"✅ Test 10 PASS: OCR executed on test image")
        logger.info(f"   Test image: {test_img_path}")
        logger.info(f"   OCR result: {result}")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Test 10 WARN: OCR test error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 2: STABILITY IMPROVEMENTS - TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        ("Deep-translator import", test_deep_translator_import),
        ("Tenacity import", test_tenacity_import),
        ("Translator initialization", test_translator_initialization),
        ("Basic translation", test_translation_basic),
        ("Error handling in reader", test_error_handling_in_reader),
        ("Font path handling", test_font_path_handling),
        ("Translated directory", test_translated_directory),
        (".env file setup", test_env_file),
        ("Logging configuration", test_logging_setup),
        ("OCR with test image", test_ocr_with_test_image),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n▶ {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
