import os
import logging
import random
import asyncio
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from plugins.database import get_file_details, get_file_details1
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from utils import verify_user, check_token, check_verification, get_token, is_subscribed, translate_text
from config import *
import re
from googletrans import Translator
import json
import base64
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size
import datetime 
import pytz 
logger = logging.getLogger(__name__)

BATCH_FILES = {}
translator = Translator()

async def dati():
    try:
        kolkata_timezone = pytz.timezone('Asia/Kolkata')
        kolkata_time = datetime.datetime.now(kolkata_timezone)
        formatted_time = kolkata_time.strftime('%d/%m/%Y %H:%M:%S')  
        return formatted_time 
    except Exception as e:
        # Handle exceptions appropriately, e.g., logging or raising
        raise RuntimeError(f"Error in dati function: {str(e)}")

@Client.on_message(filters.command("dbud") & filters.incoming)
async def dbud(client, message):
    try:
        if not await db.user_data.find_one({"id": message.from_user.id}):
            user_data = {
                "id": message.from_user.id,
                "bot-lang": 'en',
                "file-stored": 0,
                "files": [],
                "premium-users": [],
                "shortner": False,
                "shortner-type": None,
                "verify-type": None,
                "verify-hrs": None,
                "verify-files": 10,
                "verify-logs-c": None,
                "shotner-site": None,
                "shotner-api": None,
                "fsub": None,
                "file-access": True,
                "joined": await dati()
            }    
            await db.user_data.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
        txt = await db.user_data.find_one({"id": message.from_user.id})
        await message.reply(f"{txt}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")


def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])



