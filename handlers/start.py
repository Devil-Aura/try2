"""
/start, /help, /about commands
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

START_TEXT = """
👋 **Welcome to PDF Tools Bot!**

I can do a lot with your PDF files. Just send me any PDF and I'll give you options.

**Available commands:**
/start   — Show this message
/help    — Detailed help
/combine — Combine pages (send PDF first)
/split   — Split PDF into single pages
/merge   — Merge multiple PDFs
/rotate  — Rotate all pages
/compress — Compress PDF size
/watermark — Add text watermark
/extract — Extract a page range
/info    — Show PDF info & page count
/about   — About this bot

📎 **Or just send a PDF and choose from the menu!**
"""

HELP_TEXT = """
📖 **PDF Tools Bot — Help**

**📌 How to use:**
1. Send any PDF file to me.
2. I'll show a menu — pick what you want to do.

**🗂 Combine pages**
Puts multiple original pages onto a single printed page.
Great for saving paper when printing!
Choose 2, 3, 4, 6, 8, 9, 12, or 16 pages per sheet.

**✂️ Split**
Splits the PDF into individual single-page PDFs, delivered as a ZIP.

**🔀 Merge**
Send multiple PDFs one by one, then tap "Merge now" — I'll combine them all into one file.

**🔄 Rotate**
Rotate all pages 90°, 180°, or 270°.

**🗜 Compress**
Reduces file size using lossless compression.

**💧 Watermark**
Stamps your custom text diagonally on every page.

**✂️ Extract pages**
Pull out a range of pages (e.g. pages 3–7) into a new PDF.

**📊 Page count**
Instantly tells you how many pages a PDF has.
"""

ABOUT_TEXT = """
🤖 **PDF Tools Bot**

Built with ❤️ using Python & Pyrogram.
Brand: @World_Fastest_Bots

This bot is **public** — anyone can use it for free.

📬 Feedback? Reach out via @World_Fastest_Bots
"""


@Client.on_message(filters.command("start"))
async def cmd_start(client: Client, message: Message):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Help", callback_data="show_help"),
         InlineKeyboardButton("ℹ️ About", callback_data="show_about")],
    ])
    await message.reply_text(START_TEXT, reply_markup=kb)


@Client.on_message(filters.command("help"))
async def cmd_help(client: Client, message: Message):
    await message.reply_text(HELP_TEXT)


@Client.on_message(filters.command("about"))
async def cmd_about(client: Client, message: Message):
    await message.reply_text(ABOUT_TEXT)
