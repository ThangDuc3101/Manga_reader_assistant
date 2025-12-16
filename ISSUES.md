# 🐛 ISSUES - Manga Reader Assistant

> Tổng hợp các vấn đề cần khắc phục trong project

---

## 📊 Tổng quan

| # | Issue | Mức độ | Trạng thái |
|---|-------|--------|------------|
| 1 | Mất file weights YOLOv8 | 🔴 Critical | ⏳ Pending |
| 2 | Font path không chính xác | 🔴 Critical | ⏳ Pending |
| 3 | Thư mục `translated/` không tồn tại | 🟠 High | ⏳ Pending |
| 4 | `googletrans` không ổn định | 🟠 High | ⏳ Pending |
| 5 | Không có Error Handling | 🟠 High | ⏳ Pending |
| 6 | Text rendering cố định, không responsive | 🟡 Medium | ⏳ Pending |
| 7 | Không xóa text gốc trước khi render | 🟡 Medium | ⏳ Pending |
| 8 | Model load mỗi lần upload ảnh | 🟡 Medium | ⏳ Pending |
| 9 | Thiếu file `.gitignore` | 🟢 Low | ⏳ Pending |
| 10 | Code structure chưa tối ưu | 🟢 Low | ⏳ Pending |

---

## 🔴 CRITICAL ISSUES

### Issue #1: Mất file weights YOLOv8
**File:** `reader.py` (line 7-8)

**Mô tả:**
- File `yolov8_manga.pt` đã bị mất
- Link Google Drive cũng đã bị xóa
- Không thể chạy ứng dụng nếu thiếu file này

**Code hiện tại:**
```python
def __init__(self, detector="yolov8_manga.pt"):
    self.model = YOLO(f"{detector}")
```

**Giải pháp đề xuất:**
1. **Option A - Train lại model:** Sử dụng dataset manga speech bubble để train lại YOLOv8
2. **Option B - Sử dụng Roboflow:** Tìm model pre-trained trên Roboflow Universe cho manga/comic text detection
3. **Option C - Sử dụng model thay thế:** Dùng các model detection khác như:
   - `yolov8n.pt` (pretrained) + fine-tune
   - Craft text detection
   - PaddleOCR detection

**Ưu tiên:** ⭐⭐⭐⭐⭐ (Bắt buộc phải sửa đầu tiên)

---

### Issue #2: Font path không chính xác
**File:** `reader.py` (line 48)

**Mô tả:**
- Code sử dụng `"arial.ttf"` nhưng font nằm trong thư mục `font/arial.ttf`
- Sẽ gây lỗi `OSError: cannot open resource` trên hầu hết hệ thống

**Code hiện tại:**
```python
font = ImageFont.truetype("arial.ttf", 40)
```

**Giải pháp đề xuất:**
```python
import os
font_path = os.path.join(os.path.dirname(__file__), "font", "arial.ttf")
font = ImageFont.truetype(font_path, 40)
```

**Ưu tiên:** ⭐⭐⭐⭐⭐

---

## 🟠 HIGH PRIORITY ISSUES

### Issue #3: Thư mục `translated/` không tồn tại
**File:** `assistant.py` (line 29)

**Mô tả:**
- Code lưu ảnh vào thư mục `translated/` nhưng thư mục này không tồn tại
- Gây lỗi `FileNotFoundError`

**Code hiện tại:**
```python
imageTrans.save(os.path.join('translated', image_name))
```

**Giải pháp đề xuất:**
```python
output_dir = 'translated'
os.makedirs(output_dir, exist_ok=True)
imageTrans.save(os.path.join(output_dir, image_name))
```

**Ưu tiên:** ⭐⭐⭐⭐

---

### Issue #4: `googletrans` không ổn định
**File:** `reader.py` (line 2, 11, 45)

**Mô tả:**
- `googletrans==3.1.0a0` là bản alpha, không ổn định
- Thường xuyên gặp lỗi `AttributeError: 'NoneType' object has no attribute 'group'`
- Google có thể block IP nếu request quá nhiều

**Giải pháp đề xuất:**
1. **Option A:** Sử dụng `deep-translator` thay thế
   ```python
   from deep_translator import GoogleTranslator
   translator = GoogleTranslator(source='ja', target='vi')
   translated = translator.translate(text)
   ```

2. **Option B:** Sử dụng Google Cloud Translation API (có phí)

3. **Option C:** Thêm retry mechanism và error handling
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
   def translate_text(self, text):
       return self.translator.translate(text, src="ja", dest="vi")
   ```

**Ưu tiên:** ⭐⭐⭐⭐

---

### Issue #5: Không có Error Handling
**File:** Toàn bộ project

**Mô tả:**
- Không có try-except cho các thao tác có thể fail
- App crash khi gặp lỗi thay vì hiển thị thông báo thân thiện

**Các điểm cần thêm error handling:**
- Load model YOLO
- OCR recognition
- Translation API call
- File I/O operations

**Giải pháp đề xuất:**
```python
def __call__(self, img):
    try:
        textboxes = self.detect(img)
        for textbox in textboxes:
            try:
                bubble_chat = img.crop((textbox[0], textbox[1], textbox[2], textbox[3]))
                text = self.recognizer(bubble_chat)
                img = self.process_chat(text, textbox, img)
            except Exception as e:
                print(f"Error processing textbox: {e}")
                continue
        return img
    except Exception as e:
        print(f"Detection error: {e}")
        return img
