"""
Callback query handlers for all inline button actions.
"""

import os
import zipfile
import asyncio

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.state     import get_state, set_state, clear_state, update_state
from utils.keyboards import pages_per_sheet_kb, rotate_kb, action_kb
from utils.pdf_utils import (
    combine_pages, split_pdf, merge_pdfs, compress_pdf,
    rotate_pdf, extract_pages, watermark_pdf, page_count, cleanup
)
from config import TEMP_DIR

os.makedirs(TEMP_DIR, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

async def _send_pdf(cq: CallbackQuery, path: str, caption: str, filename: str):
    await cq.message.reply_document(
        document=path,
        caption=caption,
        file_name=filename,
    )


# ──────────────────────────────────────────────────────────────────────
# Cancel
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^cancel$"))
async def cb_cancel(client: Client, cq: CallbackQuery):
    uid = cq.from_user.id
    state = get_state(uid)
    cleanup(state.get("file_path"))
    for p in state.get("merge_files", []):
        cleanup(p)
    clear_state(uid)
    await cq.message.edit_text("❌ Cancelled.")


# ──────────────────────────────────────────────────────────────────────
# Help / About (inline)
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^show_help$"))
async def cb_show_help(client: Client, cq: CallbackQuery):
    await cq.message.edit_text(
        "📖 **Help**\n\nSend me any PDF file and I'll show a menu of actions:\n\n"
        "• 🗂 **Combine** — fit N pages onto one printed sheet\n"
        "• ✂️ **Split** — one page per PDF in a ZIP\n"
        "• 🔀 **Merge** — combine multiple PDFs into one\n"
        "• 🔄 **Rotate** — rotate all pages\n"
        "• 🗜 **Compress** — shrink file size\n"
        "• 💧 **Watermark** — stamp text on every page\n"
        "• ✂️ **Extract** — pull out a page range\n"
        "• 📊 **Page count** — count pages instantly",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("« Back", callback_data="show_start")
        ]])
    )


@Client.on_callback_query(filters.regex("^show_about$"))
async def cb_show_about(client: Client, cq: CallbackQuery):
    await cq.message.edit_text(
        "🤖 **PDF Tools Bot**\n\nBuilt with Python & Pyrogram\nBrand: @World_Fastest_Bots\n\nPublic & free for everyone.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("« Back", callback_data="show_start")
        ]])
    )


@Client.on_callback_query(filters.regex("^show_start$"))
async def cb_show_start(client: Client, cq: CallbackQuery):
    await cq.message.edit_text(
        "👋 **Welcome to PDF Tools Bot!**\n\nSend me a PDF to get started, or use /help.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Help", callback_data="show_help"),
             InlineKeyboardButton("ℹ️ About", callback_data="show_about")],
        ])
    )


# ──────────────────────────────────────────────────────────────────────
# Action menu selections
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^action_combine$"))
async def cb_action_combine(client: Client, cq: CallbackQuery):
    uid = cq.from_user.id
    if not get_state(uid).get("file_path"):
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    await cq.message.edit_text(
        "🗂 **Combine pages**\n\nHow many original pages should be placed on each printed sheet?",
        reply_markup=pages_per_sheet_kb(),
    )


@Client.on_callback_query(filters.regex("^action_split$"))
async def cb_action_split(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    path  = state.get("file_path")
    if not path:
        await cq.answer("Send a PDF first!", show_alert=True)
        return

    await cq.message.edit_text("✂️ Splitting PDF…")
    try:
        pages = split_pdf(path)
        total = len(pages)

        zip_path = os.path.join(TEMP_DIR, f"{uid}_split.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, p in enumerate(pages, 1):
                zf.write(p, arcname=f"page_{i:03d}.pdf")

        await cq.message.reply_document(
            document=zip_path,
            caption=f"✅ Split into **{total}** pages. Download the ZIP!",
            file_name="split_pages.zip",
        )
        cleanup(zip_path, *pages, path)
        clear_state(uid)
        await cq.message.delete()
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex("^action_merge$"))
async def cb_action_merge(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    path  = state.get("file_path")
    if not path:
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    set_state(uid, action="merge_collect", merge_files=[path])
    await cq.message.edit_text(
        "🔀 **Merge mode** — send more PDF files.\nWhen done, tap **Done — merge now**.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Done — merge now", callback_data="merge_now"),
            InlineKeyboardButton("❌ Cancel",           callback_data="cancel"),
        ]])
    )


@Client.on_callback_query(filters.regex("^merge_now$"))
async def cb_merge_now(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    files = state.get("merge_files", [])
    if len(files) < 2:
        await cq.answer("Send at least 2 PDFs!", show_alert=True)
        return

    await cq.message.edit_text("🔀 Merging PDFs…")
    try:
        out = merge_pdfs(files)
        await _send_pdf(cq, out, f"✅ Merged **{len(files)}** PDFs!", "merged.pdf")
        cleanup(out, *files)
        clear_state(uid)
        await cq.message.delete()
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex("^action_rotate$"))
async def cb_action_rotate(client: Client, cq: CallbackQuery):
    uid = cq.from_user.id
    if not get_state(uid).get("file_path"):
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    await cq.message.edit_text(
        "🔄 **Rotate pages**\n\nChoose rotation angle:",
        reply_markup=rotate_kb(),
    )


