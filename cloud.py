#FayasNoushad
#ImJanindu
#Me

import os
import pixeldrain
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import requests
import sys
import time
import logging
import aiohttp
import asyncio
from random import randint

Cloudsy = Client(
    "Cloudsy-Bot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

DOWNLOAD = "./"


def time_data(start_time):
    end = time.time()
    now = end - start_time
    now_time = now
    day = now_time // (24 * 3600)
    now_time = now_time % (24 * 3600)
    hour = now_time // 3600
    now_time %= 3600
    minutes = now_time // 60
    now_time %= 60
    seconds = now_time
    if(day!=0):
        return "%dd %dh %dm %ds" % (day, hour, minutes, seconds)
    if(hour!=0):
        return "%dh %dm %ds" % (hour, minutes, seconds)
    else:
        return "%dm %ds" % (minutes, seconds)


async def progress(current, total,up_msg, message, start_time):

    try:
        await message.edit(
            text = f"{up_msg} {current * 100 / total:.1f}% in {time_data(start_time)}"
                )
    except:
        pass

def uploadFile(file: str):
    server = requests.get("https://api.gofile.io/getServer").json()["data"]["server"]
    response = requests.post(
        url=f"https://{server}.gofile.io/uploadFile",
        data={
            "token": None,
            "folderId": None,
            "description": None,
            "password": None,
            "tags": None,
            "expire": None
        },
        files={"upload_file": open(file, "rb")}
    ).json()
    if response["status"] == "ok":
        return response["data"]
    elif "error-" in response["status"]:
        error = response["status"].split("-")[1]
        raise Exception(error)



@Cloudsy.on_message(filters.private & filters.command("start"))
async def start(bot, update):
    await update.reply_text(
        text=f"Hello {update.from_user.mention}, 👋\n\nJust send me a media & I'll upload it to the cloud.\n\nMade with ❤️ by @Sybots",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📨 Updates", url="https://t.me/sybots"),
                 InlineKeyboardButton("🗂 Source", url="https://github.com/reindears/cloudsy")]
            ]
        )
    )


@Cloudsy.on_callback_query(filters.regex(r"pixel"))
async def media_filghter(bot, data: CallbackQuery):
    
    logs = []
    message = await data.message.edit_text(
        text="Processing file"
    )
    
    try:
        # download
        try:
            await message.edit_text(
                text="Downloading file to server",
                disable_web_page_preview=True
            )
        except:
            pass
        media = await data.message.reply_to_message.download()
        logs.append("Download Successfully")
        
        # upload
        try:
            await message.edit_text(
                text="Uploading to Pixeldrain",
                disable_web_page_preview=True
            )
        except:
            pass
        response = pixeldrain.upload_file(media)
        
        try:
            os.remove(media)
        except:
            pass
        try:
            await message.edit_text(
                text="Uploaded Successfully",
                disable_web_page_preview=True
            )
        except:
            pass
        logs.append("Upload Successfully")
        
        # after upload
        if response["success"]:
            logs.append("Success is True")
            data = pixeldrain.info(response["id"])
        else:
            logs.append("Success is False")
            value = response["value"]
            error = response["message"]
            await message.edit_text(
                text=f"**Error {value}:-** `{error}`",
                disable_web_page_preview=True
            )
            return
    except Exception as error:
        await message.edit_text(
            text=f"Error :- `{error}`"+"\n\n"+'\n'.join(logs),
            disable_web_page_preview=True
        )
        return
    
    # pixeldrain data
    text = f"**File Name:** `{data['name']}`" + "\n"
    text += f"**Download Page:** `https://pixeldrain.com/u/{data['id']}`" + "\n"
    text += f"**Direct Download Link:** `https://pixeldrain.com/api/file/{data['id']}`" + "\n"
    text += f"**Upload Date:** `{data['date_upload']}`" + "\n"
    text += f"**Last View Date:** `{data['date_last_view']}`" + "\n"
    text += f"**Size:** `{data['size']}`" + "\n"
    text += f"**Total Views:** `{data['views']}`" + "\n"
    text += f"**Bandwidth Used:** `{data['bandwidth_used']}`" + "\n"
    text += f"**Mime Type:** `{data['mime_type']}`"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Open Link",
                    url=f"https://pixeldrain.com/u/{data['id']}"
                ),
                InlineKeyboardButton(
                    text="Share Link",
                    url=f"https://telegram.me/share/url?url=https://pixeldrain.com/u/{data['id']}"
                )
            ]
        ]
    )
    
    await message.edit_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    
@Cloudsy.on_message(filters.private & filters.media)
async def medias(bot, update):
    await update.reply_text(
        "Choose a Cloud Server for Uploading",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("GoFile", callback_data="gofile"),
                 InlineKeyboardButton("Anonfiles", callback_data="anon"),
                 InlineKeyboardButton("Pixeldrain", callback_data="pixel")]
            ]
        ),
        quote=True
    )

@Cloudsy.on_callback_query(filters.regex(r"gofile"))
async def filterpix(bot, data: CallbackQuery):
    message = await data.message.edit_text(
        text="`Processing...`"
    )
    try:
        # download
        try:
            await message.edit_text(
                text="Downloading file to server",
                disable_web_page_preview=True
            )
        except:
            pass
        media = await data.message.reply_to_message.download()


        try:
            await message.edit_text(
                text="Uploading to Gofile",
                disable_web_page_preview=True
            )
        except:
            pass
        response = uploadFile(media)
        try:
            os.remove(media)
        except:
            pass
    except Exception as error:
        await message.edit_text(
            text=f"Error :- `{error}`",
            disable_web_page_preview=True
        )
        return
    text = f"**File Name:** `{response['fileName']}`" + "\n"
    text += f"**Download Page:** `{response['downloadPage']}`" + "\n"
    text += f"**Direct Download Link:** `{response['directLink']}`" + "\n"
    text += f"**Info:** `{response['info']}`"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Open Link", url=response['directLink']),
                InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={response['directLink']}")
            ]
        ]
    )
    await message.edit_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    
@Cloudsy.on_callback_query(filters.regex(r"anon"))
async def uplouhad(bot, data: CallbackQuery):
    m = await data.message.edit_text("Downloading file to server")
    now = time.time()
    sed = await bot.download_media(
                data.message.reply_to_message, DOWNLOAD,
          progress=progress,
          progress_args=(
            "ETA : ", 
            m,
            now
            )
        )
    try:
        files = {'file': open(sed, 'rb')}
        await m.edit("Uploading to Anonfiles")
        callapi = requests.post("https://api.anonfiles.com/upload", files=files)
        text = callapi.json()
        output = f"""
**File Name:** {text['data']['file']['metadata']['name']}
**File Size:** {text['data']['file']['metadata']['size']['readable']}
**Download Link:** `{text['data']['file']['url']['full']}`"""
        btn = InlineKeyboardMarkup(
                                [[InlineKeyboardButton("Open Url", url=f"{text['data']['file']['url']['full']}"),
                                  InlineKeyboardButton("Share Link", url=f"https://telegram.me/share/url?url={text['data']['file']['url']['full']}")
                                 ]])
        await m.edit(output, reply_markup=btn)
        os.remove(sed)
    except Exception:
        await m.edit("Process Failed, Maybe Time Out Due To Large File Size!")
        return


Cloudsy.run()