```

**Ưu tiên:** ⭐⭐⭐⭐

---

## 🟡 MEDIUM PRIORITY ISSUES

### Issue #6: Text rendering cố định, không responsive
**File:** `reader.py` (line 48, 60-61)

**Mô tả:**
- Font size cố định 40px
- Text có thể tràn ra ngoài bubble
- Không tự động điều chỉnh theo kích thước bubble

**Code hiện tại:**
```python
font = ImageFont.truetype("arial.ttf", 40)
# ...
draw.text((posText[0], posText[1]+i*40), content[i], (255,0,0), font=font)
```

**Giải pháp đề xuất:**
```python
def calculate_font_size(self, text, box_width, box_height, max_font_size=40):
    """Tính font size phù hợp với kích thước bubble"""
    font_size = max_font_size
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(text)
        if bbox[2] <= box_width * 0.9:
            return font_size
        font_size -= 2
    return 10
```

**Ưu tiên:** ⭐⭐⭐

---

### Issue #7: Không xóa text gốc trước khi render
**File:** `reader.py`

**Mô tả:**
- Text tiếng Việt được vẽ đè lên text tiếng Nhật
- Gây khó đọc và rối mắt

**Giải pháp đề xuất:**
```python
def process_chat(self, text, posText, img):
    # Xóa vùng text gốc bằng cách fill màu trắng
    draw = ImageDraw.Draw(img)
    box_width = posText[2] - posText[0]
    box_height = posText[3] - posText[1]
    draw.rectangle([posText[0], posText[1], posText[2], posText[3]], fill="white")
    
    # Sau đó mới vẽ text mới
    # ...
```

**Ưu tiên:** ⭐⭐⭐

---

### Issue #8: Model load mỗi lần upload ảnh
**File:** `assistant.py` (line 16)

**Mô tả:**
- `Manga_Reader()` được khởi tạo mỗi lần vào tab Assistant
- Load model YOLO và Manga-OCR rất tốn thời gian và RAM

**Code hiện tại:**
```python
def app():
    # ...
    reader = Manga_Reader()  # Load mỗi lần
```

**Giải pháp đề xuất:**
Sử dụng `st.cache_resource` của Streamlit:
```python
@st.cache_resource
def load_reader():
    return Manga_Reader()

def app():
    reader = load_reader()  # Cache và reuse
```

**Ưu tiên:** ⭐⭐⭐

---

## 🟢 LOW PRIORITY ISSUES

### Issue #9: Thiếu file `.gitignore`
**Mô tả:**
- Không có `.gitignore` để loại trừ các file không cần thiết
- Có thể commit nhầm `__pycache__`, `.pt` files, v.v.

**Giải pháp đề xuất:**
Tạo file `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*.pyo
.Python
env/
venv/

# Model weights
*.pt
*.pth

# IDE
.vscode/
.idea/

# Output
translated/

# Environment
.env
```

**Ưu tiên:** ⭐⭐

---

### Issue #10: Code structure chưa tối ưu
**File:** `main.py`

**Mô tả:**
- Class `Manga_Reader_App` được định nghĩa nhưng không sử dụng đúng cách
- Method `run()` không có `self` parameter
- Cấu trúc class không cần thiết

**Code hiện tại:**
```python
class Manga_Reader_App:
    def __init__(self) -> None:
        self.app = []
    def add_app(self, title, func):
        # Không được sử dụng
        ...
    def run():  # Thiếu self
        ...
    run()  # Gọi trong class definition
```

**Giải pháp đề xuất:**
Đơn giản hóa thành functions:
```python
import streamlit as st
from streamlit_option_menu import option_menu
import about, assistant, readOnly

def main():
    with st.sidebar:
        app = option_menu(
            menu_title="Main Menu",
            options=["Assistant", "Read Only", "About"],
            icons=["chat-text", "book", "info-circle-fill"],
            menu_icon="bounding-box",
            default_index=0
        )
    
    if app == "Assistant":
        assistant.app()
    elif app == "Read Only":
        readOnly.app()
    elif app == "About":
        about.app()

if __name__ == "__main__":
    main()
```

**Ưu tiên:** ⭐⭐

---

## 📋 THỨ TỰ XỬ LÝ ĐỀ XUẤT

### Phase 1: Critical Fixes (Bắt buộc để app chạy được)
1. ✅ **Issue #1** - Giải quyết vấn đề model weights
2. ✅ **Issue #2** - Sửa font path
3. ✅ **Issue #3** - Tạo thư mục translated

### Phase 2: Stability Improvements (Ổn định app)
4. ✅ **Issue #4** - Thay thế/fix googletrans
5. ✅ **Issue #5** - Thêm error handling

### Phase 3: Feature Improvements (Cải thiện chất lượng)
6. ✅ **Issue #6** - Responsive text rendering
7. ✅ **Issue #7** - Xóa text gốc trước khi render

### Phase 4: Optimization (Tối ưu)
8. ✅ **Issue #8** - Cache model loading
9. ✅ **Issue #9** - Thêm .gitignore
10. ✅ **Issue #10** - Refactor code structure

---

## 🔗 Tài nguyên hữu ích

### Thay thế model detection:
- [Roboflow Universe - Comic/Manga Detection](https://universe.roboflow.com/search?q=manga%20text)
- [Craft Text Detector](https://github.com/clovaai/CRAFT-pytorch)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

### Thay thế Translation:
- [deep-translator](https://github.com/nidhaloff/deep-translator)
- [Google Cloud Translation](https://cloud.google.com/translate)

---

*Cập nhật lần cuối: December 2024*
