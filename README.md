# Manga Reader Assistant

> **Ứng dụng đọc và dịch Manga tiếng Nhật sang tiếng Việt tự động**

## 📖 Giới thiệu

**Manga Reader Assistant** là một ứng dụng sử dụng Computer Vision và AI để tự động phát hiện, nhận dạng và dịch văn bản trong manga tiếng Nhật sang tiếng Việt.

- **Author:** ThangBui
- **Major:** Computer Vision & AI
- **Affiliation:** MTA (Military Technical Academy)

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
│   YOLOv8    │     Manga-OCR       │    Google Translate     │
│  Detection  │   Text Recognition  │      Translation        │
└─────────────┴─────────────────────┴─────────────────────────┘
```

---

## 🔧 Các thành phần chính

### 1. **Detection - Phát hiện vùng text (YOLOv8)**
- Sử dụng model YOLOv8 đã được train để phát hiện các textbox/speech bubble trong manga
- Model đã được pruning (cắt bớt 2 heads) để giảm kích thước

### 2. **OCR - Nhận dạng văn bản (Manga-OCR)**
- Sử dụng thư viện [manga-ocr](https://github.com/kha-white/manga-ocr)
- Chuyên biệt cho việc nhận dạng chữ Nhật trong manga

### 3. **Translation - Dịch thuật (Google Translate)**
- Sử dụng `googletrans` để dịch từ tiếng Nhật → tiếng Việt
- Tự động render text đã dịch lên ảnh

### 4. **Web UI (Streamlit)**
- Giao diện web thân thiện với 3 tabs:
  - **Assistant:** Upload và dịch manga
  - **Read Only:** Xem lại manga đã dịch
  - **About:** Thông tin về project

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
└── translated/          # Thư mục lưu ảnh đã dịch
```

---

## 🚀 Cài đặt

### Yêu cầu
- Python >= 3.10
- Anaconda (khuyến nghị)

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

### Bước 4: Tải model weights
Tải file weights YOLOv8 từ [Google Drive](https://drive.google.com/file/d/1-XpMOB8wN1j1d57iq6JBLyzAQlPmyLoV/view?usp=drive_link) và đặt vào thư mục gốc với tên `yolov8_manga.pt`

### Bước 5: Chạy ứng dụng
```bash
streamlit run main.py
```

---

## 📦 Dependencies

| Package | Mô tả |
|---------|-------|
| `ultralytics` | YOLOv8 object detection |
| `streamlit` | Web UI framework |
| `streamlit_option_menu` | Sidebar menu component |
| `googletrans==3.1.0a0` | Google Translate API |
| `manga-ocr` | OCR chuyên biệt cho manga |

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

1. **Upload ảnh** → Người dùng upload trang manga (JPG/PNG)
2. **Detection** → YOLOv8 phát hiện các speech bubble
3. **OCR** → Manga-OCR đọc text tiếng Nhật trong từng bubble
4. **Translation** → Google Translate dịch sang tiếng Việt
5. **Rendering** → Text tiếng Việt được vẽ lên ảnh
6. **Save** → Ảnh đã dịch được lưu vào thư mục `translated/`

---

## ⚠️ Lưu ý

- Chất lượng dịch phụ thuộc vào độ chính xác của detection và OCR
- Font hiện tại sử dụng `arial.ttf` - có thể thay đổi trong `reader.py`
- Cần kết nối internet để sử dụng Google Translate

---

## 📄 License

MIT License

---

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo Issue hoặc Pull Request.
