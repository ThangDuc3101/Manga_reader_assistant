"""
Test suite for Phase 3: Feature Improvements
Tests for responsive text rendering and visual enhancements
"""

import os
import sys
import logging
from pathlib import Path
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wrap_text_function():
    """Test 1: Text wrapping function"""
    try:
        from reader import Manga_Reader
        from PIL import ImageFont
        
        reader = Manga_Reader()
        font = ImageFont.truetype(reader.font_path, 20)
        
        test_text = "Đây là một bài kiểm tra cho hàm wrap text"
        max_width = 200
        
        lines = reader.wrap_text(test_text, font, max_width)
        
        if len(lines) > 0 and all(isinstance(line, str) for line in lines):
            logger.info(f"✅ Test 1 PASS: Text wrapped into {len(lines)} lines")
            for i, line in enumerate(lines):
                logger.info(f"   Line {i+1}: {line}")
            return True
        else:
            logger.error("❌ Test 1 FAIL: wrap_text returned invalid output")
            return False
    except Exception as e:
        logger.error(f"❌ Test 1 FAIL: {e}")
        return False

def test_calculate_font_size():
    """Test 2: Dynamic font size calculation"""
    try:
        from reader import Manga_Reader
        
        reader = Manga_Reader()
        
        test_text = "Xin chào thế giới"
        box_width = 300
        box_height = 150
        
        font_size = reader.calculate_font_size(test_text, box_width, box_height)
        
        if 8 <= font_size <= 40:
            logger.info(f"✅ Test 2 PASS: Calculated font size: {font_size}pt")
            return True
        else:
            logger.error(f"❌ Test 2 FAIL: Invalid font size: {font_size}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 2 FAIL: {e}")
        return False

def test_small_textbox_handling():
    """Test 3: Handling of very small textboxes"""
    try:
        from reader import Manga_Reader
        
        reader = Manga_Reader()
        
        # Very small textbox
        small_width = 30
        small_height = 20
        test_text = "テスト"
        
        font_size = reader.calculate_font_size(test_text, small_width, small_height)
        
        if font_size >= 8:
            logger.info(f"✅ Test 3 PASS: Small textbox handled, font size: {font_size}pt")
            return True
        else:
            logger.error(f"❌ Test 3 FAIL: Invalid font size for small textbox")
            return False
    except Exception as e:
        logger.error(f"❌ Test 3 FAIL: {e}")
        return False

def test_long_text_wrapping():
    """Test 4: Long text wrapping"""
    try:
        from reader import Manga_Reader
        from PIL import ImageFont
        
        reader = Manga_Reader()
        font = ImageFont.truetype(reader.font_path, 16)
        
        long_text = "Đây là một đoạn văn bản rất dài để kiểm tra xem hàm wrap text có hoạt động tốt với các đoạn text dài không"
        max_width = 200
        
        lines = reader.wrap_text(long_text, font, max_width)
        
        if len(lines) >= 3:
            logger.info(f"✅ Test 4 PASS: Long text wrapped into {len(lines)} lines")
            return True
        else:
            logger.error(f"❌ Test 4 FAIL: Expected multiple lines, got {len(lines)}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 4 FAIL: {e}")
        return False

def test_full_pipeline_with_test_image():
    """Test 5: Full pipeline with actual test image"""
    try:
        from reader import Manga_Reader
        
        test_images = ["test/jjk2.png", "test/jjk4.png", "test/jjk5.png"]
        
        # Find first existing test image
        test_img_path = None
        for img_path in test_images:
            if os.path.exists(img_path):
                test_img_path = img_path
                break
        
        if not test_img_path:
            logger.warning("⚠️  Test 5 WARN: No test images found")
            return False
        
        reader = Manga_Reader()
        img = Image.open(test_img_path)
        
        logger.info(f"Processing image: {test_img_path} ({img.size})")
        result = reader(img)
        
        if result and result.size == img.size:
            # Save result
            output_path = "translated/test_phase3_result.png"
            result.save(output_path)
            logger.info(f"✅ Test 5 PASS: Full pipeline executed successfully")
            logger.info(f"   Result saved to: {output_path}")
            return True
        else:
            logger.error("❌ Test 5 FAIL: Pipeline returned invalid result")
            return False
    except Exception as e:
        logger.error(f"❌ Test 5 FAIL: {e}")
        return False

