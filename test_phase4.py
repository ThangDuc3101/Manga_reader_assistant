"""
Test suite for Phase 4: Polish & Optional Enhancements
Tests for multi-language support, batch processing, and UI improvements
"""

import os
import sys
import logging
from pathlib import Path
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_language_support():
    """Test 1: Multi-language support initialization"""
    try:
        from reader import Manga_Reader, SUPPORTED_LANGUAGES
        
        # Test Vietnamese (default)
        reader_vi = Manga_Reader(target_language='vi')
        assert reader_vi.target_language == 'vi'
        logger.info("✅ Test 1 PASS: Vietnamese language initialized")
        
        # Test changing language
        if 'en' in SUPPORTED_LANGUAGES:
            success = reader_vi.set_target_language('en')
            assert success and reader_vi.target_language == 'en'
            logger.info("✅ Test 1 PASS: Language switching works")
            return True
        return True
    except Exception as e:
        logger.error(f"❌ Test 1 FAIL: {e}")
        return False

def test_all_supported_languages():
    """Test 2: All supported languages are valid"""
    try:
        from reader import SUPPORTED_LANGUAGES
        
        required_languages = {
            'vi': 'Vietnamese',
            'en': 'English',
            'zh-CN': 'Chinese (Simplified)',
            'ko': 'Korean',
            'th': 'Thai',
        }
        
        for code, name in required_languages.items():
            assert code in SUPPORTED_LANGUAGES, f"Missing language: {code}"
            assert SUPPORTED_LANGUAGES[code] == name, f"Wrong name for {code}"
        
        logger.info(f"✅ Test 2 PASS: All {len(SUPPORTED_LANGUAGES)} supported languages verified")
        return True
    except Exception as e:
        logger.error(f"❌ Test 2 FAIL: {e}")
        return False

def test_processing_statistics():
    """Test 3: Processing statistics tracking"""
    try:
        from reader import Manga_Reader
        
        reader = Manga_Reader()
        
        # Check initial stats
        stats = reader.get_stats()
        assert stats['total_images'] == 0
        assert stats['processed_images'] == 0
        assert stats['total_textboxes'] == 0
        assert stats['total_time'] == 0
        
        logger.info("✅ Test 3 PASS: Stats initialization correct")
        
        # Check reset
        reader.reset_stats()
        stats = reader.get_stats()
        assert stats['total_images'] == 0
        
        logger.info("✅ Test 3 PASS: Stats reset works")
        return True
    except Exception as e:
        logger.error(f"❌ Test 3 FAIL: {e}")
        return False

def test_batch_processing():
    """Test 4: Batch processing with stats"""
    try:
        from reader import Manga_Reader
        
        test_images = ["test/jjk2.png", "test/jjk4.png"]
        
        # Find existing test images
        available_images = [img for img in test_images if os.path.exists(img)]
        
        if not available_images:
            logger.warning("⚠️  Test 4 WARN: No test images available")
            return False
        
        reader = Manga_Reader()
        reader.reset_stats()
        
        # Process each image
        for img_path in available_images:
            image = Image.open(img_path)
            result = reader(image)
            assert result is not None
        
        # Check stats were updated
        stats = reader.get_stats()
        assert stats['total_images'] == len(available_images)
        assert stats['processed_images'] == len(available_images)
        assert stats['total_time'] > 0
        
        logger.info(f"✅ Test 4 PASS: Batch processed {len(available_images)} images")
        logger.info(f"   Total time: {stats['total_time']:.2f}s")
        logger.info(f"   Total textboxes: {stats['total_textboxes']}")
        return True
    except Exception as e:
        logger.error(f"❌ Test 4 FAIL: {e}")
        return False

def test_language_switching():
    """Test 5: Language switching during execution"""
    try:
        from reader import Manga_Reader
        
        reader = Manga_Reader(target_language='vi')
        assert reader.target_language == 'vi'
        
        # Switch to English
        success = reader.set_target_language('en')
        assert success
        assert reader.target_language == 'en'
        
        # Switch back to Vietnamese
        success = reader.set_target_language('vi')
        assert success
        assert reader.target_language == 'vi'
        
        logger.info("✅ Test 5 PASS: Language switching works correctly")
        return True
    except Exception as e:
        logger.error(f"❌ Test 5 FAIL: {e}")
        return False

def test_invalid_language_handling():
    """Test 6: Invalid language code handling"""
    try:
        from reader import Manga_Reader
        
        reader = Manga_Reader()
        
        # Try to set invalid language (should fallback to vi)
        success = reader.set_target_language('invalid')
        assert success
        assert reader.target_language == 'vi'
        
        logger.info("✅ Test 6 PASS: Invalid language code handled gracefully")
        return True
    except Exception as e:
        logger.error(f"❌ Test 6 FAIL: {e}")
        return False

def test_statistics_accuracy():
    """Test 7: Statistics accuracy after processing"""
    try:
        from reader import Manga_Reader
        
        test_images = ["test/jjk2.png"]
        
        if not os.path.exists(test_images[0]):
            logger.warning("⚠️  Test 7 WARN: Test image not available")
            return False
        
        reader = Manga_Reader()
        reader.reset_stats()
        
        image = Image.open(test_images[0])
        result = reader(image)
        
        stats = reader.get_stats()
        
        # Verify stats
        assert stats['total_images'] == 1
        assert stats['processed_images'] == 1
        assert stats['total_textboxes'] > 0  # Should detect some textboxes
        assert stats['total_time'] > 0
        
        logger.info("✅ Test 7 PASS: Statistics accurate")
        logger.info(f"   Textboxes detected: {stats['total_textboxes']}")
        logger.info(f"   Processing time: {stats['total_time']:.3f}s")
        return True
    except Exception as e:
        logger.error(f"❌ Test 7 FAIL: {e}")
        return False

def test_multiple_languages():
    """Test 8: Processing with multiple languages"""
    try:
        from reader import Manga_Reader, SUPPORTED_LANGUAGES
        
        test_languages = ['vi', 'en', 'zh-CN']
        
        for lang in test_languages:
            if lang not in SUPPORTED_LANGUAGES:
                continue
            
            reader = Manga_Reader(target_language=lang)
            assert reader.target_language == lang
            logger.info(f"   ✓ {lang} ({SUPPORTED_LANGUAGES[lang]})")
        
        logger.info("✅ Test 8 PASS: Multiple language support verified")
        return True
    except Exception as e:
        logger.error(f"❌ Test 8 FAIL: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 4: POLISH & ENHANCEMENTS - TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        ("Language support initialization", test_language_support),
        ("All supported languages", test_all_supported_languages),
        ("Processing statistics tracking", test_processing_statistics),
        ("Batch processing", test_batch_processing),
        ("Language switching", test_language_switching),
        ("Invalid language handling", test_invalid_language_handling),
        ("Statistics accuracy", test_statistics_accuracy),
        ("Multiple languages", test_multiple_languages),
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
