#    This file is part of the Youtube Notification  distribution.
#    Copyright (c) 2022 kaif_00z
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/kaif-00z/YoutubeNotificationBot/blob/main/License> .


from . import *
from .helper import *

LOGS.info("• Starting Bot... •")

try:
    bot.start(bot_token=BOT_TOKEN)
except Exception as exc:
    LOGS.info(str(exc))


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        f"Hi `{event.sender.first_name}`\nThis is A YouTube Notification Bot.\n I Notified You Wen Your Subscribed Youtubers Post A Video or Start A Live Streams",
        buttons=[
            [
                Button.url("SOURCE CODE", url="github.com/Kaif-00z/"),
                Button.url("DEVELOPER", url="t.me/kaif_00z"),
            ],
        ],
    )


@bot.on(events.NewMessage(incoming=True, pattern="/subsinfo"))
async def sub_info(event):
    if str(event.sender_id) != OWNER:
        return
    text = "**Subscribed Channels**\n\n"
    for ch in get_channels():
        try:
            info = await channel_info(ch["id"])
            default_name = info["items"][0]["snippet"]["title"]
        except BaseException:
            default_name = "Unknown"
        display_name = ch["custom_name"] or default_name
        text += f"`• {display_name}` (id: `{ch['id']}`"
        if ch["custom_name"]:
            text += " • custom"
        text += ")\n"
    if not get_channels():
        text += "_No channels stored._"
    await event.reply(text)


# Owner-only: add a channel (with optional custom name)
@bot.on(events.NewMessage(pattern=r"/addchannel\s+(.+)"))
async def add_channel_cmd(event):
    if str(event.sender_id) != OWNER:
        return
    args = event.pattern_match.group(1).strip()
    parts = args.split()
    channel_id = parts[0]
    custom_name = " ".join(parts[1:]) or None
    # Validate via API
    try:
        info = await channel_info(channel_id)
        if not info.get("items"):
            return await event.reply("Invalid channel id.")
        add_channel(channel_id, custom_name)
        title = info["items"][0]["snippet"]["title"]
        await event.reply(f"Added channel `{channel_id}` as `{custom_name or title}`.")
    except Exception as e:
        await event.reply(f"Error: {e}")


# Owner-only: remove a channel
@bot.on(events.NewMessage(pattern=r"/remchannel\s+(\S+)"))
async def rem_channel_cmd(event):
    if str(event.sender_id) != OWNER:
        return
    channel_id = event.pattern_match.group(1)
    if remove_channel(channel_id):
        await event.reply(f"Removed `{channel_id}`.")
    else:
        await event.reply("Channel not found.")


# Owner-only: set custom name
@bot.on(events.NewMessage(pattern=r"/setname\s+(\S+)\s+(.+)"))
async def set_name_cmd(event):
    if str(event.sender_id) != OWNER:
        return
    channel_id = event.pattern_match.group(1)
    new_name = event.pattern_match.group(2).strip()
    if set_custom_name(channel_id, new_name):
        await event.reply(f"Custom name set for `{channel_id}` -> `{new_name}`.")
    else:
        await event.reply("Channel not found.")


# Owner-only: clear custom name
@bot.on(events.NewMessage(pattern=r"/clearname\s+(\S+)"))
async def clear_name_cmd(event):
    if str(event.sender_id) != OWNER:
        return
    channel_id = event.pattern_match.group(1)
    if clear_custom_name(channel_id):
        await event.reply(f"Cleared custom name for `{channel_id}`.")
    else:
        await event.reply("Channel not found.")


async def save_it():
    # Initialize last_video_id for each channel without sending notifications
    for ch in get_channels():
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                latest = feed.entries[0].yt_videoid
                if latest not in MEMORY:
                    MEMORY.append(latest)
        except BaseException as er:
            LOGS.info(f"Failed to fetch feed for {ch['id']}: {er.with_traceback(None)}")
            continue


async def forever_check():
    LOGS.info("Checking for new videos...")
    for ch in get_channels():
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                latest = feed.entries[0].yt_videoid
                if latest not in MEMORY:
                    await proper_info_msg(bot, CHAT, latest, override_name=ch["custom_name"])
                    MEMORY.append(latest)
            await asyncio.sleep(0.3)
        except BaseException as er:
            LOGS.info(f"Failed to fetch feed for {ch['id']}: {er.with_traceback(None)}")
            await asyncio.sleep(0.2)
            continue

sch.add_job(forever_check, "interval", minutes=DELAY_TIME)

LOGS.info("Bot has started...")

async def start_everything():
    await save_it()
    sch.start()

bot.loop.run_until_complete(start_everything())
bot.loop.run_forever()
