# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio 
import os
import time
import json

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 

from config import API_ID, API_HASH
from database.db import database 
from TechVJ.strings import strings, HELP_TXT

# ----- THROTTLE SETTINGS -----
# Throttle thresholds in bytes per second:
# 4 MB/s download, 8 MB/s upload
THRESHOLD_DOWN = 4 * 1024 * 1024   # 4 MB/s
THRESHOLD_UP   = 8 * 1024 * 1024   # 8 MB/s

# Dictionary to store last time and last bytes processed for each message & type
throttle_tracker = {}

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

# Progress callback with throttling
def progress(current, total, message, type):
    now = time.time()
    key = (message.id, type)
    if key not in throttle_tracker:
        throttle_tracker[key] = (now, current)
    else:
        last_time, last_bytes = throttle_tracker[key]
        delta_time = now - last_time
        delta_bytes = current - last_bytes
        if delta_time > 0:
            speed = delta_bytes / delta_time  # bytes per second
            threshold = THRESHOLD_DOWN if type == "down" else THRESHOLD_UP
            if speed > threshold:
                # Calculate the expected time for delta_bytes at the threshold speed
                expected_time = delta_bytes / threshold
                extra_time = expected_time - delta_time
                if extra_time > 0:
                    time.sleep(extra_time)
        throttle_tracker[key] = (time.time(), current)
        
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# Fast status updates (with shorter sleep intervals)
FAST_TRANSFER = True

async def downstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(0.5 if FAST_TRANSFER else 3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        status_text = f"Downloaded : {txt}" if txt.strip() else "."
        try:
            await client.edit_message_text(message.chat.id, message.id, status_text)
            await asyncio.sleep(1 if FAST_TRANSFER else 10)
        except Exception:
            await asyncio.sleep(0.5 if FAST_TRANSFER else 5)

async def upstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(0.5 if FAST_TRANSFER else 3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        status_text = f"Uploaded : {txt}" if txt.strip() else "."
        try:
            await client.edit_message_text(message.chat.id, message.id, status_text)
            await asyncio.sleep(1 if FAST_TRANSFER else 10)
        except Exception:
            await asyncio.sleep(0.5 if FAST_TRANSFER else 5)

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url="https://t.me/She_who_remain")
    ], [
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/+3bMBj190KOc3YzNk'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/+3bMBj190KOc3YzNk')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        message.chat.id, 
        f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        for msgid in range(fromID, toID + 1):
            # Private link (https://t.me/c/)
            if "https://t.me/c/" in message.text:
                user_data = database.find_one({'chat_id': message.chat.id})
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, message, chatid, msgid)
    
            # Bot link (https://t.me/b/)
            elif "https://t.me/b/" in message.text:
                user_data = database.find_one({"chat_id": message.chat.id})
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # Public link
            else:
                username = datas[3]
                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:    
                        user_data = database.find_one({"chat_id": message.chat.id})
                        if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                            await client.send_message(message.chat.id, strings['need_login'])
                            return
                        acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                        await acc.connect()
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            # Wait 5 seconds after processing each message before starting the next.
            await asyncio.sleep(5)

async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)
    chat = message.chat.id
    if msg_type == "Text":
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        return

    # Send a simple dot as the progress message.
    smsg = await client.send_message(message.chat.id, '.', reply_to_message_id=message.id)
    download_status_file = f'{message.id}downstatus.txt'
    upload_status_file = f'{message.id}upstatus.txt'
    down_task = asyncio.create_task(downstatus(client, download_status_file, smsg))

    file = None
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    finally:
        if os.path.exists(download_status_file):
            os.remove(download_status_file)

    up_task = asyncio.create_task(upstatus(client, upload_status_file, smsg))
    caption = msg.caption if msg.caption else None

    try:
        if msg_type == "Document":
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                ph_path = None
            try:
                await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)

        elif msg_type == "Video":
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                ph_path = None
            try:
                await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)

        elif msg_type == "Animation":
            try:
                await client.send_animation(chat, file, reply_to_message_id=message.id)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        elif msg_type == "Sticker":
            try:
                await client.send_sticker(chat, file, reply_to_message_id=message.id)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        elif msg_type == "Voice":
            try:
                await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        elif msg_type == "Audio":
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                ph_path = None
            try:
                await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])   
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)

        elif msg_type == "Photo":
            try:
                await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    finally:
        if file and os.path.exists(file):
            os.remove(file)
        if os.path.exists(upload_status_file):
            os.remove(upload_status_file)
        # Delete the progress (dot) message
        await client.delete_messages(message.chat.id, [smsg.id])
        # Wait 5 seconds after processing one file before finishing.
        await asyncio.sleep(5)

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
