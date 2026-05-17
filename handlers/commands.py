"""
Command shortcuts — /combine, /split, /merge, /rotate, /compress, /watermark,
/extract, /info
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.state     import get_state, update_state
from utils.keyboards import action_kb
from utils.pdf_utils import page_count


@Client.on_message(filters.command(["combine", "split", "merge", "rotate",
                                    "compress", "watermark", "extract", "info"]))
async def cmd_shortcut(client: Client, message: Message):
    uid   = message.from_user.id
    state = get_state(uid)

    if not state.get("file_path"):
        await message.reply_text(
            "📎 Please **send your PDF file first**, then use this command."
        )
        return

    cmd = message.command[0].lower()

    if cmd == "info":
        path  = state["file_path"]
        total = page_count(path)
        await message.reply_text(f"📊 Your PDF has **{total}** page(s).")
        return

    # Trigger the correct action via a fake state nudge
    action_map = {
        "combine":   "action_combine",
        "split":     "action_split",
        "merge":     "action_merge",
        "rotate":    "action_rotate",
        "compress":  "action_compress",
        "watermark": "action_watermark",
        "extract":   "action_extract",
    }
    action = action_map.get(cmd)
    if action:
        await message.reply_text(
            "📄 Choose your action:",
            reply_markup=action_kb(),
        )
