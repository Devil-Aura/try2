# 📄 PDF Tools Bot

A full-featured Telegram PDF bot built with Python & Pyrogram.  
Brand: **@World_Fastest_Bots**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗂 **Combine pages** | Put 2/3/4/6/8/9/12/16 original pages onto one printed sheet |
| ✂️ **Split** | Split every page into its own PDF, delivered as a ZIP |
| 🔀 **Merge** | Combine multiple PDFs into one |
| 🔄 **Rotate** | Rotate all pages 90°, 180°, or 270° |
| 🗜 **Compress** | Lossless size reduction |
| 💧 **Watermark** | Stamp custom text on every page |
| ✂️ **Extract pages** | Pull out a page range into a new PDF |
| 📊 **Page count** | Instantly count pages |

---

## 🛠 Setup on VPS

### 1. Install system dependencies

```bash
apt update && apt install -y python3 python3-pip poppler-utils
```

### 2. Upload / clone the bot

```bash
# Upload the zip and extract, or clone your repo
unzip pdf_bot.zip -d pdf_bot
cd pdf_bot
```

### 3. Install Python packages

```bash
pip3 install -r requirements.txt
```

### 4. Set your bot token

Edit `config.py` and replace:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```
with your token from [@BotFather](https://t.me/BotFather).

### 5. Run the bot

**Direct run (testing):**
```bash
python3 bot.py
```

**As a systemd service (recommended for VPS):**
```bash
cp pdf_bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pdf_bot
systemctl start pdf_bot
systemctl status pdf_bot
```

---

## 📁 Project Structure

```
pdf_bot/
├── bot.py                  # Entry point
├── config.py               # API credentials & settings
├── requirements.txt
├── pdf_bot.service         # Systemd service
├── handlers/
│   ├── start.py            # /start /help /about
│   ├── receive.py          # Incoming PDF handler
│   ├── callbacks.py        # All inline button callbacks
│   ├── commands.py         # Command shortcuts
│   └── text_handler.py     # Watermark text / page range input
└── utils/
    ├── pdf_utils.py        # All PDF processing functions
    ├── keyboards.py        # Inline keyboard builders
    └── state.py            # In-memory user state
```

---

## ⚙️ Configuration (`config.py`)

| Variable | Description |
|---|---|
| `API_ID` | Your Telegram API ID |
| `API_HASH` | Your Telegram API hash |
| `BOT_TOKEN` | Token from @BotFather |
| `TEMP_DIR` | Folder for temporary files (auto-cleaned) |
| `MAX_FILE_SIZE_MB` | Max PDF size accepted (default 50 MB) |
| `RENDER_DPI` | Rendering quality for page combining (default 200) |

---

## 🖨 Print Tips

When using **Combine pages**, the output PDF is optimized for printing:
- Pages are rendered at 200 DPI with preserved aspect ratio
- Each sheet fits up to 16 original pages
- Print at **100% scale** for best readability

---

## 📬 Support

Feedback & issues → [@World_Fastest_Bots](https://t.me/World_Fastest_Bots)
