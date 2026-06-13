import os
import asyncio
from telethon import events
from plugins.bot import add_handler
from utils.decorators import rishabh
import yt_dlp
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types import StreamType

call = None
queue = []
is_playing = False
current_song = None

def init(client_instance):
    global call
    call = PyTgCalls(client_instance)
    call.start()
    
    commands = [
        ".play <song name> - Play in VC",
        ".pause - Pause",
        ".resume - Resume",
        ".skip - Skip",
        ".stop - Stop & Leave",
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
    except:
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
    except:
        await play_next(chat_id)

@events.register(events.NewMessage(pattern=r"^\.play (.+)", outgoing=True))
@rishabh()
async def play_command(event):
    global queue
    query = event.pattern_match.group(1).strip()
    status = await event.edit("**🎵 Downloading...**")
    
    path, title = await download_song(query)
    if not path:
        await status.edit("**❌ Download failed**")
        return
    
    queue.append((path, title))
    await status.edit(f"**✅ Added to Queue:** `{title}`")
    
    if not is_playing:
        chat = await event.get_chat()
        await play_next(chat.id)

@events.register(events.NewMessage(pattern=r"^\.(pause|resume|skip|stop|queue)$", outgoing=True))
@rishabh()
async def music_controls(event):
    cmd = event.pattern_match.group(1)
    chat_id = event.chat_id
    if cmd == "pause":
        await call.pause_stream(chat_id)
        await event.edit("**⏸ Paused**")
    elif cmd == "resume":
        await call.resume_stream(chat_id)
        await event.edit("**▶ Resumed**")
    elif cmd == "skip":
        await call.leave_group_call(chat_id)
        await asyncio.sleep(1)
        await play_next(chat_id)
        await event.edit("**⏭ Skipped**")
    elif cmd == "stop":
        await call.leave_group_call(chat_id)
        queue.clear()
        global is_playing, current_song
        is_playing = False
        current_song = None
        await event.edit("**⏹ Stopped & Left VC**")
    elif cmd == "queue":
        text = "**🎵 Current Queue:**\n\n"
        if current_song:
            text += f"▶ **Now Playing:** {current_song}\n\n"
        for i, (_, title) in enumerate(queue, 1):
            text += f"{i}. {title}\n"
        await event.edit(text)