@Client.on_message(filters.command("tr") & filters.incoming)
async def tr(client, message):
    try:
        user_id = message.from_user.id 
        txt = script.START_TXT.format(message.from_user.mention)
        ttxt = await translate_text(txt, user_id) 
        await message.reply(f"{ttxt}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not BOT_RUN and message.from_user.id not in ADMINS:
        await message.reply(f'The bot is still under development. It will be officially released in January or February 2025.\n\nCurrently, this is made public only for introduction purposes, but it is not yet ready for use.')
        return
    username = (await client.get_me()).username
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    if not await db.user_data.find_one({"id": message.from_user.id}):
        user_data = {
            "id": message.from_user.id,
            "bot_lang": 'en',
            "movie_no": 0,
            "files_taken": 0,
            "files": [],
            "premium-users": [],
            "shortner-type": None,
            "verify-type": None,
            "verify-hrs": 'Daily',
            "verify-files": 10,
            "verify-logs-c": None,
            "shotner-site": None,
            "shotner-api": None,
            "fsub": None,
            "file-access": False,
            "joined": await dati()
        }
        await db.user_data.update_one(
            {"id": user_data["id"]}, {"$set": user_data}, upsert=True
        )
        return
    
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )

          
    

    elif data.split("-", 1)[0] == "8112":
        try:
            # Extract movie number
            movies_no = data.split("-", 1)[1].strip()
            
            # Fetch movie details from the database
            media_details = await db.user_data.find_one(
                {"id": message.from_user.id, "files.movies_no": movies_no},
                {"files.$": 1}  # Project only the matched file
            )
            
            if not media_details or "files" not in media_details:
                await message.reply("Movie not found!")
                return
            
            # Extract file details
            file_details = media_details["files"][0]
            poster_url = file_details.get("poster_url", "").replace("\n", "").strip()
            movie_name = file_details.get("name", "Unknown Movie")
            release_year = file_details.get("year", "Unknown Year")
            movie_language = file_details.get("language", "Unknown Language")
            movie_ids = file_details.get("movie_id", [])
            
            if not movie_ids:
                await message.reply("No file IDs found for this movie!")
                return
            
            # Prepare caption
            caption = (
                f"🎬 **{movie_name}**\n"
                f"🗓 **Year:** {release_year}\n"
                f"🌐 **Language:** {movie_language}"
            )
            
            # Prepare buttons for each file
            buttons = []
            for movie_id in movie_ids:
                if isinstance(movie_id, dict):
                    file_id = movie_id.get("id", "Unknown ID")
                    resolution_text = movie_id.get("resolution", "Unknown Resolution")
                    file_size = movie_id.get("size", "Unknown Size")
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                f"{resolution_text} - {file_size}",
                                callback_data=f"file_{file_id}"
                            )
                        ]
                    )
                
            
            # Send poster with buttons
            if buttons:
                reply_markup = InlineKeyboardMarkup(buttons)
                await message.reply_photo(
                    photo=poster_url,
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                await message.reply("No file details available to generate buttons.")
        
        except Exception as e:
            await message.reply(f"Error: {e}")
            # Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
            btn = [[
                InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
            ],[
                InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
            ]]
            await message.reply_text(
                text="<b>You are not verified !\nKindly verify to continue !</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,  
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = '@VJ_Botz  ' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file.file_name.split()))
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            
            await msg.edit_caption(f_caption)
            if STREAM_MODE == True:
                g = await msg.reply_text(
                    text=f"**•• ʏᴏᴜ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ᴏɴʟɪɴᴇ sᴛʀᴇᴀᴍ ʟɪɴᴋ ᴏғ ʏᴏᴜʀ ғɪʟᴇ ᴀɴᴅ ᴀʟsᴏ ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ғᴏʀ ʏᴏᴜʀ ғɪʟᴇ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ 👇**",
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}')
                            ]
                        ]
                    )
                )
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
                await asyncio.sleep(AUTO_DELETE_TIME)
                try:
                    await msg.delete()
                except:
                    pass
                await g.delete()
                await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
            return
        except:
            pass
        return await message.reply('No such file exist.')

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
        btn = [[
            InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
        ],[
            InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
        ]]
        await message.reply_text(
            text="<b>You are not verified !\nKindly verify to continue !</b>",
            protect_content=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    x = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
    )
    if STREAM_MODE == True:
        g = await x.reply_text(
            text=f"**•• ʏᴏᴜ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ᴏɴʟɪɴᴇ sᴛʀᴇᴀᴍ ʟɪɴᴋ ᴏғ ʏᴏᴜʀ ғɪʟᴇ ᴀɴᴅ ᴀʟsᴏ ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ғᴏʀ ʏᴏᴜʀ ғɪʟᴇ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ 👇**",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}')
                    ]
                ]
            )
        )
    if AUTO_DELETE_MODE == True:
        k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
        await asyncio.sleep(AUTO_DELETE_TIME)
        try:
            await x.delete()
        except:
            pass
        await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")       


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if not BOT_RUN and query.from_user.id not in ADMINS:  # Check if bot is under maintenance
        await query.answer(
            text="Bot is under maintenance.",
            show_alert=True  # Show as an alert instead of a toast
        )
        return

    if query.data == "close_data":  # Handle 'close_data' action
        await query.message.delete()
        return

    elif query.data.startswith("file_"):  # Handle 'file_' action
        try:
            file_id = query.data.split("_")[1]  # Extract file ID from callback data
            await query.answer(
                url=f"https://telegram.me/{temp.U_NAME}?start={file_id}"  # Respond with URL
            )
        except Exception as e:
            # Handle any exceptions that occur
            await query.answer(
                text=f"{e}",
                show_alert=True  # Show as an alert to notify the user
            )
            # Optionally, log the error for debugging
            print(f"Error in file_ handler: {e}")
            return
    
    elif query.data.startswith("generate_stream_link"):
        _, file_id = query.data.split(":")
        try:
            user_id = query.from_user.id
            username =  query.from_user.mention 
            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
            )
            fileName = {quote_plus(get_name(log_msg))}
            stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            xo = await query.message.reply_text(f'ðŸ”')
            await asyncio.sleep(1)
            await xo.delete()
            button = [[
                InlineKeyboardButton("ðŸš€ Fast Download ðŸš€", url=download),  # we download Link
                InlineKeyboardButton('ðŸ–¥ï¸ Watch online ðŸ–¥ï¸', url=stream)
            ]]
            reply_markup=InlineKeyboardMarkup(button)
            await log_msg.reply_text(
                text=f"â€¢â€¢ ÊŸÉªÉ´á´‹ É¢á´‡É´á´‡Ê€á´€á´›á´‡á´… êœ°á´Ê€ Éªá´… #{user_id} \nâ€¢â€¢ á´œêœ±á´‡Ê€É´á´€á´á´‡ : {username} \n\nâ€¢â€¢ á–´áŽ¥á’ªá—´ Ná—©á—°á—´ : {fileName}",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
            button = [[
                InlineKeyboardButton("ðŸš€ Fast Download ðŸš€", url=download),  # we download Link
                InlineKeyboardButton('ðŸ–¥ï¸ Watch online ðŸ–¥ï¸', url=stream)
            ],[
                InlineKeyboardButton("â€¢ á´¡á´€á´›á´„Êœ ÉªÉ´ á´¡á´‡Ê™ á´€á´˜á´˜ â€¢", web_app=WebAppInfo(url=stream))
            ]]
            reply_markup=InlineKeyboardMarkup(button)
            await query.message.reply_text(
                text="â€¢â€¢ ÊŸÉªÉ´á´‹ É¢á´‡É´á´‡Ê€á´€á´›á´‡á´… â˜ ï¸Žâš”",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"â˜£something went wrong\n\n{e}", show_alert=True)
            return
    
            

