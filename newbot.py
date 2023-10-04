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

@tasks.loop(minutes=1)
async def update_status():
    channel_id = 1158524081742827532  # Замініть на ID каналу, де бот буде відправляти повідомлення
    channel = bot.get_channel(channel_id)
    
    if channel:
        guild_id = 1141311464985083975  # Замініть на ID вашого серверу
        guild = bot.get_guild(guild_id)
        
        # Отримуємо окремо статуси учасників
        online_members = [member for member in guild.members if member.status == discord.Status.online]
        idle_members = [member for member in guild.members if member.status == discord.Status.idle]
        offline_members = [member for member in guild.members if member.status == discord.Status.offline]
        
        online_message = '\n'.join([f'**{member.name}** - **online** - грає у **{member.activity.name}**' if member.activity else f'**{member.name}** - **online** - не грає ні в що' for member in online_members])
        idle_message = '\n'.join([f'**{member.name}** - **idle**' for member in idle_members])
        offline_message = '\n'.join([f'**{member.name}** - **offline**' for member in offline_members])

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'|----------- ONLINE -----------|\n{online_message}\n|----------- IDLE -----------|\n{idle_message}\n|----------- OFFLINE -----------|\n{offline_message}\nОновлено: {current_time}'
        
        if not hasattr(bot, 'status_message'):
            bot.status_message = await channel.send(message)
        else:
            await bot.status_message.edit(content=message)

@bot.event
async def on_member_update(before, after):
    if before.status != after.status or before.activity != after.activity:
        await update_status()

# Запуск бота
bot.run('MTE1ODUyNTMwMDU3ODE5NzU1Ng.GKd1hG.78HVUIG66f9CUuKNra6ZHwaQt4d0J7bUA3wgUY')  # Замініть на свій токен бота



# token - MTE1ODUyNTMwMDU3ODE5NzU1Ng.GKd1hG.78HVUIG66f9CUuKNra6ZHwaQt4d0J7bUA3wgUY
# id каналу - 1158891013931278416
# id серверу - 1141311464985083975