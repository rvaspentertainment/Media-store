# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.database import unpack_new_file_id
from plugins.users_api import get_user, get_short_link
from plugins.dbusers import db
import re
import os
import json
import base64
import logging

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

def get_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / 1024 ** 2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024 ** 3:.2f} GB"

from pyrogram.enums import MessageMediaType
from pymongo.errors import PyMongoError

@Client.on_message((filters.document | filters.video | filters.audio) & filters.chat(-1002400439772))
async def incoming_gen_link(bot, message):
    try:
        # Get bot's username
        username = (await bot.get_me()).username

        # Determine the media type
        if message.video:
            media = message.video
        elif message.document:
            media = message.document
        elif message.audio:
            media = message.audio
        else:
            raise ValueError("Unsupported media type.")

        # Ensure caption exists
        if not message.caption:
            raise ValueError("Caption is required to extract movie details.")

        # Extract details from caption
        caption_parts = message.caption.strip().split("-")
        if len(caption_parts) < 5:
            raise ValueError("Caption format is incorrect. Expected format: poster-movie_name-release_year-movie_language-movies_no")

        poster = caption_parts[0]
        movie_name = caption_parts[1]
        release_year = caption_parts[2]
        movie_language = caption_parts[3]
        movies_no = caption_parts[4]
        
        # Extract user_id from movies_no
        user_id = int(movies_no.split("-")[0])  # Extract user_id from movies_no

        # Extract file details
        file_id, ref = unpack_new_file_id(media.file_id)
        string = f'file_{file_id}'
        outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

        # Extract file name, size, and resolution
        file_name = media.file_name.lower() if media.file_name else "unknown"
        file_size = get_size(media.file_size)  # Convert size to readable format
        resolution = "Unknown Resolution"
        
        # Define resolution and codec keywords
        resolution_keywords = ["360p", "480p", "720p", "576p", "1080p", "2160p", "4k"]
        codec_keywords = ["hevc", "x265", "×265", "hdrip", "dvd rip", "predvd", "hd rip", "dvdrip", "pre dvd"]

        found_resolutions = []
        found_codecs = []

        # Check for resolution keywords in the file name
        for res in resolution_keywords:
            if res in file_name:
                found_resolutions.append(res)

        # Check for codec keywords in the file name
        for codec in codec_keywords:
            if codec in file_name:
                found_codecs.append(codec)

        # Combine resolution and codec if both are found
        if found_resolutions and found_codecs:
            resolution = " ".join(found_resolutions + found_codecs).capitalize()
        elif found_resolutions:
            resolution = " ".join(found_resolutions).capitalize()
        elif found_codecs:
            resolution = " ".join(found_codecs).capitalize()

        # Prepare the file data
        file_data = {
            "id": outstr,
            "resolution": resolution,
            "size": file_size
        }

        # Debugging logs
        print("File Data:", file_data)

        # Check if the movies_no already exists
        existing_movie = await db.user_data.find_one(
            {"id": user_id, "files.movies_no": movies_no},
            {"files.$": 1}  # Fetch only the matched movie
        )

        print("Existing Movie:", existing_movie)  # Debugging log

        if existing_movie:
            # Update existing movie
            update_result = await db.user_data.update_one(
                {"id": user_id, "files.movies_no": movies_no},
                {"$addToSet": {"files.$.movie_id": file_data}}  # Add only if not already present
            )
            print("Update Result:", update_result.modified_count)  # Debugging log
        else:
            # Add a new movie entry
            movie_data = {
                "movies_no": movies_no,
                "movie_id": [file_data],
                "name": movie_name,
                "poster_url": poster,
                "year": release_year,
                "language": movie_language
            }

            update_result = await db.user_data.update_one(
                {"id": user_id},
                {"$push": {"files": movie_data}},  # Add new file
                upsert=True
            )
            print("Insert Result:", update_result.upserted_id)  # Debugging log

        # Notify target chat
        await bot.send_message(
            -1002443600521,
            f"Movie Updated:\n"
            f"Name: {movie_name}\n"
            f"Year: {release_year}\n"
            f"Language: {movie_language}\n"
            f"Resolution: {resolution}\n"
            f"Size: {file_size}\n"
            f"File ID: {outstr}"
        )

    except PyMongoError as db_error:
        # Handle database-specific errors
        await bot.send_message(message.chat.id, f"Database Error: {str(db_error)}")
    except Exception as e:
        # Handle all other errors
        await bot.send_message(message.chat.id, f"Error: {str(e)}")

@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    username = (await bot.get_me()).username
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')
    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("**ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ**")
    if message.has_protected_content and message.chat.id not in ADMINS:
        return await message.reply("okDa")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    file_id, ref = unpack_new_file_id((getattr(replied, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?Tech_VJ={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username
    if " " not in message.text:
        return await message.reply("Use correct format.\nExample /batch https://t.me/vj_botz/10 https://t.me/vj_botz/20.")
    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample /batch https://t.me/vj_botz/10 https://t.me/vj_botz/20.")
    cmd, first, last = links
    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')
    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int(("-100" + f_chat_id))

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    match = regex.match(last)
    if not match:
        return await message.reply('Invalid link')
    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id = int(("-100" + l_chat_id))

    if f_chat_id != l_chat_id:
        return await message.reply("Chat ids not matched.")
    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    sts = await message.reply("**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ ғᴏʀ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ**.\n**ᴛʜɪs ᴍᴀʏ ᴛᴀᴋᴇ ᴛɪᴍᴇ ᴅᴇᴘᴇɴᴅɪɴɢ ᴜᴘᴏɴ ɴᴜᴍʙᴇʀ ᴏғ ᴍᴇssᴀɢᴇs**")

    FRMT = "**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ...**\n**ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs:** {total}\n**ᴅᴏɴᴇ:** {current}\n**ʀᴇᴍᴀɪɴɪɴɢ:** {rem}\n**sᴛᴀᴛᴜs:** {sts}"

    outlist = []

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

    # file store without db channel
    og_msg = 0
    tot = 0
    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if msg.empty or msg.service:
            continue
        if not msg.media:
            # only media messages supported.
            continue
        try:
            file_type = msg.media
            file = getattr(msg, file_type.value)
            caption = getattr(msg, 'caption', '')
            if caption:
                caption = caption.html
            if file:
                file = {
                    "file_id": file.file_id,
                    "caption": caption,
                    "title": getattr(file, "file_name", ""),
                    "size": file.file_size,
                    "protect": cmd.lower().strip() == "/pbatch",
                }

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

                og_msg +=1
                outlist.append(file)
        except:
            pass
        if not og_msg % 20:
            try:
                await sts.edit(FRMT.format(total=l_msg_id-f_msg_id, current=tot, rem=((l_msg_id-f_msg_id) - tot), sts="Saving Messages"))
            except:
                pass
    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)
    post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json", caption="⚠️Generated for filestore.")
    os.remove(f"batchmode_{message.from_user.id}.json")
    file_id, ref = unpack_new_file_id(post.document.file_id)
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?Tech_VJ=BATCH-{file_id}"
    else:
        share_link = f"https://t.me/{username}?start=BATCH-{file_id}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\nContains `{og_msg}` files.\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\nContains `{og_msg}` files.\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        
# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

