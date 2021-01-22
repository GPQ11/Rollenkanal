import sys
import discord
import settings
from random import randint
from discord.ext import commands
from discord.channel import CategoryChannel, TextChannel, VoiceChannel

EXCLUDE_ROLES = ['@everyone', 'Admin', 'Bot', 'Rollenkanal', 'Schauspielerin', 'Dummy', 'neue Rolle', 'new role']

client = commands.Bot('$ ')


async def send(context, message):
    await context.message.channel.send(f'```\n{message}\n```')

@client.event
async def on_ready():
    print('Rollenkanal online')

@client.command()
async def ccrole(context):
    print(f'{context.message.author} running update...')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    tasks = 0
    for role in context.guild.roles[::-1]:
        if role.name not in EXCLUDE_ROLES:
            if discord.utils.get(context.guild.categories, name=role.name) == None:
                tasks += 1
                category = await context.guild.create_category(role.name)
                await category.set_permissions(context.guild.default_role, overwrite=discord.PermissionOverwrite(read_messages=False))
                await category.set_permissions(role, overwrite=discord.PermissionOverwrite(read_messages=True))
                await context.guild.create_voice_channel(role.name, category=category)
                await context.guild.create_text_channel(role.name, category=category)
    
    if tasks < 1: await send(context, 'Already up to date')
    else: await send(context, 'Finished updating')

@client.command()
async def rclean(context):
    print(f'{context.message.author} running rclean...')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    roles = 0
    for role in context.message.guild.roles:
        if role.name == 'neue Rolle' or role.name == 'new role':
            roles += 1
            await role.delete()
    if roles < 1: await send(context, 'Nothing to clean up')
    else: await send(context, f'Deleted {roles} roles')

@client.command()
async def cclean(context):
    print(f'{context.message.author} running cclean...')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    channels = 0
    text_names = []
    voice_names = []
    for channel in context.guild.channels:
        if not isinstance(channel, CategoryChannel) and channel.category_id == None:
            channels += 1
            await channel.delete()
        elif isinstance(channel, VoiceChannel):
            if channel.name in voice_names:
                channels += 1
                await channel.delete()
            else: voice_names.append(channel.name)
        elif isinstance(channel, TextChannel):
            if channel.name in text_names:
                channels += 1
                await channel.delete()
            else: text_names.append(channel.name)
        elif isinstance(channel, CategoryChannel) and len(channel.channels) < 1:
            channels += 1
            await channel.delete()
                
    if channels < 1: await send(context, 'Nothing to clean up')
    else: await send(context, f'Deleted {channels} channels')

@client.command()
async def clear(context, amount=None):
    print(f'{context.message.author} running clear...')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    try: amount = int(amount) + 1
    except: pass
    await context.channel.purge(limit=amount)

@client.command()
async def random(context, min=None, max=None):
    print(f'{context.message.author} running random...')
    try:
        if min == None: await send(context, f'Es wurde eine {randint(1, sys.maxsize)} gewürfelt!')
        elif max == None: await send(context, f'Es wurde eine {randint(1, int(min))} gewürfelt!')
        else: await send(context, f'Es wurde eine {randint(int(min), int(max))} gewürfelt!')
    except: await send(context, 'Die Eingabeparameter müssen Teil der Menge ℕ₀ sein!')

@client.remove_command('help')
@client.command()
async def help(context):
    print(f'{context.message.author} running help...')
    await send(context, 'Available commands:\n'+
        '\nccrole: creates new channels depending on existing roles\n'+
        '\tcclean: deletes empty categories and top-level channels\n'+
        '\trclean: deletes any unconfigured roles\n'+
        '\trandom: generates a random number (usually very big)\n'+
        '\trandom:')

if __name__ == '__main__':
    try:
        client.run(settings.TOKEN)
    except Exception as e:
        print(e)
        client.run(settings.TOKEN)