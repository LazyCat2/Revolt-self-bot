import time
import voltage
import psutil
import asyncio

from voltage.ext import commands
from threading import Thread as th
from win10toast import ToastNotifier

notify = ToastNotifier()
prefix = 'lc'
client = voltage.Client()


async def get_prefix(msg, _=...):
    return prefix + ' ' if msg.content.startswith(prefix + ' ') else prefix


bot = commands.CommandsClient(prefix=get_prefix)
bot.commands = {}
cooldown = {}
emojis = {
    'kill': '964534407010603089',
    'nice': '496745638239666207',
    'genius': '943536847563395073'
}


async def response(msg, content=''):
    if isinstance(msg, commands.CommandContext):
        msg = msg.message

    try:
        if msg.author.id == bot.user.id:
            await msg.edit(content=content)  # f'╭╴`{prefix} {ctx.command.name}`\n' +
            return msg
        return await msg.reply(content=content, mention=False)
    except:
        return await msg.channel.send(msg.author.mention + '\n' + content)


@bot.listen('message')
async def on_msg(msg):
    print(msg.content)
    #  https://app.revolt.chat/server/SERVER_ID/channel/CNL_ID/MSG_ID
    if not msg.content.startswith(prefix) and msg.author.id == bot.user.id:
        if msg.content.startswith(':') and msg.content.endswith(':'):
            if msg.content[1:-1] in emojis:
                return await msg.edit(f'https://cdn.discordapp.com/emojis/{emojis[msg.content[1:-1]]}.webp?size=48&quality=lossless')
        parsed = msg.content.split('\n')
        for x in parsed:
            if x.startswith('https://app.revolt.chat/server/'):
                link = x.split('/')
                cnl = bot.get_channel(link[6])
                ref = await cnl.fetch_message(link[7])
                embed = voltage.SendableEmbed(
                    title=ref.author.name,
                    description=ref.content,
                    icon_url=ref.author.display_avatar.url,
                    color='var(--accent)'
                )
                await msg.edit(content=msg.content.replace(x, '') + '\n\n[[Original message]](<' + x + '>)',
                               embed=embed)
                return
    if not msg.author.id == bot.user.id:
        if cooldown.get(msg.author.id, 0) > time.time():
            return

        cooldown[msg.author.id] = time.time() + 3

    await bot.handle_commands(msg)


@bot.command()
async def info(ctx):
    await response(ctx, f'''```
CPU usage: {psutil.cpu_percent()}
Disc usage: {psutil.disk_usage('C:/').percent}%

Users:    {len(bot.users)}
Servers:  {len(bot.servers)}
Channels: {len(bot.channels)}
Members:  {len(bot.members)}
```
[[GitHub]](https://github.com/LazyCat2/)
''')


@bot.command()
async def ping(ctx):
    a = time.time()
    msg = await response(ctx, 'Pong')
    await response(msg, '`' + str(round((time.time() - a) * 1000)) + ' ms`')


@bot.command()
async def help(ctx):
    await response(ctx, '> ' + '\n'.join([
        prefix + ' ' + x for x in bot.commands
    ]))


bot.run(open('token.txt').read(), bot=False)
