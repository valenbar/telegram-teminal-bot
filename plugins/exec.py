import asyncio
import os
from getpass import getuser

from pyrogram import Client, filters
from pyrogram.types import Message

from config import allowed, log_channel
from functions.terminal import Terminal

# from plugins.markups import base_markup, kill_markup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_message(filters.user(allowed) & ~filters.command(['start', 'help', 'st', 'stats', 'ip', 'my_files', 'update', 'speedtest', 'cd', 'speedtest', 'wol']) & filters.text)
async def exec_cmd(_: Client, msg: Message):
    m = msg.text
    cmd = await Terminal.execute(m)
    user = getuser()
    uid = os.geteuid()

    output = f"`{user}:~#` `{cmd}`\n" if uid == 0 else f"`{user}:~$` pid: {cmd.get_pid()} `{cmd}`\n"
    count = 0
    k = None
    kill_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"kill {cmd.get_pid()}", callback_data=f'kill_pid:{cmd.get_pid()}')]])
    while not cmd.finished:
        count += 1
        await asyncio.sleep(0.3)
        if count >= 5:
            count = 0
            out_data = f"{output}`{cmd.read_line}`"
            try:
                if not k:
                    k = await msg.reply(out_data)
                else:
                    await k.edit(out_data, reply_markup=kill_markup)
            except Exception:
                pass
    out_data = f"`{output}{cmd.get_output}`"
    if len(out_data) > 4096:
        if k:
            await k.delete()
        with open("terminal.txt", "w+") as file:
            file.write(out_data)
            file.close()
        await msg.reply_document(
            "terminal.txt", caption=cmd)
        os.remove("terminal.txt")
        return
    send = k.edit if k else msg.reply
    await send(out_data)
    if log_channel:
        try:
            await _.send_message(log_channel, f"User: {msg.from_user.mention} Execute Command: {m}")
        except Exception as e:
            pass

