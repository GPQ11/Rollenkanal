#!/usr/bin/python

'''This module is used for a Discord bot for the GPQ11 Discord server.'''

import sys
import time
from random import randint
from datetime import datetime

import discord
import discord.utils
from discord.ext import commands
from discord.channel import CategoryChannel, TextChannel, VoiceChannel

import settings


SERVER_NAME = 'Q11'
EXCLUDE_ROLES = [
    '@everyone',
    'Admin',
    'Bot',
    'Rollenkanal',
    'Schauspielerin',
    'Dummy',
    'neue Rolle',
    'new role'
]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot('$', intents=intents)


def log(message):
    log_message = f'[{datetime.now().time()}] {message}'.replace('\n', '\\n')
    print(log_message)
    with open('logs/' + str(datetime.now().date()) + '.log', 'a') as f:
        f.write(log_message + '\n')

def get_gpq11_guild():
    '''returns a guild object if the bot is member of a guild named "Q11"; returns None if not'''
    for guild in client.guilds:
        if guild.name.strip() == SERVER_NAME:
            return guild
    return None


def get_role_table():
    '''returns a dict of int-string pairs mathcing the roles on a guild named "Q11"'''
    role_table = {}
    index = 0
    for role in get_gpq11_guild().roles[::-1]:
        if role.name not in EXCLUDE_ROLES + ['Kurssprecher']:
            role_table[index] = role.name
            index += 1
    return role_table

async def send(context, message):
    '''sends a message in the channel of the context object'''
    log(f'sending \"{message}\" to \"{context.message.author}\"')
    await context.message.channel.send(f'```\n{message}\n```')

@client.event
async def on_ready():
    '''executed on bot login'''
    log('Rollenkanal online')
    if get_gpq11_guild() is None:
        client.logout()


@client.command()
@commands.has_permissions(administrator=True)
async def ccrole(context):
    '''Erstellt Kanäle abhängig von existierenden Rollen'''
    log(f'\"{context.message.author}\" running ccrole... (\"{context.message.content}\")')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    tasks = 0
    for role in context.guild.roles[::-1]:
        if role.name not in EXCLUDE_ROLES:
            if discord.utils.get(context.guild.categories, name=role.name) is None:
                tasks += 1
                category = await context.guild.create_category(role.name)
                await category.set_permissions(context.guild.default_role, overwrite=discord.PermissionOverwrite(read_messages=False))
                await category.set_permissions(role, overwrite=discord.PermissionOverwrite(read_messages=True))
                await context.guild.create_voice_channel(role.name, category=category)
                await context.guild.create_text_channel(role.name, category=category)
    
    if tasks < 1:
        await send(context, 'Already up to date')
    else:
        await send(context, 'Finished updating')

@client.command()
@commands.has_permissions(administrator=True)
async def rclean(context):
    '''Löscht unkonfigurierte Rollen'''
    log(f'\"{context.message.author}\" running rclean... (\"{context.message.content}\")')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    roles = 0
    for role in context.message.guild.roles:
        if role.name == 'neue Rolle' or role.name == 'new role':
            roles += 1
            await role.delete()
    if roles < 1:
        await send(context, 'Nothing to clean up')
    else:
        await send(context, f'Deleted {roles} roles')



@client.command()
@commands.has_permissions(administrator=True)
async def cclean(context):
    '''Löscht leere Kategorien und Kanäle ohne Kategorie'''
    log(f'\"{context.message.author}\" running cclean... (\"{context.message.content}\")')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    channels = 0
    text_names = []
    voice_names = []
    for channel in context.guild.channels:
        if not isinstance(channel, CategoryChannel) and channel.category_id is None:
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
                
    if channels < 1:
        await send(context, 'Nothing to clean up')
    else:
        await send(context, f'Deleted {channels} channels')

@client.command()
@commands.has_permissions(administrator=True)
async def clear(context, anzahl=None):
    '''Löscht eine (un-)bestimmte Anzahl von Nachrichten in einem Channel'''
    log(f'\"{context.message.author}\" running clear... (\"{context.message.content}\")')
    if isinstance(context.channel, discord.channel.DMChannel):
        await send(context, 'Das geht leider nicht in privaten Konversationen!')
        return
    
    try: anzahl = int(anzahl) + 1
    except: pass

    await context.channel.purge(limit=anzahl)


