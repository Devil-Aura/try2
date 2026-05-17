"""
Handles incoming PDF documents — shows the action menu.
"""

import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.state    import set_state, get_state, update_state
from utils.keyboards import action_kb, confirm_kb
from config import MAX_FILE_SIZE_MB, TEMP_DIR

os.makedirs(TEMP_DIR, exist_ok=True)


@Client.on_message(filters.document & filters.private)
async def receive_pdf(client: Client, message: Message):
    doc = message.document

    # Accept only PDFs
    if not (doc.mime_type == "application/pdf" or doc.file_name.lower().endswith(".pdf")):
        await message.reply_text("⚠️ Please send a **PDF** file.")
        return

    # Size check
    if doc.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        await message.reply_text(f"⚠️ File too large. Max size is {MAX_FILE_SIZE_MB} MB.")
        return

    uid = message.from_user.id
    state = get_state(uid)

    # ── Merge mode: accumulate files ──────────────────────────────────
    if state.get("action") == "merge_collect":
        prog = await message.reply_text("⬇️ Downloading file…")
        path = await message.download(file_name=os.path.join(TEMP_DIR, f"{uid}_{doc.file_unique_id}.pdf"))
        files: list = state.get("merge_files", [])
        files.append(path)
        update_state(uid, merge_files=files)
        await prog.edit_text(
            f"✅ Got **{len(files)}** PDF(s) so far.\n"
            "Send more, or tap **Done** to merge.",
            reply_markup=confirm_kb(),
        )
        return

    # ── Normal flow: download then show menu ──────────────────────────
    prog = await message.reply_text("⬇️ Downloading…")
    path = await message.download(file_name=os.path.join(TEMP_DIR, f"{uid}_{doc.file_unique_id}.pdf"))
    set_state(uid, file_path=path)

    await prog.edit_text(
        f"📄 **{doc.file_name}**\nWhat would you like to do?",
        reply_markup=action_kb(),
    )