@Client.on_callback_query(filters.regex("^action_compress$"))
async def cb_action_compress(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    path  = state.get("file_path")
    if not path:
        await cq.answer("Send a PDF first!", show_alert=True)
        return

    await cq.message.edit_text("🗜 Compressing…")
    try:
        orig_size = os.path.getsize(path)
        out       = compress_pdf(path)
        new_size  = os.path.getsize(out)
        saved     = orig_size - new_size
        pct       = (saved / orig_size * 100) if orig_size else 0

        await _send_pdf(
            cq, out,
            f"✅ Compressed!\n"
            f"Original: `{orig_size//1024} KB`\n"
            f"New: `{new_size//1024} KB`\n"
            f"Saved: `{saved//1024} KB ({pct:.1f}%)`",
            "compressed.pdf",
        )
        cleanup(out, path)
        clear_state(uid)
        await cq.message.delete()
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex("^action_watermark$"))
async def cb_action_watermark(client: Client, cq: CallbackQuery):
    uid = cq.from_user.id
    if not get_state(uid).get("file_path"):
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    update_state(uid, action="await_watermark_text")
    await cq.message.edit_text(
        "💧 **Watermark**\n\nReply with the text you want stamped on every page.\n"
        "Example: `CONFIDENTIAL` or `Draft 2024`"
    )


@Client.on_callback_query(filters.regex("^action_extract$"))
async def cb_action_extract(client: Client, cq: CallbackQuery):
    uid = cq.from_user.id
    if not get_state(uid).get("file_path"):
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    update_state(uid, action="await_extract_range")
    await cq.message.edit_text(
        "✂️ **Extract pages**\n\n"
        "Reply with the page range, e.g.:\n`3-7` (pages 3 to 7)\n`5` (just page 5)"
    )


@Client.on_callback_query(filters.regex("^action_pagecount$"))
async def cb_action_pagecount(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    path  = state.get("file_path")
    if not path:
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    try:
        n = page_count(path)
        await cq.message.edit_text(
            f"📊 This PDF has **{n} page{'s' if n != 1 else ''}**.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Back to actions", callback_data="back_to_actions"),
                InlineKeyboardButton("❌ Done", callback_data="cancel"),
            ]])
        )
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex("^back_to_actions$"))
async def cb_back_to_actions(client: Client, cq: CallbackQuery):
    await cq.message.edit_text("📄 What would you like to do?", reply_markup=action_kb())


# ──────────────────────────────────────────────────────────────────────
# Combine — custom number input
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^combine_custom$"))
async def cb_combine_custom(client: Client, cq: CallbackQuery):
    uid = cq.from_user.id
    if not get_state(uid).get("file_path"):
        await cq.answer("Send a PDF first!", show_alert=True)
        return
    update_state(uid, action="await_custom_combine")
    await cq.message.edit_text(
        "✏️ **Custom pages per sheet**\n\n"
        "Reply with any number between **1 and 32**.\n"
        "Example: `5` or `10`"
    )


# ──────────────────────────────────────────────────────────────────────
# Combine N pages per sheet
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^combine_(\d+)$"))
async def cb_combine(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    path  = state.get("file_path")
    n     = int(cq.data.split("_")[1])

    if not path:
        await cq.answer("Session expired. Please send your PDF again.", show_alert=True)
        return

    await cq.message.edit_text(f"🗂 Combining **{n} pages** per sheet… please wait.")
    try:
        total = page_count(path)
        out   = combine_pages(path, n)
        out_pages = page_count(out)

        await _send_pdf(
            cq, out,
            f"✅ Done!\n"
            f"Original: `{total}` pages → Output: `{out_pages}` sheet(s)\n"
            f"Each sheet contains **{n}** original pages.\n"
            f"📌 _Print at 100% scale for best clarity._",
            f"combined_{n}up.pdf",
        )
        cleanup(out, path)
        clear_state(uid)
        await cq.message.delete()
    except Exception as e:
        await cq.message.edit_text(f"❌ Error during processing:\n`{e}`")


# ──────────────────────────────────────────────────────────────────────
# Rotate
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^rotate_(\d+)$"))
async def cb_rotate(client: Client, cq: CallbackQuery):
    uid   = cq.from_user.id
    state = get_state(uid)
    path  = state.get("file_path")
    deg   = int(cq.data.split("_")[1])

    if not path:
        await cq.answer("Session expired. Send PDF again.", show_alert=True)
        return

    await cq.message.edit_text(f"🔄 Rotating all pages by **{deg}°**…")
    try:
        out = rotate_pdf(path, deg)
        await _send_pdf(cq, out, f"✅ Rotated all pages by **{deg}°**!", "rotated.pdf")
        cleanup(out, path)
        clear_state(uid)
        await cq.message.delete()
    except Exception as e:
        await cq.message.edit_text(f"❌ Error: `{e}`")
