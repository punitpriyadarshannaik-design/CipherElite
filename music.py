# Auto load plugin
def __load__(client):
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(init(client))
    except Exception as e:
        print(f"Music Load Error: {e}") os
import asyncio
from telethon import events
from plugins.bot import add_handler
import yt_dlp

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types.stream import StreamType

# Safe decorator import
try:
    from utils.decorators import rishabh
except:
    rishabh = lambda: lambda f: f

call = None
queue = []
is_playing = False
current_song = None


async def init(client_instance):
    global call

    call = PyTgCalls(client_instance)
    await call.start()

    # Auto play next song
    @call.on_stream_end()
    async def stream_ended(_, update):
        await asyncio.sleep(1)
        await play_next(update.chat_id)

    commands = [
        ".play <song name> - Play music in VC",
        ".pause - Pause current song",
        ".resume - Resume current song",
        ".skip - Skip current song",
        ".stop - Stop music & leave VC",
        ".queue - Show queue"
    ]

    add_handler("music", commands, "🎵 Music Player")


async def download_song(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"ytsearch1:{query}",
                download=True
            )

            if "entries" in info:
                info = info["entries"][0]

            filename = ydl.prepare_filename(info)
            title = info.get("title", query)

            return filename, title

    except Exception as e:
        print(f"Download Error: {e}")
        return None, None


async def play_next(chat_id):
    global is_playing, current_song

    if not queue:
        is_playing = False
        current_song = None

        try:
            await call.leave_group_call(chat_id)
        except:
            pass

        return

    path, title = queue.pop(0)
    current_song = title

    try:
        await call.join_group_call(
            chat_id,
            AudioPiped(
                path,
                HighQualityAudio()
            ),
            stream_type=StreamType().pulse_stream
        )

        is_playing = True

    except Exception as e:
        print(f"Play Error: {e}")

        await asyncio.sleep(2)
        await play_next(chat_id)


@events.register(
    events.NewMessage(
        pattern=r"^\.play (.+)",
        outgoing=True
    )
)
@rishabh()
async def play_command(event):
    global queue, is_playing

    query = event.pattern_match.group(1).strip()

    status = await event.edit(
        "**🎵 Downloading song...**"
    )

    path, title = await download_song(query)

    if not path:
        return await status.edit(
            "**❌ Failed to download song**"
        )

    queue.append((path, title))

    await status.edit(
        f"**✅ Added to Queue:** `{title}`\n"
        f"📍 Position: {len(queue)}"
    )

    if not is_playing:
        await play_next(event.chat_id)


@events.register(
    events.NewMessage(
        pattern=r"^\.(pause|resume|skip|stop|queue)$",
        outgoing=True
    )
)
@rishabh()
async def music_controls(event):
    global is_playing, current_song

    cmd = event.pattern_match.group(1)

    try:
        if cmd == "pause":
            await call.pause_stream(event.chat_id)

            await event.edit(
                "**⏸ Music Paused**"
            )

        elif cmd == "resume":
            await call.resume_stream(event.chat_id)

            await event.edit(
                "**▶ Music Resumed**"
            )

        elif cmd == "skip":
            await call.leave_group_call(event.chat_id)

            await asyncio.sleep(1)

            await play_next(event.chat_id)

            await event.edit(
                "**⏭ Song Skipped**"
            )

        elif cmd == "stop":
            queue.clear()

            is_playing = False
            current_song = None

            try:
                await call.leave_group_call(event.chat_id)
            except:
                pass

            await event.edit(
                "**⏹ Music Stopped & Left VC**"
            )

        elif cmd == "queue":
            text = "**🎵 Music Queue:**\n\n"

            if current_song:
                text += (
                    f"▶ Now Playing: "
                    f"`{current_song}`\n\n"
                )

            if queue:
                for i, (_, title) in enumerate(queue, start=1):
                    text += f"{i}. `{title}`\n"
            else:
                text += "No songs in queue."

            await event.edit(text)

    except Exception as e:
        await event.edit(
            f"**❌ Error:** `{str(e)[:150]}`"
        )
        # Auto load plugin
def __load__(client):
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(init(client))
    except Exception as e:
        print(f"Music Load Error: {e}")