@client.command()
async def getrole(context, roleid=None):
    '''Verleiht Mitgliedern die Möglichkeit sich selbst bestimmte Rollen zu vergeben'''
    if not isinstance(context.channel, discord.channel.DMChannel):
        return

    log(f'\"{context.message.author}\" running getrole... (\"{context.message.content}\")')

    gpq11_guild = get_gpq11_guild()
    member = gpq11_guild.get_member_named(context.message.author.name)
    if member is None:
        await send(context, 'Das darfst du nicht!')
        return

    role_table = get_role_table()
    if roleid is None:
        message = ''
        for key in role_table:
            message += f'{key}:\t{role_table[key]}\n'
        await send(context, message + '---------------\n$getrole <KEY>\n$unrole <KEY>')
        return
    try:
        roleid = int(roleid)
        if roleid < 0 or roleid > list(role_table.keys())[-1]:
            raise(ValueError())
    except ValueError:
        await send(context, f'Der Eingabeparameter muss Teil des Intervalls [0;{list(role_table.keys())[-1]}] ∈ ℕ₀ sein!')
        return

    for role in member.roles:
        if role_table[roleid] != role.name and role_table[roleid].split(' ')[0] in role.name:
            await send(context, f'Du hast bereits eine Rolle dieser Kategorie! ({role_table[roleid]})')
            return
        if role_table[roleid] == role.name:
            await send(context, f'Du hast die Rolle \'{role_table[roleid]}\' bereits!')
            return
    
    await member.add_roles(discord.utils.get(gpq11_guild.roles, name=role_table[roleid]))
    await send(context, f'\'{role_table[roleid]}\' als Rolle hinzugefügt!')



@client.command()
async def unrole(context, roleid=None):
    '''Verleiht Mitgliedern die Möglichkeit sich selbst bestimmte Rollen wegzunehmen'''
    if not isinstance(context.channel, discord.channel.DMChannel):
        return

    log(f'\"{context.message.author}\" running unrole... (\"{context.message.content}\")')

    gpq11_guild = get_gpq11_guild()
    member = gpq11_guild.get_member_named(context.message.author.name)
    if member is None:
        await send(context, 'Das darfst du nicht!')
        return

    role_table = get_role_table()
    if roleid is None:
        message = ''
        for key in role_table:
            message += f'{key}:\t{role_table[key]}\n'
        await send(context, message + '---------------\n$getrole <KEY>\n$unrole <KEY>')
        return

    try:
        roleid = int(roleid)
        if roleid < 0 or roleid > list(role_table.keys())[-1]:
            raise(ValueError())
    except ValueError:
        await send(context, f'Der Eingabeparameter muss Teil des Intervalls [0;{list(role_table.keys())[-1]}] ∈ ℕ₀ sein!')
        return

    for role in member.roles:
        if role_table[roleid] == role.name:
            await member.remove_roles(discord.utils.get(gpq11_guild.roles, name=role_table[roleid]))
            await send(context, f'\'{role_table[roleid]}\' als Rolle entfernt!')
            return

    await send(context, f'Du hast die Rolle \'{role_table[roleid]}\' nicht!')


@client.command()
async def random(context, minimum=None, maximum=None, anzahl=1):
    '''Erstellt Pseudozufallszahlen'''
    log(f'\"{context.message.author}\" running random... (\"{context.message.content}\")')
        
    try:
        anzahl = int(anzahl)
        for i in range(anzahl):
            if minimum is None:
                await send(context, f'Es wurde eine {randint(1, sys.maxsize)} gewürfelt!')
            elif maximum is None:
                await send(context, f'Es wurde eine {randint(1, int(minimum))} gewürfelt!')
            else:
                minimum = int(minimum)
                maximum = int(maximum)
                if maximum < minimum:
                    await send(context, f'Es wurde eine {randint(maximum, minimum)} gewürfelt!')
                else:
                    await send(context, f'Es wurde eine {randint(minimum, maximum)} gewürfelt!')
    except ValueError:
        await send(context, 'Die Eingabeparameter müssen Teil der Menge ℕ₀ sein!')




if __name__ == '__main__':
    while True:
        try:
            client.run(settings.TOKEN)
        except KeyboardInterrupt:
            print('keyboard interrupt')
            exit(0)
        except Exception as exception:
            print(exception)
            time.sleep(10)
