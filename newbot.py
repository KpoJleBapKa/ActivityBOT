import discord
from discord.ext import commands, tasks
import datetime
import asyncio

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Створіть список для зберігання даних про сервери та канали
server_data = [
    {'server_id': 748275815992656223, 'channel_id': 1159441002935889930},  # Налаштування для першого серверу
    {'server_id': 1141311464985083975, 'channel_id': 1158891013931278416},  # Налаштування для другого серверу
    # Додайте налаштування для інших серверів тут
]

@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} підключився до Discord!')
    
    # Видалення всіх повідомлень у текстовому каналі для кожного серверу
    for data in server_data:
        server_id = data['server_id']
        channel_id = data['channel_id']
        channel = bot.get_channel(channel_id)
        
        if channel:
            await channel.purge()
    
    update_status.start()
    update_roles.start()

@tasks.loop(seconds=30)
async def update_status():
    for data in server_data:
        server_id = data['server_id']
        channel_id = data['channel_id']
        channel = bot.get_channel(channel_id)
        
        if channel:
            guild = bot.get_guild(server_id)
            
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
            
            # Створіть повідомлення для кожного з розділів
            online_message = '|----------- ONLINE -----------|\n' + '\n'.join(online_members)
            idle_message = '|----------- IDLE -----------|\n' + '\n'.join(idle_members)
            dnd_message = '|----------- DON\'T DISTURB -----------|\n' + '\n'.join(dnd_members)
            offline_message = '|----------- OFFLINE -----------|\n' + '\n'.join(offline_members)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Створіть список повідомлень для відправки
            messages_to_send = []
            
            # Додайте повідомлення до списку з можливим розділенням на частини
            messages_to_send.extend(split_message(online_message))
            messages_to_send.extend(split_message(idle_message))
            messages_to_send.extend(split_message(dnd_message))
            messages_to_send.extend(split_message(offline_message))
            messages_to_send.append(f'Оновлено: {current_time}')
            
            # Перевірте, чи є вже повідомлення, і відредагуйте їх
            if hasattr(bot, f'status_messages_{server_id}'):
                for i, message in enumerate(messages_to_send):
                    if i < len(getattr(bot, f'status_messages_{server_id}')):
                        await getattr(bot, f'status_messages_{server_id}')[i].edit(content=message)
                    else:
                        # Якщо індекс повідомлення перевищує існуючі, створіть нове повідомлення
                        new_msg = await channel.send(message)
                        getattr(bot, f'status_messages_{server_id}').append(new_msg)
            
            else:
                # Якщо повідомлень немає, створіть їх
                setattr(bot, f'status_messages_{server_id}', [])
                for message in messages_to_send:
                    new_msg = await channel.send(message)
                    getattr(bot, f'status_messages_{server_id}').append(new_msg)

def split_message(message):
    # Розділити повідомлення на частини, якщо його довжина перевищує 1900 символів
    max_length = 1900
    messages = []
    current_message = ""
    
    for line in message.splitlines():
        if len(current_message) + len(line) + 1 <= max_length:
            if current_message:
                current_message += "\n"
            current_message += line
        else:
            messages.append(current_message)
            current_message = line
    
    if current_message:
        messages.append(current_message)
    
    return messages

@tasks.loop(seconds=30)
async def update_roles():
    for data in server_data:
        server_id = data['server_id']
        guild = bot.get_guild(server_id)
        
        for member in guild.members:
            # Збережіть існуючі ролі учасника, які були видані до цього ботом
            bot_roles = [role.name for role in member.roles if role.name.startswith("Online ")]
            
            playing_activities = [activity.name for activity in member.activities if activity.type == discord.ActivityType.playing]
            
            for activity_name in playing_activities:
                role_name = f"Online {activity_name}"
                if role_name not in bot_roles:
                    # Якщо роль не видається ботом, видайте її
                    role = discord.utils.get(guild.roles, name=role_name)
                    if role is None:
                        # Якщо роль не існує, створіть її та задайте колір
                        await guild.create_role(name=role_name, color=discord.Color.green())
                        role = discord.utils.get(guild.roles, name=role_name)
                    if role:
                        await member.add_roles(role)
            
            # Видаліть ролі, які не відповідають активностям учасника
            for role in member.roles:
                if role.name.startswith("Online ") and role.name not in [f"Online {activity}" for activity in playing_activities]:
                    await member.remove_roles(role)

# Змінено для обробки завершення роботи програми
async def on_shutdown():
    await bot.close()

# Запуск бота
if __name__ == "__main__":
    bot.add_listener(on_shutdown, "on_shutdown")
    bot.run('YOUR_TOKEN')  # Замініть на свій токен бота



# token - MTE1ODUyNTMwMDU3ODE5NzU1Ng.GKd1hG.78HVUIG66f9CUuKNra6ZHwaQt4d0J7bUA3wgUY
# YOUR_TOKEN
# id каналу - 1158891013931278416 
# id серверу - 1141311464985083975