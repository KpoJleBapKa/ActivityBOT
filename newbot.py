import discord
from discord.ext import commands, tasks
import datetime

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} підключився до Discord!')
    update_status.start()

@tasks.loop(seconds=30)
async def update_status():
    channel_id = 1158891013931278416  # Замініть на ID каналу, де бот буде відправляти повідомлення
    channel = bot.get_channel(channel_id)
    
    if channel:
        guild_id = 1141311464985083975  # Замініть на ID вашого серверу
        guild = bot.get_guild(guild_id)
        
        online_members = []
        idle_members = []
        dnd_members = []
        offline_members = []
        
        for member in guild.members:
            if member.status == discord.Status.online:
                if any(activity.type == discord.ActivityType.playing for activity in member.activities):
                    playing_activities = [activity.name for activity in member.activities if activity.type == discord.ActivityType.playing]
                    online_members.append(f'**{member.name}** - **online** - грає у **{" / ".join(playing_activities)}**')
                else:
                    online_members.append(f'**{member.name}** - **online** - не грає у жодну гру')
            elif member.status == discord.Status.idle:
                if any(activity.type == discord.ActivityType.playing for activity in member.activities):
                    playing_activities = [activity.name for activity in member.activities if activity.type == discord.ActivityType.playing]
                    idle_members.append(f'**{member.name}** - **idle** - грає у **{" / ".join(playing_activities)}**')
                else:
                    idle_members.append(f'**{member.name}** - **idle** - не грає у жодну гру')
            elif member.status == discord.Status.offline:
                offline_members.append(f'**{member.name}** - **offline**')
            elif member.status == discord.Status.dnd:
                if any(activity.type == discord.ActivityType.playing for activity in member.activities):
                    playing_activities = [activity.name for activity in member.activities if activity.type == discord.ActivityType.playing]
                    dnd_members.append(f'**{member.name}** - **don\'t disturb** - грає у **{" / ".join(playing_activities)}**')
                else:
                    dnd_members.append(f'**{member.name}** - **don\'t disturb** - не грає у жодну гру')
        
        online_message = '\n'.join(online_members)
        idle_message = '\n'.join(idle_members)
        dnd_message = '\n'.join(dnd_members)
        offline_message = '\n'.join(offline_members)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'|----------- ONLINE -----------|\n{online_message}\n|----------- IDLE -----------|\n{idle_message}\n|----------- DON\'T DISTURB -----------|\n{dnd_message}\n|----------- OFFLINE -----------|\n{offline_message}\nОновлено: {current_time}'
        
        if not hasattr(bot, 'status_message'):
            bot.status_message = await channel.send(message)
        else:
            await bot.status_message.edit(content=message)

@bot.event
async def on_member_update(before, after):
    if before.status != after.status or before.activities != after.activities:
        await update_status()

# Запуск бота
bot.run('YOUR_TOKEN')  # Замініть на свій токен бота




# token - MTE1ODUyNTMwMDU3ODE5NzU1Ng.GKd1hG.78HVUIG66f9CUuKNra6ZHwaQt4d0J7bUA3wgUY
# id каналу - 1158891013931278416 
# id серверу - 1141311464985083975