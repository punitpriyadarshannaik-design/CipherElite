from pyrogram import Client, filters
from pyrogram.types import Message
import random
import asyncio

app = Client("toxic_savage_bot")

TOXIC_REPLIES = [
    "Arre madarchod teri maa ki chut mein aag laga ke naach raha hoon bc 😂",
    "Bhosdi ke dimag ki jagah gaand mein baith ke sochta hai kya nikal yahan se",
    "Teri behen ko kal raat 4 baar choda tha ab tu aa gaya randi ke pille",
    "Saale harami teri puri khandaan ki gaand mein mera lund ghusa ke chod dunga",
    "Fuck off gandu teri maa ka bhosda itna loose hai ki puri colony chod chuki hai",
    "Bhai tu itna chutiya hai ki teri maa bhi sochti hogi ki ye kiska sperm tha",
    "Tere jaise chutiye ko dekh ke hi mera mood kharab ho jata hai gaand phaad dun kya",
    "Random mode on teri gaand mein bomb daal ke remote se udaa dun kya bc",
    "Teri life itni bakwas hai ki teri behen bhi dusre ke saath maze le rahi hogi",
    "Madarchod bol kya chahiye maa chodun teri ya behen ko line mein khada karun",

    """Sun le randi ke bacche tu itna bekaar hai ki teri maa bhi regret karti hogi tune paida hone ka
Tera baap bhi nahi pata hoga tujhe kisne banaya
Ab yahan aa ke bakchodi karta hai
Teri gaand mein itna bada danda ghusa dunga ki 7 din tak toilet nahi kar payega samjha kya gandu""",

    """Haan bol na madarchod kya scene hai
Teri zindagi itni fuckup hai ki main bhi dekh ke has raha hoon
Teri gf roz kisi aur ke saath leti hogi
Chutiya sala""",

    """Bina soche jawab
Teri maa ki chut
Teri behen ki chut
Teri puri family ki gaand
Sab mar jaayenge agar main serious ho gaya"""
]


def get_toxic_reply(message_text: str = ""):
    text = (message_text or "").lower()

    trigger_words = ["hi", "hello", "kaise", "kese", "kya", "bol"]

    if any(word in text for word in trigger_words):
        return (
            random.choice(TOXIC_REPLIES)
            + "\n\nAur bol na chutiye kya scene hai aaj"
        )

    if random.random() < 0.3:
        long_replies = [r for r in TOXIC_REPLIES if len(r) > 100]
        return random.choice(long_replies)

    return random.choice(TOXIC_REPLIES)


@app.on_message(filters.private & ~filters.me)
async def toxic_private(client, message: Message):
    try:
        await asyncio.sleep(random.uniform(0.8, 3.5))

        reply = get_toxic_reply(message.text or "")

        await message.reply_text(reply)

        print(
            f"[TOXIC] Reply sent to "
            f"{message.from_user.first_name if message.from_user else 'Unknown'}"
        )

    except Exception as e:
        print(f"Error: {e}")


@app.on_message(filters.group & ~filters.me)
async def toxic_group(client, message: Message):
    try:
        if random.random() < 0.35:
            await asyncio.sleep(random.uniform(1.5, 5))

            reply = get_toxic_reply(message.text or "")

            await message.reply_text(reply)

    except Exception as e:
        print(f"Group Error: {e}")


if __name__ == "__main__":
    print("🚀 Toxic Savage Userbot Started")
    print("⚠️ Warning Account ban ho sakta hai private use karo")

    app.run()
