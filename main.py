from discord.channel import CategoryChannel, TextChannel, VoiceChannel
import settings
import discord
from discord.ext import commands

class RKClient(discord.Client):
    async def on_message(self, msg):
        if msg.content.startswith('$ '):
            args = msg.content[2::].split(' ')
            if len(args) < 1: return
            if args[0] == 'update':
                for role in msg.guild.roles[::-1]:
                    if role.name not in '@everyoneAdminBotRollenkanalSchauspielerin':
                        try:
                            if discord.utils.get(msg.guild.categories, name=role.name) == None:
                                category = await msg.guild.create_category(role.name)
                                await category.set_permissions(msg.guild.default_role, overwrite=discord.PermissionOverwrite(read_messages=False))
                                await category.set_permissions(role, overwrite=discord.PermissionOverwrite(read_messages=True))
                                await msg.guild.create_voice_channel(role.name, category=category)
                                await msg.guild.create_text_channel(role.name, category=category)
                        except Exception as e:
                            print(e)
                await msg.channel.send('Finished updating')
            
            elif args[0] == 'cclean':
                text_names = []
                voice_names = []
                channels = 0
                for channel in msg.guild.channels:
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
                
                if channels < 1: await msg.channel.send('Nothing to clean up')
                else: await msg.channel.send(f'Deleted {channels} channels')


if __name__ == '__main__':
    RKClient().run(settings.TOKEN)