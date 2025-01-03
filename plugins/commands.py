import os
import logging
import random
import asyncio
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from plugins.database import get_file_details
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

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        if not BOT_RUN and message.from_user.id not in ADMINS:
            await message.reply(
                'The bot is still under development. It will be officially released in January or February 2025.\n\n'
                'Currently, this is made public only for introduction purposes, but it is not yet ready for use.'
            )
            return

        try:
            username = (await client.get_me()).username
        except Exception as e:
            await message.reply(f"Error fetching bot username: {str(e)}")
            return

        try:
            if not await db.is_user_exist(message.from_user.id):
                await db.add_user(message.from_user.id, message.from_user.first_name)
                await client.send_message(
                    LOG_CHANNEL,
                    script.LOG_TEXT.format(message.from_user.id, message.from_user.mention)
                )
        except Exception as e:
            await message.reply(f"Error checking/adding user: {str(e)}")
            return

        if len(message.command) != 2:
            try:
                buttons = [
                    [InlineKeyboardButton('💝 Subscribe My YouTube Channel', url='https://youtube.com/@Tech_VJ')],
                    [
                        InlineKeyboardButton('🔍 Support Group', url='https://t.me/vj_bot_disscussion'),
                        InlineKeyboardButton('🤖 Update Channel', url='https://t.me/vj_botz')
                    ],
                    [
                        InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
                        InlineKeyboardButton('😊 About', callback_data='about')
                    ]
                ]
                if CLONE_MODE:
                    buttons.append([InlineKeyboardButton('🤖 Create Your Own Clone Bot', callback_data='clone')])
                reply_markup = InlineKeyboardMarkup(buttons)
                user_id = message.from_user.id
                txt = script.START_TXT
                ttxt = await translate_text(txt, user_id)
                await message.reply_photo(
                    photo=random.choice(PICS),
                    caption=ttxt,
                    reply_markup=reply_markup
                )
            except Exception as e:
                await message.reply(f"Error preparing start message: {str(e)}")
            return

        if AUTH_CHANNEL and not await is_subscribed(client, message):
            try:
                invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
            except ChatAdminRequired:
                logger.error("Make sure Bot is admin in Forcesub channel")
                return
            btn = [
                [
                    InlineKeyboardButton("❆ Join Our Channel ❆", url=invite_link.invite_link)
                ],[
                    InlineKeyboardButton('🤔 Why Iam Join🤔', callback_data='sinfo')
                ]
            ]
            if message.command[1] != "subscribe":
                try:
                    kk, file_id = message.command[1].split("_", 1)
                    btn.append([InlineKeyboardButton("↻ Try Again", callback_data=f"checksub#{kk}#{file_id}")])
                except (IndexError, ValueError):
                    btn.append([InlineKeyboardButton("↻ Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            await client.send_photo(
                chat_id=message.from_user.id,
                photo="https://telegra.ph/file/20b4aaaddb8aba646e53c.jpg",
                caption="**You are not in our channel given below so you don't get the movie file...\n\n"
                        "If you want the movie file, click on the '🍿Join Our Back-Up Channel🍿' button below and join our back-up channel, "
                        "then click on the '🔄 Try Again' button below...\n\n"
                        "Then you will get the movie files...**",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return

        data = message.command[1]
        try:
            pre, file_id, movies_no = data.text.split(" ", 1)  # Split the message into command and argument
        except ValueError:
            file_id = data
            pre = ""

        if data.split("-", 1)[0] == "verify":
            try:
                userid = data.split("-", 2)[1]
                token = data.split("-", 3)[2]
                if str(message.from_user.id) != str(userid):
                    return await message.reply_text(
                        text="<b>Invalid link or Expired link !</b>",
                        protect_content=True
                    )
                is_valid = await check_token(client, userid, token)
                if is_valid:
                    await message.reply_text(
                        text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\n"
                             "Now you have unlimited access for all files till today midnight.</b>",
                        protect_content=True
                    )
                    await verify_user(client, userid, token)
                else:
                    return await message.reply_text(
                        text="<b>Invalid link or Expired link !</b>",
                        protect_content=True
                    )
            except Exception as e:
                await message.reply_text(f"Error during verification: {str(e)}")
            return

        try:
            files_ = await get_file_details(file_id)           
        except Exception as e:
            await message.reply(f"Error fetching file details: {str(e)}")
            return

        if not files_:
            try:
                media_details = await db.user_data.find_one(
                    {"id": message.from_user.id, "files.movies_no": movies_no},
                    {"files.$": 1}  # Project only the matched file
                )
                if not media_details or "files" not in media_details:
                    await message.reply("Movie not found!")
                    return
                
                file_details = media_details["files"][0]
                poster_url = file_details.get("poster_url")
                movie_name = file_details.get("name")
                release_year = file_details.get("year")
                movie_language = file_details.get("language")
                caption = f"🎬 **{movie_name}**\n🗓 **Year:** {release_year}\n🌐 **Language:** {movie_language}"
                file_details_list = await get_file_details1(movies_no)
                words = ["360p", "480p", "720p", "576p", "1080p", "4k", "2160p", "hdrip", "dvd rip", "predvd", "hd rip", "dvdrip", "pre dvd", "HEVC", "X265", "x265", "×265"]
                buttons = []
                for file in file_details_list:
                    file_name = file.get("file_name", "").lower()
                    file_size = file.get("file_size", 0)
                    file_id = file.get("file_id", "")
                    quality = next((word for word in words if word in file_name), "Unknown")
                    button_text = f"{quality.upper()} ({file_size // 1024 ** 2} MB)"
                    buttons.append(InlineKeyboardButton(button_text, callback_data=f"get_movie_{file_id}"))
                if poster_url:
                    await client.send_photo(
                        chat_id=message.from_user.id,
                        photo=poster_url,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup([buttons]),
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                else:
                    await message.reply("Poster URL not available!")
            except Exception as e:
                await message.reply(f"Error processing file details: {str(e)}")
            return

        try:
            user_id = message.from_user.id
            files = files_[0]
            title = files.file_name
            size = get_size(files.file_size)
            f_caption = files.file_name
            msuid = files.caption 
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title if title else '',
                        file_size=size if size else '',
                        file_caption=f_caption if f_caption else ''
                    )
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
            if not f_caption:
                f_caption = f"{files.file_name}"
            if db.user_data[msuid]["shortner-type"] == "verify" and db.user_data[msuid]["shortner"] and user_id not in db.user_data[msuid]["premium-users"]:
                if not await check_verification(client, message.from_user.id) and VERIFY_MODE:
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
                    x = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                        protect_content=True if pre == 'filep' else False,
                    )
                except Exception as e:
                    await message.reply(f"Error sending cached media: {str(e)}")
                    return
                
                db.user_data[user_id]["files_taken"] += 1
                
                if STREAM_MODE:
                    try:
                        g = await x.reply_text(
                            text=f"**• To open get generate stream link click below**",
                            quote=True,
                            disable_web_page_preview=True,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton('🚀 Fast Download / Watch Online📽️', callback_data=f'generate_stream_link:{file_id}')
                                    ]
                                ]
                            )
                        )
                        return
                    except Exception as e:
                        await message.reply(f"Error sending stream link: {str(e)}")
        except Exception as e:
            await message.reply(f"Error: {str(e)}")
        
    except Exception as e:
        await message.reply(f"Unexpected error: {str(e)}")


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if not BOT_RUN and query.from_user.id not in ADMINS:  # Corrected `callback_query` to `query`
        await query.answer(
            text='Bot is under maintenance.',
            show_alert=True  # Show as an alert instead of a toast
        )
        return
    if query.data == "close_data":
        await query.message.delete()
    
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
    
            

