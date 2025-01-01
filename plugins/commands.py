# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

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
import json
import datetime 
import pytz 
import base64
from telegraph import upload_file
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size
logger = logging.getLogger(__name__)

BATCH_FILES = {}
QUALITY_KEYWORDS = [
    "240p", "360p", "480p", "720p", "1080p", "2160p", 
    "1440p", "576p", "4k", "hevc", "x265", "×265"
]
from googletrans import Translator

# Initialize the Translator instance
translator = Translator()

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)

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
            await message.reply("updating")
            await db.user_data.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
        txt = await db.user_data.find_one({"id": message.from_user.id})
        await message.reply(f"{txt}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_message(filters.command("sd1") & filters.private)
async def check_saved_details1(client, message):
    try:
        media_details = db.user_data.find()
        response = ""
        async for document in media_details:
            response += str(document) + "\n"
        
        if response:
            await message.reply(response)
        else:
            await message.reply("No details found for this movie number.")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@Client.on_message(filters.command("sd") & filters.private)
async def check_saved_details(client, message):
    try:
        # Convert the cursor to a list (limit to 100 documents to avoid large results)
        media_details = await db.user_data.find_one({"movies_no": 591732965-3})
        if media_details:
            # Reply with the details as a string
            await message.reply(str(media_details))
        else:
            await message.reply("No details found for this movie number.")
    except Exception as e:
        # Send the error as a reply
        await message.reply(f"Error: {str(e)}")

@Client.on_message(filters.command("duud") & filters.user(ADMINS))
async def duud(client, message):
    try:
        user_id = message.from_user.id 
        await db.user_data.delete_many({"id": user_id})
    except Exception as e:
        await message.reply(str(e))
    
async def translate_text(txt, user_id): 
    dest_lang = 'kn'  # Default to Kannada
    if dest_lang == 'en':  # Skip translation if already English
        return txt
    try:
        translated = translator.translate(text=txt, dest=dest_lang)
        return translated.text
    except Exception as e:
        return f"Error: {str(e)}"

@Client.on_message(filters.command("tr") & filters.incoming)
async def tr(client, message):
    try:
        user_id = message.from_user.id  # Get user ID
        txt = script.START_TXT  # Assuming START_TXT is defined in the script
        ttxt = await translate_text(txt, user_id)  # Translate the text
        await message.reply_text(f"{ttxt}")  # Reply with the translated text
    except Exception as e:
        await message.reply_text(f"⚠️ Something went wrong\n\n{e}")


def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ0


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
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', callback_data='media_saver')
            ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')
            ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = message.from_user.id 
        txt = script.START_TXT 
        ttxt = await translate_text(txt, user_id)    
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=f'{ttxt}',
            reply_markup=reply_markup
        )
        return

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
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
        sts = await message.reply("**🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ**")
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
                        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                        quote=True,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                                                            InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]])  # web stream Link
                    )
                if STREAM_MODE == True:
                    button = [[
                        InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                        InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)
                    ],[
                        InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
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
            k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
            await asyncio.sleep(AUTO_DELETE_TIME)
            for x in filesarr:
                try:
                    await x.delete()
                except:
                    pass
            await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        return

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
        

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"])
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("<b>Shortener API updated successfully to</b> " + api)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    text = f"`/base_site (base_site)`\n\n<b>Current base site: None\n\n EX:</b> `/base_site shortnerdomain.com`\n\nIf You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if base_site == None:
            await update_user_info(user_id, {"base_site": base_site})
            return await m.reply("<b>Base Site updated successfully</b>")
            
        if not domain(base_site):
            return await m.reply(text=text, disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("<b>Base Site updated successfully</b>")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if not BOT_RUN and query.from_user.id not in ADMINS:  
        await query.answer(
            text='Bot is under maintenance.',
            show_alert=True
        )
        return
    
    if query.data == "close_data":
        await query.message.delete()

    elif query.data.startswith("engtxt_"):
        engtxt = query.data.split("_", 1)[1]
        await query.message.edit_text(
            text=f'{engtxt}',
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('English', callback_data=f'engtxt_{script.ABOUT_TXT}')
        ], [
            InlineKeyboardButton('◀️', callback_data='start'),
            InlineKeyboardButton('❌', callback_data='close_data')
        ]]
        await client.edit_message_media(
            chat_id=query.message.chat.id, 
            message_id=query.message.id, 
            media=InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id
        txt = script.ABOUT_TXT
        ttxt = await translate_text(txt, user_id)
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('English', callback_data=f'engtxt_{script.START_TXT}')
        ], [
            InlineKeyboardButton('🙋‍♀️ Help', callback_data='help'),
            InlineKeyboardButton('😊 About', callback_data='about'),
            InlineKeyboardButton('⚙️ Bot settings', callback_data='settings')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            chat_id=query.message.chat.id, 
            message_id=query.message.id, 
            media=InputMediaPhoto(random.choice(PICS))
        )
        txt = script.START_TXT.format(query.from_user.id)
        ttxt = await translate_text(txt, query.from_user.id)
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('English', callback_data=f'engtxt_{script.HELP_TXT}')
        ], [
            InlineKeyboardButton('◀️', callback_data='start'),
            InlineKeyboardButton('⚙️ Settings', callback_data='settings'),
            InlineKeyboardButton('❌', callback_data='close_data')
        ]]
        await client.edit_message_media(
            chat_id=query.message.chat.id, 
            message_id=query.message.id, 
            media=InputMediaPhoto(random.choice(PICS))
        )
        user_id = query.from_user.id
        txt = script.HELP_TXT
        ttxt = await translate_text(txt, user_id)
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f'{ttxt}',
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
            InlineKeyboardButton('User Premium', callback_data='u_premium'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
        ],[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start')
        ],[
            InlineKeyboardButton('◀️', callback_data='start'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  




    elif query.data == "lang":
        buttons = [[
            InlineKeyboardButton('ಕನ್ನಡ', callback_data='kan')
        ],[
            InlineKeyboardButton('English', callback_data='eng'),
            InlineKeyboardButton('Telugu', callback_data='tel')
        ],[
            InlineKeyboardButton('Tamil', callback_data='tam'),
            InlineKeyboardButton('Malayalam', callback_data='mal'),
            InlineKeyboardButton('Hindi', callback_data='hin')
        ],[
            InlineKeyboardButton('◀️', callback_data='settings'),
            InlineKeyboardButton('▶️', callback_data='lang1')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )     

    elif query.data == "lang1":
        buttons = [[
            InlineKeyboardButton('Bot Language', callback_data='lang'),
            InlineKeyboardButton('Shortner', callback_data='short'),
            InlineKeyboardButton('Force Subscribe (fsub)', callback_data='fsub')
        ],[
            InlineKeyboardButton('File Access', callback_data='file-access'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
        ],[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start')
        ],[
            InlineKeyboardButton('◀️', callback_data='lang'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )       
        

    elif query.data == "short":
        buttons = [[
            InlineKeyboardButton('✔', callback_data='short_t'),
            InlineKeyboardButton('❌', callback_data='short_f')
        ],[
            InlineKeyboardButton('◀️', callback_data='settings')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
        
    
    elif query.data == "short_f":
        db.update.user_data[query.from_user.id] ["shortner"] == False 
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='short'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )            
        
        
    elif query.data == "short_t":
        db.update.user_data[query.from_user.id]["shortner"] = True
        if (db.user_data[query.from_user.id].get("shortener-site") is None or 
            db.user_data[query.from_user.id].get("shortener-api") is None):
                ssl = await client.ask(message.chat.id, "**Send your shortener site link**")
                sapi = await client.ask(message.chat.id, "**Send your shortener API**")
                db.update.user_data[query.from_user.id]["shortener-site"] = ssl
                db.update.user_data[query.from_user.id]["shortener-api"] = sapi
                return
        buttons = [[
            InlineKeyboardButton('Verify', callback_data='verify_t'),
            InlineKeyboardButton('Link Shortner', callback_data='l_short')
        ],[
            InlineKeyboardButton('◀️', callback_data='short')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
        
    elif query.data == "l_short":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='short_t'),
            InlineKeyboardButton('❌', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.L_SHORT_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                
               
        
        
    elif query.data == "verify_t":
        buttons = [[
            InlineKeyboardButton('Daily', callback_data='d_verify'),
            InlineKeyboardButton('Per Hours', callback_data='h_verify'),
            InlineKeyboardButton('Per Files', callback_data='f_verify')
        ],[
            InlineKeyboardButton('◀️', callback_data='short_t')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.VERIFY_T__TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
        
        
    elif query.data == "d_verify":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='verify_t'),
            InlineKeyboardButton('❌', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.D_VERIFY_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
        
        
    elif query.data == "h_verify":
        buttons = [[
            InlineKeyboardButton('3️⃣', callback_data='h_verify3'),
            InlineKeyboardButton('6️⃣', callback_data='h_verify6'),
            InlineKeyboardButton('1️⃣2️⃣', callback_data='h_verify12'),
            InlineKeyboardButton('2️⃣4️⃣', callback_data='h_verify24')
        ],[
            InlineKeyboardButton('◀️', callback_data='short_t')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.H_VERIFY_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                
        
    elif query.data == "h_verify3":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='h_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


    elif query.data == "h_verify6":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='h_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


    elif query.data == "h_verify12":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='h_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


    elif query.data == "h_verify24":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='h_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                
        
        
    elif query.data == "f_verify":
        buttons = [[
            InlineKeyboardButton('3️⃣', callback_data='f_verify3'),
            InlineKeyboardButton('5️⃣', callback_data='f_verify5'),
            InlineKeyboardButton('8️⃣', callback_data='f_verify8'),
            InlineKeyboardButton('1️⃣0️⃣', callback_data='f_verify10')
        ],[
            InlineKeyboardButton('◀️', callback_data='short_t')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        


    elif query.data == "f_verify3":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='f_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )           


    elif query.data == "f_verify5":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='f_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


    elif query.data == "f_verify8":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='f_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


    elif query.data == "f_verify10":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='f_verify'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                             
        
    elif query.data == "file_access":
        buttons = [[
            InlineKeyboardButton('✔', callback_data='file_access_t'),
            InlineKeyboardButton('❌', callback_data='file_access_f')
        ],[
            InlineKeyboardButton('◀️', callback_data='short_t')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )                      

        
    elif query.data == "file_access_t":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='verify_t'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        


    elif query.data == "file_access_f":
        buttons = [[       
            InlineKeyboardButton('◀️', callback_data='verify_t'),
            InlineKeyboardButton('❌', callback_data='close_data')
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
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )    
        
    elif query.data == "vlc":
        buttons = [[       
            InlineKeyboardButton('✔', callback_data='vlcid'),
            InlineKeyboardButton('❌', callback_data='vlc_f')
       ],[
            InlineKeyboardButton('◀️', callback_data='verify_t'),
            InlineKeyboardButton('❌', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        user_id = query.from_user.id 
        txt = script.VLC_TXT
        ttxt = await translate_text(txt, user_id)    
        await query.message.edit_text(
            text=f'{ttxt}',
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "vlcid":
        
        if db.user_data[query.from_user.id] ["verify_log_c"] is None:
             vj = await client.ask(message.chat.id, "**Forward any message from your log channel**")
        else:
            buttons = [[
                InlineKeyboardButton('◀️', callback_data='verify_t'),
                InlineKeyboardButton('❌', callback_data='close_data')
            ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(buttons)
            user_id = query.from_user.id 
            txt = script.VLC_TXT
            ttxt = await translate_text(txt, user_id)    
            await query.message.edit_text(
                 text=f'{ttxt}',
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )                


    elif query.data == "media_saver":
        try:
            user_id = query.from_user.id

            # Get poster
            poster = await get_poster(client, query.message.chat.id)
            if not poster:
                return

            # Get media details
            movie_name = await get_text(client, query.message.chat.id, "Send the name of the media.")
            release_year = await get_year(client, query.message.chat.id)
            movie_language = await get_text(
                client, query.message.chat.id, 
                "Send the language(s) of the media (e.g., Kannada-English-Telugu)."
            )

            
            
            udb = await db.user_data.find_one({"id": query.from_user.id})
            current_movie_no = udb["movie_no"]
            new_movie_no = current_movie_no + 1
            movies_no = f"{query.from_user.id}-{new_movie_no}"
            movie_files = await collect_movie_files(client, query.from_user.id, movies_no)
            movie_data = {
                "movies_no": movies_no,
                "name": movie_name,
                "poster_url": poster,
                "year": release_year,
                "language": movie_language
            }
            await db.user_data.update_one(
                {"id": query.from_user.id},
                {"$set": {"movie_no": new_movie_no}},
                upsert=True
            )
            await db.files.update_one(
                {"id": movies_no},
                {"$set": movie_data},
                upsert=True
            )
            await client.send_message(-1002294034797, f"{user_id}-{movies_no}-{movie_name}-{poster}-{release_year}-{movie_language}")    
            

        except Exception as e:
            error_message = f"Error: {e}\nUser: {query.from_user.id}\nData: {query.data}"
            await client.send_message(-1002443600521, error_message)
            await client.send_message(query.message.chat.id, "An unexpected error occurred. Please try again.")

async def get_poster(client, chat_id):
    try:
        # Ask user for media
        t_msg = await client.ask(chat_id, "Now send me your photo or video under 5MB to get a media link.")
        path = await t_msg.download()

        # Upload the media
        image_url = await upload_image_requests(path, chat_id)
        if not image_url:
            await client.send_message(chat_id, "Failed to upload your file. Please try again.")
            return None
        return image_url
    except Exception as e:
        await client.send_message(chat_id, f"Error processing your file: {str(e)}")
        return None
        


        
async def get_text(client, chat_id, prompt):
    text_msg = await client.ask(chat_id, prompt)
    return text_msg.text.strip()

async def get_year(client, chat_id):
    while True:
        year_msg = await client.ask(chat_id, "Send the release year of the media (numeric).")
        if year_msg.text.isdigit():
            return int(year_msg.text)
        await client.send_message(chat_id, "Invalid year. Please send a numeric year.")

async def collect_movie_files(client, chat_id, movies_no):
    while True:
        media = await client.ask(chat_id, "Send the media file (or type 'Done' to finish).")
        if media.text and media.text.lower() == "done":
            await client.send_message(chat_id, "Media collection complete!")
            break
        if media.document or media.video:
            file_id = media.document.file_id if media.document else media.video.file_id
            caption = f"{movies_no}"  # Example caption, adjust as needed
            try:
                await client.send_document(
                    -1002400439772,  # Replace with your channel ID
                    document=file_id,
                    caption=caption
                )
            except Exception as e:
                await client.send_message(chat_id, f"Error uploading file: {str(e)}")
        else:
            await client.send_message(chat_id, "Invalid file. Please send a document or video.")

import aiohttp
import os

async def upload_image_requests(image_path, chat_id):
    upload_url = "https://envs.sh"
    try:
        # Check file size
        if os.path.getsize(image_path) > 5 * 1024 * 1024:  # 5 MB
            await client.send_message(chat_id, "File size exceeds the 5MB limit. Please try a smaller file.")
            return None

        # Asynchronous HTTP client
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as file:
                files = {'file': file}
                async with session.post(upload_url, data=files) as response:
                    if response.status == 200:
                        return await response.text()  # Return the uploaded file URL
                    else:
                        await client.send_message(chat_id, f"Upload failed with status code {response.status}.")
                        return None
    except Exception as e:
        await client.send_message(chat_id, f"Error uploading file: {str(e)}")
        return None
    finally:
        # Clean up the file
        if os.path.exists(image_path):
            os.remove(image_path)

