"""
Plain text message handler — handles watermark text input, page range input,
and custom combine number input.
"""

import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.state     import get_state, clear_state
from utils.pdf_utils import watermark_pdf, extract_pages, page_count, combine_pages, cleanup
from config          import TEMP_DIR

os.makedirs(TEMP_DIR, exist_ok=True)


@Client.on_message(filters.text & filters.private & ~filters.command(
    ["start", "help", "about", "combine", "split", "merge", "rotate",
     "compress", "watermark", "extract", "info"]
))
async def handle_text(client: Client, message: Message):
    uid    = message.from_user.id
    state  = get_state(uid)
    action = state.get("action")

    # ── Custom combine number ─────────────────────────────────────────
    if action == "await_custom_combine":
        path = state.get("file_path")
        if not path or not os.path.exists(path):
            await message.reply_text("⚠️ Session expired. Please send your PDF again.")
            clear_state(uid)
            return

        raw = message.text.strip()
        try:
            n = int(raw)
            if not (1 <= n <= 32):
                raise ValueError
        except ValueError:
            await message.reply_text("⚠️ Please send a whole number between **1** and **32**.")
            return

        prog = await message.reply_text(f"🗂 Combining **{n} pages** per sheet… please wait.")
        try:
            total   = page_count(path)
            out     = combine_pages(path, n)
            out_pgs = page_count(out)
            await message.reply_document(
                document=out,
                caption=(
                    f"✅ Done!\n"
                    f"Original: `{total}` pages → Output: `{out_pgs}` sheet(s)\n"
                    f"Each sheet contains **{n}** original pages.\n"
                    f"📌 _Print at 100% scale for best clarity._"
                ),
                file_name=f"combined_{n}up.pdf",
            )
            cleanup(out, path)
            clear_state(uid)
            await prog.delete()
        except Exception as e:
            await prog.edit_text(f"❌ Error: `{e}`")

    # ── Watermark text ────────────────────────────────────────────────
    elif action == "await_watermark_text":
        text = message.text.strip()
        path = state.get("file_path")
        if not path or not os.path.exists(path):
            await message.reply_text("⚠️ Session expired. Please send your PDF again.")
            clear_state(uid)
            return

        prog = await message.reply_text(f"💧 Applying watermark `{text}`…")
        try:
            out = watermark_pdf(path, text)
            await message.reply_document(
                document=out,
                caption=f"✅ Watermark **{text}** applied to all pages!",
                file_name="watermarked.pdf",
            )
            cleanup(out, path)
            clear_state(uid)
            await prog.delete()
        except Exception as e:
            await prog.edit_text(f"❌ Error: `{e}`")

    # ── Page extraction range ─────────────────────────────────────────
    elif action == "await_extract_range":
        path = state.get("file_path")
        if not path or not os.path.exists(path):
            await message.reply_text("⚠️ Session expired. Please send your PDF again.")
            clear_state(uid)
            return

        raw = message.text.strip()
        try:
            if "-" in raw:
                parts = raw.split("-")
                start, end = int(parts[0].strip()), int(parts[1].strip())
            else:
                start = end = int(raw.strip())
        except ValueError:
            await message.reply_text(
                "⚠️ Invalid format. Use `3-7` for a range or `5` for a single page."
            )
            return

        total = page_count(path)
        if start < 1 or end > total or start > end:
            await message.reply_text(
                f"⚠️ Invalid range. This PDF has **{total}** pages.\n"
                f"Enter a range between `1` and `{total}`."
            )
            return

        prog = await message.reply_text(f"✂️ Extracting pages {start}–{end}…")
        try:
            out = extract_pages(path, start, end)
            n   = end - start + 1
            await message.reply_document(
                document=out,
                caption=f"✅ Extracted **{n}** page(s) ({start}–{end}).",
                file_name=f"pages_{start}_to_{end}.pdf",
            )
            cleanup(out, path)
            clear_state(uid)
            await prog.delete()
        except Exception as e:
            await prog.edit_text(f"❌ Error: `{e}`")
