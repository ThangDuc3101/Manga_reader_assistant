# Manga Reader Assistant

> **Ứng dụng đọc và dịch Manga tiếng Nhật sang tiếng Việt (hoặc 12+ ngôn ngữ khác) tự động**

## 📖 Giới thiệu

**Manga Reader Assistant** là một ứng dụng sử dụng Computer Vision và AI để tự động phát hiện, nhận dạng và dịch văn bản trong manga tiếng Nhật sang tiếng Việt hoặc các ngôn ngữ khác.

- **Author:** ThangBui
- **Major:** Computer Vision & AI
- **Affiliation:** MTA (Military Technical Academy)
- **Status:** ✅ Production Ready (4 Phases Complete)

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Web UI                       │
│                        (main.py)                            │
├─────────────┬─────────────────────┬─────────────────────────┤
│  Assistant  │     Read Only       │         About           │
│(assistant.py│   (readOnly.py)     │       (about.py)        │
├─────────────┴─────────────────────┴─────────────────────────┤
│                     Manga Reader Core                       │
│                       (reader.py)                           │
├─────────────┬─────────────────────┬─────────────────────────┤
│  Roboflow   │     Manga-OCR       │  Deep-Translator API    │
│  REST API   │   Text Recognition  │      Translation        │
└─────────────┴─────────────────────┴─────────────────────────┘
```

---

## 🔧 Các thành phần chính

### 1. **Detection - Phát hiện vùng text (Roboflow REST API)**
- Sử dụng model `manga-bubble-pqdou` từ Roboflow Universe
- REST API integration (không cần tải model weights cục bộ)
- Tự động phát hiện các textbox/speech bubble trong manga
- Confidence threshold có thể điều chỉnh

### 2. **OCR - Nhận dạng văn bản (Manga-OCR)**
- Sử dụng thư viện [manga-ocr](https://github.com/kha-white/manga-ocr)
- Chuyên biệt cho việc nhận dạng chữ Nhật trong manga
- Tự động cache model để tối ưu performance

### 3. **Translation - Dịch thuật (Deep-Translator)**
- Sử dụng `deep-translator` (thay thế `googletrans` không ổn định)
- Hỗ trợ **12+ ngôn ngữ** (không chỉ Tiếng Việt)
- Retry mechanism với exponential backoff
- Tối đa 3 lần retry khi API gặp lỗi

### 4. **Text Rendering - Vẽ text lên ảnh**
- **Dynamic font sizing**: Tự động điều chỉnh kích thước chữ theo bubble size
- **Text wrapping**: Tự động xuống dòng phù hợp với chiều rộng bubble
- **Text clearing**: Xóa sạch text gốc (Nhật) trước khi vẽ text mới (Việt)
- **Centering**: Text được căn giữa theo chiều dọc & ngang
- **No overflow**: Đảm bảo text không tràn ra ngoài bubble

### 5. **Web UI (Streamlit)**
- Giao diện web thân thiện với 3 tabs:
  - **Assistant:** Upload và dịch manga với language selector
  - **Read Only:** Xem lại manga đã dịch từ folder
  - **About:** Thông tin về project
- **Sidebar features:**
  - ⚙️ Language selection (12+ languages)
  - 📤 Upload ảnh
  - 📊 Processing statistics (images, textboxes, time)
  - Progress bar cho batch processing

---

## 🌐 Ngôn ngữ được hỗ trợ

| Code | Ngôn ngữ |
|------|----------|
| `vi` | Vietnamese (Tiếng Việt) |
| `en` | English |
| `zh-CN` | Chinese Simplified |
| `zh-TW` | Chinese Traditional |
| `ko` | Korean |
| `th` | Thai |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `pt` | Portuguese |
| `it` | Italian |
| `ru` | Russian |

---

## 📁 Cấu trúc thư mục

```
Manga_reader_assistant/
├── main.py              # Entry point - Streamlit app
├── reader.py            # Core Manga Reader class
├── assistant.py         # Tab Assistant - Upload & dịch manga
├── readOnly.py          # Tab Read Only - Xem manga đã dịch
├── about.py             # Tab About - Thông tin project
├── requirements.txt     # Dependencies
├── .env.example         # Template cho API key
├── .gitignore           # Git ignore patterns
├── font/
│   └── arial.ttf        # Font để render text
├── img/
│   ├── demo.png         # Screenshot demo
│   ├── pruning_model.png
│   ├── results.png
│   ├── results2.png
│   └── results3.png
├── test/                # Ảnh test mẫu (Jujutsu Kaisen)
│   ├── jjk2.png
│   ├── jjk4.png
│   └── jjk5.png
├── translated/          # Thư mục lưu ảnh đã dịch (auto-create)
└── test_phaseX.py       # Các test files
```

---

## 🚀 Cài đặt

### Yêu cầu
- Python >= 3.10
- Anaconda (khuyến nghị)
- API key từ Roboflow (miễn phí)

### Bước 1: Clone repository
```bash
git clone https://github.com/ThangDuc3101/Manga_reader_assistant.git
cd Manga_reader_assistant
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)
```bash
conda create -n manga-reader python=3.10
conda activate manga-reader
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Setup API key
1. Copy `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```

2. Tạo API key từ Roboflow:
   - Truy cập https://app.roboflow.com/settings/api
   - Copy API key

3. Thêm API key vào `.env`:
   ```
   ROBOFLOW_API_KEY=your_api_key_here
   ```

### Bước 5: Chạy ứng dụng
```bash
streamlit run main.py
```

Ứng dụng sẽ mở tại `http://localhost:8501`

