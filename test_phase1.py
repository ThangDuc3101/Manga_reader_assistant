"""
Test script for Phase 1 fixes
Run: python test_phase1.py
"""

import os
import sys

def test_env_file():
    """Test #1: Check .env file and ROBOFLOW_API_KEY"""
    print("=" * 50)
    print("TEST 1: Check .env file")
    print("=" * 50)
    
    if os.path.exists(".env"):
        print("[OK] File .env exists")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ROBOFLOW_API_KEY", "")
        if api_key and api_key != "your_api_key_here":
            print(f"[OK] ROBOFLOW_API_KEY is set (length: {len(api_key)})")
            return True
        else:
            print("[FAIL] ROBOFLOW_API_KEY not set or using default value")
            print("   -> Create .env file with:")
            print("   ROBOFLOW_API_KEY=your_actual_api_key")
            return False
    else:
        print("[FAIL] File .env does not exist")
        print("   -> Copy .env.example to .env and add API key")
        return False


def test_font_path():
    """Test #2: Check font path"""
    print("\n" + "=" * 50)
    print("TEST 2: Check font path")
    print("=" * 50)
    
    font_path = os.path.join(os.path.dirname(__file__), "font", "arial.ttf")
    
    if os.path.exists(font_path):
        print(f"[OK] Font file exists: {font_path}")
        
        # Test load font
        try:
            from PIL import ImageFont
            font = ImageFont.truetype(font_path, 40)
            print("[OK] Font loaded successfully")
            return True
        except Exception as e:
            print(f"[FAIL] Error loading font: {e}")
            return False
    else:
        print(f"[FAIL] Font file not found: {font_path}")
        return False


def test_translated_folder():
    """Test #3: Check translated folder"""
    print("\n" + "=" * 50)
    print("TEST 3: Check translated folder")
    print("=" * 50)
    
    translated_dir = "translated"
    os.makedirs(translated_dir, exist_ok=True)
    
    if os.path.exists(translated_dir) and os.path.isdir(translated_dir):
        print(f"[OK] Folder '{translated_dir}' exists")
        
        # Test write permission
        test_file = os.path.join(translated_dir, "test_write.txt")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("[OK] Write permission granted")
            return True
        except Exception as e:
            print(f"[FAIL] No write permission: {e}")
            return False
    else:
        print(f"[FAIL] Folder '{translated_dir}' does not exist")
        return False


def test_roboflow_connection():
    """Test Roboflow API connection"""
    print("\n" + "=" * 50)
    print("TEST 4: Check Roboflow API connection")
    print("=" * 50)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ROBOFLOW_API_KEY", "")
        if not api_key or api_key == "your_api_key_here":
            print("[SKIP] ROBOFLOW_API_KEY not set")
            return None
        
        import requests
        print("   Connecting to Roboflow API...")
        
        # Test API connection
        api_url = "https://detect.roboflow.com/manga-bubble-pqdou/1"
        response = requests.get(api_url, params={"api_key": api_key})
        
        if response.status_code == 400:  # Expected when no image provided
            print("[OK] Roboflow API connection successful")
            print(f"   Model: maana/manga-bubble-pqdou/1")
            return True
        elif response.status_code == 401:
            print(f"[FAIL] Invalid API key")
            return False
        else:
            print(f"[OK] Roboflow API responded with status: {response.status_code}")
            return True
        
    except Exception as e:
        print(f"[FAIL] Roboflow connection error: {e}")
        return False


def test_full_pipeline():
    """Test full pipeline with sample image"""
    print("\n" + "=" * 50)
    print("TEST 5: Test full pipeline (Detection + OCR)")
    print("=" * 50)
    
    # Check test images
    test_images = ["test/jjk2.png", "test/jjk4.png", "test/jjk5.png"]
    available_image = None
    
    for img_path in test_images:
        if os.path.exists(img_path):
            available_image = img_path
            break
    
    if not available_image:
        print("[SKIP] No test images found in test/ folder")
        return None
    
    print(f"   Using image: {available_image}")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ROBOFLOW_API_KEY", "")
        if not api_key or api_key == "your_api_key_here":
            print("[SKIP] ROBOFLOW_API_KEY not set")
            return None
        
        from PIL import Image
        from reader import Manga_Reader
        
        print("   Initializing Manga_Reader...")
        reader = Manga_Reader(use_roboflow=True)
        
        print("   Loading image...")
        img = Image.open(available_image)
        
        print("   Detecting textboxes...")
        textboxes = reader.detect(img)
        print(f"   -> Found {len(textboxes)} textbox(es)")
        
        if len(textboxes) > 0:
            print("[OK] Detection working!")
            
            # Test OCR on first textbox
            print("   Testing OCR...")
            bubble = img.crop((textboxes[0][0], textboxes[0][1], textboxes[0][2], textboxes[0][3]))
            text = reader.recognizer(bubble)
            # Avoid encoding issues with Japanese text in console
            print(f"   -> OCR result: [Japanese text detected, length={len(text)}]")
            print("[OK] OCR working!")
            
            return True
        else:
            print("[WARN] No textbox detected (may be due to test image)")
            return True
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 50)
    print("   PHASE 1 TEST SUITE")
    print("=" * 50 + "\n")
    
    results = {}
    
    # Run tests
    results["env_file"] = test_env_file()
    results["font_path"] = test_font_path()
    results["translated_folder"] = test_translated_folder()
    results["roboflow_connection"] = test_roboflow_connection()
    results["full_pipeline"] = test_full_pipeline()
    
    # Summary
    print("\n" + "=" * 50)
    print("[SUMMARY] TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in results.items():
        if result is True:
            status = "[PASS]"
        elif result is False:
            status = "[FAIL]"
        else:
            status = "[SKIP]"
        print(f"   {test_name}: {status}")
    
    # Check if critical tests passed
    critical_passed = results["font_path"] and results["translated_folder"]
    
    print("\n" + "=" * 50)
    if critical_passed:
        if results["env_file"]:
            print("[SUCCESS] Phase 1 ready to test with Streamlit!")
            print("   Run: streamlit run main.py")
        else:
            print("[WARNING] Need to setup .env file before running app")
            print("   1. Copy .env.example to .env")
            print("   2. Get API key from https://app.roboflow.com/settings/api")
            print("   3. Add API key to .env file")
    else:
        print("[ERROR] There are errors that need to be fixed")
    print("=" * 50)


if __name__ == "__main__":
    main()
