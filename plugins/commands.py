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
from utils import verify_user, check_token, check_verification, get_token
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

async def translate_text(txt, user_id): 
    dest_lang = 'kn'  # Default to English if not set
    if dest_lang == 'en':  # Skip translation if already English
        return txt
    try:
        translated = translator.translate(txt, dest=dest_lang)
        return translated.text
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

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
    username = (await client.get_me()).username
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    if not await db.user_data.find_one({"id": message.from_user.id}):
        user_data = {
            "id": message.from_user.id,
            "bot_lang": 'en',
            "file_stored": 0,
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
        await db.user_data.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('ðŸ’â€â™€ï¸ Êœá´‡ÊŸá´˜', callback_data='help'),
            InlineKeyboardButton('ðŸ˜Š á´€Ê™á´á´œá´›', callback_data='about'),
            InlineKeyboardButton('âš™ Bot settings', callback_data='settings')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('ðŸ¤– á´„Ê€á´‡á´€á´›á´‡ Êá´á´œÊ€ á´á´¡É´ á´„ÊŸá´É´á´‡ Ê™á´á´›', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        me2 = (await client.get_me()).mention
        txt = script.START_TXT.format(message.from_user.mention, me2)
        ttxt = await translate_text(txt, message.from_user.id) 
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=ttxt,
            reply_markup=reply_markup
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
    elif data.split("-", 1)[0] == "BATCH":
        try:
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
        except Exception as e:
            return await message.reply_text(f"**Error - {e}**")
        sts = await message.reply("**ðŸ”º á´˜ÊŸá´‡á´€sá´‡ á´¡á´€Éªá´›**")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs            
        filesarr = []
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                if STREAM_MODE == True:
                    # Create the inline keyboard button with callback_data
                    user_id = message.from_user.id
                    username =  message.from_user.mention 

                    log_msg = await client.send_cached_media(
                        chat_id=LOG_CHANNEL,
                        file_id=msg.get("file_id"),
                    )
                    fileName = {quote_plus(get_name(log_msg))}
                    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
 
                    await log_msg.reply_text(
                        text=f"â€¢â€¢ ÊŸÉªÉ´á´‹ É¢á´‡É´á´‡Ê€á´€á´›á´‡á´… êœ°á´Ê€ Éªá´… #{user_id} \nâ€¢â€¢ á´œêœ±á´‡Ê€É´á´€á´á´‡ : {username} \n\nâ€¢â€¢ á–´áŽ¥á’ªá—´ Ná—©á—°á—´ : {fileName}",
                        quote=True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ðŸš€ Fast Download ðŸš€", url=download),  # we download Link
                                                            InlineKeyboardButton('ðŸ–¥ï¸ Watch online ðŸ–¥ï¸', url=stream)]])  # web stream Link
                    )
                if STREAM_MODE == True:
                    button = [[
                        InlineKeyboardButton("ðŸš€ Fast Download ðŸš€", url=download),  # we download Link
                        InlineKeyboardButton('ðŸ–¥ï¸ Watch online ðŸ–¥ï¸', url=stream)
                    ],[
                        InlineKeyboardButton("â€¢ á´¡á´€á´›á´„Êœ ÉªÉ´ á´¡á´‡Ê™ á´€á´˜á´˜ â€¢", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup=InlineKeyboardMarkup(button)
                else:
                    reply_markup = None
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=reply_markup
                )
                filesarr.append(msg)           
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(button)
                )
                filesarr.append(msg)
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        if AUTO_DELETE_MODE == True:
            k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>â—ï¸â—ï¸â—ï¸IMPORTANTâ—ï¸ï¸â—ï¸â—ï¸</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> ðŸ«¥ <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
            await asyncio.sleep(AUTO_DELETE_TIME)
            for x in filesarr:
                try:
                    await x.delete()
                except:
                    pass
            await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        return  




                               
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
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file.file_name.split()))
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
                    text=f"**â€¢â€¢ Êá´á´œ á´„á´€É´ É¢á´‡É´á´‡Ê€á´€á´›á´‡ á´É´ÊŸÉªÉ´á´‡ sá´›Ê€á´‡á´€á´ ÊŸÉªÉ´á´‹ á´Ò“ Êá´á´œÊ€ Ò“ÉªÊŸá´‡ á´€É´á´… á´€ÊŸsá´ Ò“á´€sá´› á´…á´á´¡É´ÊŸá´á´€á´… ÊŸÉªÉ´á´‹ Ò“á´Ê€ Êá´á´œÊ€ Ò“ÉªÊŸá´‡ á´„ÊŸÉªá´„á´‹ÉªÉ´É¢ á´É´ Ê™á´‡ÊŸá´á´¡ Ê™á´œá´›á´›á´É´ ðŸ‘‡**",
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('ðŸš€ Fast Download / Watch OnlineðŸ–¥ï¸', callback_data=f'generate_stream_link:{file_id}')
                            ]
                        ]
                    )
                )
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>â—ï¸â—ï¸â—ï¸IMPORTANTâ—ï¸ï¸â—ï¸â—ï¸</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> ðŸ«¥ <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
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
    user_id  = message.from_user.id 
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.file_name
    msuid = files.caption 
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    if db.user_data[msuid] ["shortner-type"] == "verify" and db.user_data[msuid] ["shortner"] and user_id not in db.user_data[msuid] ["premium-users"] :
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
        db.user_data[user_id]["files_taken"] += 1
        if STREAM_MODE == True:
            g = await x.reply_text(
                text=f"**â€¢â€¢ Êá´á´œ á´„á´€É´ É¢á´‡É´á´‡Ê€á´€á´›á´‡ á´É´ÊŸÉªÉ´á´‡ sá´›Ê€á´‡á´€á´ ÊŸÉªÉ´á´‹ á´Ò“ Êá´á´œÊ€ Ò“ÉªÊŸá´‡ á´€É´á´… á´€ÊŸsá´ Ò“á´€sá´› á´…á´á´¡É´ÊŸá´á´€á´… ÊŸÉªÉ´á´‹ Ò“á´Ê€ Êá´á´œÊ€ Ò“ÉªÊŸá´‡ á´„ÊŸÉªá´„á´‹ÉªÉ´É¢ á´É´ Ê™á´‡ÊŸá´á´¡ Ê™á´œá´›á´›á´É´ ðŸ‘‡**",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('ðŸš€ Fast Download / Watch OnlineðŸ–¥ï¸', callback_data=f'generate_stream_link:{file_id}')
                        ]
                    ]
                )
            )
        if AUTO_DELETE_MODE == True:
            k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>â—ï¸â—ï¸â—ï¸IMPORTANTâ—ï¸ï¸â—ï¸â—ï¸</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> ðŸ«¥ <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await x.delete()
                except:
                    pass
            await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")       
        


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('ðŸ”’ CÊŸá´sá´‡', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('ðŸ’â€â™€ï¸ Êœá´‡ÊŸá´˜', callback_data='help'),
            InlineKeyboardButton('ðŸ˜Š á´€Ê™á´á´œá´›', callback_data='about'),
            InlineKeyboardButton('âš™ Bot settings', callback_data='settings')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        txt = script.START_TXT.format(query.from_user.id)
        ttxt = await translate_text(txt, user_id) 
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('ðŸ”’ CÊŸá´sá´‡', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        user_id = query.from_user.id 
        txt = script.HELP_TXT
        ttxt = await translate_text(txt, user_id)    
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  

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

elif query.data == "settings":
        buttons = [[
            InlineKeyboardButton('Bot Language', callback_data='lang'),
            InlineKeyboardButton('Shortner', callback_data='short'),
            InlineKeyboardButton('Force Subscribe (fsub)', callback_data='fsub')
        ],[
            InlineKeyboardButton('File Access', callback_data='fileaccess'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
        ],[
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='start'),
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        user_id = query.from_user.id 
        txt = script.SET_TXT
        ttxt = await translate_text(txt, user_id)    
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  




    elif query.data == "lang":
        buttons = [[
            InlineKeyboardButton('à²•à²¨à³à²¨à²¡, callback_data='kan')
        ],[
            InlineKeyboardButton('English', callback_data='eng'),
            InlineKeyboardButton('Telugu, callback_data='tel')
        ],[
            InlineKeyboardButton('Tamil', callback_data='tam'),
            InlineKeyboardButton('Malayalam', callback_data='mal'),
            InlineKeyboardButton('Hindi', callback_data='hin')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='settings'),
            InlineKeyboardButton('â–¶ï¸', callback_data='lang1')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        user_id = query.from_user.id 
        txt = script.LANG_TXT
        ttxt = await translate_text(txt, user_id)    
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )     



elif query.data == "lang1":
        buttons = [[
            InlineKeyboardButton('Bot Language, callback_data='lang'),
            InlineKeyboardButton('Shortner', callback_data='short'),
            InlineKeyboardButton('Force Subscribe (fsub)', callback_data='fsub')
        ],[
            InlineKeyboardButton('File Access', callback_data='file-access'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
        ],[
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start'),
            InlineKeyboardButton('Há´á´á´‡', callback_data='start')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='lang'),
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        user_id = query.from_user.id 
        txt = script.LANG_TXT
        ttxt = await translate_text(txt, user_id)    
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )       
        

elif query.data == "short":
        buttons = [[
            InlineKeyboardButton('âœ”', callback_data='short_t'),
            InlineKeyboardButton('âŒ', callback_data='short_f')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='settings')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.SHORT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
        
    
elif query.data == "short_f":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='short')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.SHORT_F_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )            
        
        
elif query.data == "short_t":
        buttons = [[
            InlineKeyboardButton('Verify', callback_data='verify_t'),
            InlineKeyboardButton('Link Shortner', callback_data='l_short')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='short')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.SHORT_T_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
        
elif query.data == "link_short":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='short_t')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                
        
        
elif query.data == "verify_t":
        buttons = [[
            InlineKeyboardButton('Daily', callback_data='d_verify'),
            InlineKeyboardButton('Per Hours', callback_data='h_verify'),
            InlineKeyboardButton('Per Files', callback_data='f_verify')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='short_t')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
        
        
elif query.data == "d_verify":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='verify_t')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
        
        
elif query.data == "h_verify":
        buttons = [[
            InlineKeyboardButton('3ï¸âƒ£', callback_data='h_verify3'),
            InlineKeyboardButton('6ï¸âƒ£', callback_data='h_verify6'),
            InlineKeyboardButton('1ï¸âƒ£2ï¸âƒ£', callback_data='h_verify12'),
            InlineKeyboardButton('2ï¸âƒ£4ï¸âƒ£', callback_data='h_verify24')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='short_t')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                
        
elif query.data == "h_verify3":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='h_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "h_verify6":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='h_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "h_verify12":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='h_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "h_verify24":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='h_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                
        
        
elif query.data == "f_verify":
        buttons = [[
            InlineKeyboardButton('3ï¸âƒ£', callback_data='f_verify3'),
            InlineKeyboardButton('5ï¸âƒ£', callback_data='f_verify5'),
            InlineKeyboardButton('8ï¸âƒ£', callback_data='f_verify8'),
            InlineKeyboardButton('1ï¸âƒ£0ï¸âƒ£', callback_data='f_verify10')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='short_t')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )


elif query.data == "f_verify3":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='f_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "f_verify5":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='f_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "f_verify8":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='f_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "f_verify10":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='f_verify')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                             
        
        
  elif query.data == "file_access":
        buttons = [[
            InlineKeyboardButton('âœ”, callback_data='file_access_t'),
            InlineKeyboardButton('âŒ', callback_data='file_access_f')
        ],[
            InlineKeyboardButton('â—€ï¸', callback_data='short_t')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                      

        
elif query.data == "file_access_t":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='verify_t')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


elif query.data == "file_access_f":
        buttons = [[       
            InlineKeyboardButton('â—€ï¸', callback_data='verify_t')
            InlineKeyboardButton('âŒ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=ttxt,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )    