---

## 📦 Dependencies

| Package | Phiên bản | Mô tả |
|---------|-----------|-------|
| `streamlit` | Latest | Web UI framework |
| `streamlit_option_menu` | Latest | Sidebar menu component |
| `deep-translator` | Latest | Dịch thuật (thay thế googletrans) |
| `manga-ocr` | Latest | OCR chuyên biệt cho manga |
| `requests` | Latest | HTTP requests cho Roboflow API |
| `python-dotenv` | Latest | Environment variables management |
| `tenacity` | Latest | Retry mechanism với exponential backoff |
| `pillow` | Latest | Image processing |

---

## ✨ Features & Improvements

### Phase 1: Critical Fixes ✅
- ✅ Model weights → Roboflow REST API integration
- ✅ Font path → Fixed with `os.path.join()`
- ✅ Missing `translated/` folder → Auto-create

### Phase 2: Stability ✅
- ✅ Unstable `googletrans` → Replaced with `deep-translator`
- ✅ No error handling → Comprehensive try-except + logging
- ✅ Retry mechanism → Exponential backoff (3 attempts max)

### Phase 3: Visual Quality ✅
- ✅ Dynamic font sizing → Adjust based on textbox dimensions
- ✅ Text wrapping → Auto wrap to fit width
- ✅ Clear original text → Complete clearing before rendering
- ✅ Text centering → Horizontal & vertical alignment
- ✅ No overflow → Graceful handling of edge cases

### Phase 4: Polish & Enhancements ✅
- ✅ Multi-language support → 12 languages (not just Vietnamese)
- ✅ Processing statistics → Track images, textboxes, time
- ✅ Progress bar → Visual feedback for batch processing
- ✅ Enhanced UI → Better sidebar organization
- ✅ Model caching → `@st.cache_resource` for optimization

---

## 🖼️ Demo

### Giao diện ứng dụng
![Demo](./img/demo.png)

### Kết quả dịch manga
![Results](./img/results.png)

### Đọc manga đã dịch
![Results](./img/results3.png)

### Trang About
![About](./img/results2.png)

---

## 📝 Workflow xử lý

```
1. Upload ảnh (JPG/PNG)
         ↓
2. Roboflow API phát hiện textboxes
         ↓
3. Manga-OCR đọc text tiếng Nhật
         ↓
4. Deep-Translator dịch sang ngôn ngữ đã chọn
         ↓
5. Rendering text:
   a. Xóa sạch text gốc (background clearing)
   b. Tính font size phù hợp (dynamic sizing)
   c. Wrap text if needed (line wrapping)
   d. Vẽ text dịch (với centering)
         ↓
6. Lưu ảnh đã dịch vào thư mục `translated/`
         ↓
7. Hiển thị kết quả + statistics
```

---

## ⚠️ Lưu ý

- **Roboflow API**: Cần kết nối internet để sử dụng. Tài khoản miễn phí có giới hạn requests/tháng
- **Translation**: Deep-translator cần kết nối internet để dịch
- **Performance**: Model Manga-OCR sẽ được cache sau lần đầu tiên load
- **Font**: Hiện tại sử dụng `arial.ttf` - có thể thay đổi font khác trong `reader.py`
- **Language support**: Một số ngôn ngữ có thể không hỗ trợ tốt tuỳ vào deep-translator
- **Textbox detection**: Độ chính xác detection phụ thuộc vào quality của manga image

---

## 🐛 Troubleshooting

### Lỗi: "ROBOFLOW_API_KEY not found"
**Giải pháp:** Kiểm tra xem `.env` file có chứa `ROBOFLOW_API_KEY` không

### Lỗi: "Connection error to Roboflow API"
**Giải pháp:** 
- Kiểm tra kết nối internet
- Kiểm tra API key có valid không
- Kiểm tra giới hạn request của tài khoản Roboflow

### Lỗi: "Translation failed"
**Giải pháp:**
- Kiểm tra kết nối internet
- Thử lại (retry mechanism sẽ tự động chạy 3 lần)
- Thử đổi ngôn ngữ

### Text không hiển thị đúng trên ảnh
**Giải pháp:**
- Kiểm tra textbox size có quá nhỏ không
- Kiểm tra font file có tồn tại không
- Thử upload ảnh chất lượng cao hơn

---

## 📄 License

MIT License

---

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📊 Project Status

- **Version:** 1.0.0 (Production Ready)
- **Issues Fixed:** 10/10 ✅
- **Tests Passed:** 34/34 ✅
- **Phases Completed:** 4/4 ✅
- **Last Updated:** December 16, 2024

---

*Made with ❤️ by ThangBui - MTA*
