import os
import asyncio
from telethon import events
from plugins.bot import add_handler
import yt_dlp
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types import StreamType

# Safety for decorator
try:
    from utils.decorators import rishabh
except:
    rishabh = lambda: lambda f: f  # bypass if decorator not found

call = None
queue = []
is_playing = False
current_song = None

def init(client_instance):
    global call
    call = PyTgCalls(client_instance)
    call.start()
    
    commands = [
        ".play <song name> - Play in voice chat",
        ".pause - Pause song",
        ".resume - Resume",
        ".skip - Skip song",
        ".stop - Stop & Leave VC",
        ".queue - Show queue"
    ]
    add_handler("music", commands, "🎵 Music Player")

async def download_song(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', query)
            return filename, title
    except Exception as e:
        print(f"Download Error: {e}")
        return None, None

async def play_next(chat_id):
    global is_playing, current_song
    if not queue:
        is_playing = False
        current_song = None
        return
    
    song_path, song_title = queue.pop(0)
    current_song = song_title
    try:
        await call.join_group_call(
            chat_id,
            AudioPiped(song_path, HighQualityAudio()),
            stream_type=StreamType().local_stream
        )
        is_playing = True
    except Exception as e:
        print(f"Play Error: {e}")
        await asyncio.sleep(2)
        await play_next(chat_id)

@events.register(events.NewMessage(pattern=r"^\.play (.+)", outgoing=True))
@rishabh()
async def play_command(event):
    global queue
    query = event.pattern_match.group(1).strip()
    status = await event.edit("**🎵 Downloading song...**")
    
    path, title = await download_song(query)
    if not path:
        await status.edit("**❌ Download failed!**")
        return
    
    queue.append((path, title))
    await status.edit(f"**✅ Added to Queue:** `{title}`\n📍 Position: {len(queue)}")
    
    if not is_playing:
        chat = await event.get_chat()
        await play_next(chat.id)

@events.register(events.NewMessage(pattern=r"^\.(pause|resume|skip|stop|queue)$", outgoing=True))
@rishabh()
async def music_controls(event):
    cmd = event.pattern_match.group(1)
    try:
        if cmd == "pause":
            await call.pause_stream(event.chat_id)
            await event.edit("**⏸ Paused**")
        elif cmd == "resume":
            await call.resume_stream(event.chat_id)
            await event.edit("**▶ Resumed**")
        elif cmd == "skip":
            await call.leave_group_call(event.chat_id)
            await asyncio.sleep(1)
            chat = await event.get_chat()
            await play_next(chat.id)
            await event.edit("**⏭ Skipped**")
        elif cmd == "stop":
            await call.leave_group_call(event.chat_id)
            queue.clear()
            global is_playing, current_song
            is_playing = False
            current_song = None
            await event.edit("**⏹ Stopped & Left Voice Chat**")
        elif cmd == "queue":
            text = "**🎵 Music Queue:**\n\n"
            if current_song:
                text += f"▶ **Now Playing:** {current_song}\n\n"
            if queue:
                for i, (_, title) in enumerate(queue, 1):
                    text += f"{i}. {title}\n"
            else:
                text += "No songs in queue."
            await event.edit(text)
    except Exception as e:
        await event.edit(f"**Error:** {str(e)[:100]}")
