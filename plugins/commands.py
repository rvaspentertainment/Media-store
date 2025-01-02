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
    
            
