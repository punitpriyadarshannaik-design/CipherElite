from telethon import events
import requests
import os
import random

API = "https://bot.lyo.su/quote/generate"

COLORS = {
    "red": "#ff4d4d",
    "blue": "#4da6ff",
    "green": "#4dff88",
    "pink": "#ff4fd8",
    "purple": "#b266ff",
    "black": "#0f0f0f",
    "white": "#ffffff",
    "indigo": "#4b0082"
}

@events.register(events.NewMessage(pattern=r"^\.q(?: |$)(.*)", outgoing=True))
async def quote_maker(event):

    reply = await event.get_reply_message()

    if not reply:
        await event.edit("Reply to a message")
        return

    args = event.pattern_match.group(1).lower().split()

    await event.edit("Creating Quote...")

    # FORMAT
    fmt = "webp"

    if "img" in args or "png" in args or "i" in args:
        fmt = "png"

    # COLOR
    color = "#0f0f0f"

    for arg in args:
        if arg in COLORS:
            color = COLORS[arg]

    if "random" in args:
        color = random.choice(list(COLORS.values()))

    # REPLY MODE
    reply_message = {}

    if "r" in args or "reply" in args:
        if reply.reply_to_msg_id:
            reply_message = {
                "chatId": reply.chat_id,
                "id": reply.reply_to_msg_id
            }

    sender = await reply.get_sender()

    name = sender.first_name or "User"

    text = reply.raw_text

    payload = {
        "type": "quote",
        "format": fmt,
        "backgroundColor": color,
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": [
            {
                "entities": [],
                "avatar": True,
                "from": {
                    "id": sender.id,
                    "name": name
                },
                "text": text,
                "replyMessage": reply_message
            }
        ]
    }

    try:
        r = requests.post(API, json=payload).json()

        image_url = r["result"]["image"]

        file_data = requests.get(image_url).content

        ext = "webp"

        if fmt == "png":
            ext = "png"

        file_name = f"quote.{ext}"

        with open(file_name, "wb") as f:
            f.write(file_data)

        await event.delete()

        await event.client.send_file(
            event.chat_id,
            file_name,
            reply_to=reply.id
        )

        os.remove(file_name)

    except Exception as e:
        await event.edit(f"Error: {str(e)}")
