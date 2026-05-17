"""
Inline keyboard builders.
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def pages_per_sheet_kb() -> InlineKeyboardMarkup:
    """Select how many pages to combine into one sheet."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1️⃣  1 page",  callback_data="combine_1"),
            InlineKeyboardButton("2️⃣  2 pages", callback_data="combine_2"),
            InlineKeyboardButton("3️⃣  3 pages", callback_data="combine_3"),
        ],
        [
            InlineKeyboardButton("4️⃣  4 pages", callback_data="combine_4"),
            InlineKeyboardButton("6️⃣  6 pages", callback_data="combine_6"),
            InlineKeyboardButton("8️⃣  8 pages", callback_data="combine_8"),
        ],
        [
            InlineKeyboardButton("9️⃣  9 pages",  callback_data="combine_9"),
            InlineKeyboardButton("🔢 12 pages", callback_data="combine_12"),
            InlineKeyboardButton("🔢 16 pages", callback_data="combine_16"),
        ],
        [InlineKeyboardButton("✏️ Custom number…", callback_data="combine_custom")],
        [InlineKeyboardButton("❌ Cancel",         callback_data="cancel")],
    ])


def rotate_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("↻ 90°",  callback_data="rotate_90"),
            InlineKeyboardButton("↻ 180°", callback_data="rotate_180"),
            InlineKeyboardButton("↻ 270°", callback_data="rotate_270"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])


def action_kb() -> InlineKeyboardMarkup:
    """Shown after receiving a PDF — pick what to do."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗂 Combine pages", callback_data="action_combine"),
            InlineKeyboardButton("✂️ Split",         callback_data="action_split"),
        ],
        [
            InlineKeyboardButton("🔀 Merge (send more)", callback_data="action_merge"),
            InlineKeyboardButton("🔄 Rotate",            callback_data="action_rotate"),
        ],
        [
            InlineKeyboardButton("🗜 Compress",    callback_data="action_compress"),
            InlineKeyboardButton("💧 Watermark",   callback_data="action_watermark"),
        ],
        [
            InlineKeyboardButton("✂️ Extract pages", callback_data="action_extract"),
            InlineKeyboardButton("📊 Page count",    callback_data="action_pagecount"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Done — merge now", callback_data="merge_now"),
            InlineKeyboardButton("❌ Cancel",           callback_data="cancel"),
        ]
    ])