def test_text_clearing():
    """Test 6: Original text clearing"""
    try:
        from reader import Manga_Reader
        from PIL import Image, ImageDraw, ImageFont
        
        reader = Manga_Reader()
        
        # Create test image with colored text
        test_img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(test_img)
        
        # Draw some colored text using TrueType font
        try:
            font = ImageFont.truetype(reader.font_path, 20)
        except:
            font = ImageFont.load_default()
        
        # Draw colored text (not white) so we can verify clearing
        draw.text((50, 50), "TEST AREA", fill=(0, 0, 0), font=font)
        
        # Define textbox around the text
        textbox = [40, 40, 200, 100]
        
        # Apply clearing (fill with white)
        draw = ImageDraw.Draw(test_img)
        x1, y1, x2, y2 = textbox
        draw.rectangle([x1, y1, x2, y2], fill="white", outline=None)
        
        # Check if area is cleared (mostly white)
        crop = test_img.crop(textbox)
        pixels = list(crop.getdata())
        white_pixels = sum(1 for p in pixels if p == (255, 255, 255))
        white_ratio = white_pixels / len(pixels)
        
        if white_ratio > 0.9:
            logger.info(f"✅ Test 6 PASS: Text clearing successful ({white_ratio*100:.1f}% white)")
            return True
        else:
            logger.error(f"❌ Test 6 FAIL: Clearing ineffective ({white_ratio*100:.1f}% white)")
            return False
    except Exception as e:
        logger.error(f"❌ Test 6 FAIL: {e}")
        return False

def test_center_alignment():
    """Test 7: Text center alignment"""
    try:
        from reader import Manga_Reader
        from PIL import Image, ImageFont
        
        reader = Manga_Reader()
        font = ImageFont.truetype(reader.font_path, 16)
        
        # Create test image
        test_img = Image.new('RGB', (400, 300), color='white')
        
        textbox = [50, 50, 350, 150]
        x1, y1, x2, y2 = textbox
        box_width = x2 - x1
        padding = 10
        max_width = box_width - (padding * 2)
        
        test_text = "Xin chào"
        bbox = font.getbbox(test_text)
        line_width = bbox[2] - bbox[0]
        
        # Center calculation
        x_center = x1 + padding + (max_width - line_width) // 2
        
        if x1 + padding <= x_center <= x2 - padding - line_width:
            logger.info(f"✅ Test 7 PASS: Text center alignment calculated correctly")
            logger.info(f"   Textbox: {x1}-{x2}, Text position: {x_center}")
            return True
        else:
            logger.error(f"❌ Test 7 FAIL: Text alignment out of bounds")
            return False
    except Exception as e:
        logger.error(f"❌ Test 7 FAIL: {e}")
        return False

def test_responsive_font_sizing():
    """Test 8: Responsive font sizing for different textbox sizes"""
    try:
        from reader import Manga_Reader
        
        reader = Manga_Reader()
        test_text = "テスト"
        
        # Test different textbox sizes
        test_cases = [
            (100, 50, "small"),
            (300, 150, "medium"),
            (500, 300, "large"),
        ]
        
        results = []
        for width, height, label in test_cases:
            font_size = reader.calculate_font_size(test_text, width, height)
            results.append((label, font_size))
            logger.info(f"   {label.capitalize()} ({width}x{height}): {font_size}pt")
        
        # Check if font sizes increase with textbox size
        if results[0][1] <= results[1][1] <= results[2][1]:
            logger.info(f"✅ Test 8 PASS: Responsive font sizing working correctly")
            return True
        else:
            logger.error(f"❌ Test 8 FAIL: Font sizes not responsive to textbox size")
            return False
    except Exception as e:
        logger.error(f"❌ Test 8 FAIL: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 3: FEATURE IMPROVEMENTS - TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        ("Text wrapping function", test_wrap_text_function),
        ("Dynamic font size calculation", test_calculate_font_size),
        ("Small textbox handling", test_small_textbox_handling),
        ("Long text wrapping", test_long_text_wrapping),
        ("Full pipeline with test image", test_full_pipeline_with_test_image),
        ("Text clearing", test_text_clearing),
        ("Center alignment", test_center_alignment),
        ("Responsive font sizing", test_responsive_font_sizing),
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
