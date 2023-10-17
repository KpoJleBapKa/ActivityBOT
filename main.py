import discord
from discord.ext import commands, tasks
import datetime
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='&', intents=intents, shutdown_hooks=True)

POST_ID = 1160695186884665374

ROLES = {
    '♀️': 1160695452782575656,
    '♂️': 1160695315368788089,
    '💅': 1161426283260022815,
    '🎮': 1160695682181636126,
    '⛏️': 1160695772153643169,
    '🔫': 1160695841833631824,
    '♿': 1160695846342512781,
    '🍺': 1160695979658448978,
    '🚗': 1160696027645497375,
    '🦀': 1163877637131874425,
    '👹': 1161426426168365127, 
    '👟': 1161426472104370196,
    '🎤': 1161426499488976967,
    '💢': 1161426530925293599,
    '⚡': 1161426586805997598,
    '👑': 1161426366542139451,
    '⚔️': 1161426392962060451,
}

@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} підключився до Discord!')

    # Отримайте повідомлення за його ідентифікатором
    channel_id = 1160691803767455754  # Замініть на ідентифікатор вашого каналу
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(POST_ID)

    # Пройдіться по реакціях на повідомленні і видайте відповідні ролі
    for reaction in message.reactions:
        if reaction.emoji in ROLES:
            role_id = ROLES[reaction.emoji]
            role = discord.utils.get(message.guild.roles, id=role_id)
            if role is not None:
                users = await reaction.users().flatten()
                for user in users:
                    member = message.guild.get_member(user.id)
                    if member is not None:
                        await member.add_roles(role)
                        print(f'Видано роль {role.name} користувачу {member.display_name}')

    # Перевірка і видалення ролей, які не відповідають реакціям на повідомленні
    for member in message.guild.members:
        roles_to_remove = [role for role in member.roles if role.id in ROLES.values() and role.name not in [str(reaction.emoji) for reaction in message.reactions]]
        for role in roles_to_remove:
            await member.remove_roles(role)
            print(f'Знято роль {role.name} у користувача {member.display_name}')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == POST_ID:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

        if payload.emoji.name in ROLES:
            role = discord.utils.get(guild.roles, id=ROLES[payload.emoji.name])

            if role is not None:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.add_roles(role)
                    print(f'Видано роль {role.name} користувачу {member.display_name}')

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == POST_ID:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)

        if payload.emoji.name in ROLES:
            role = discord.utils.get(guild.roles, id=ROLES[payload.emoji.name])

            if role is not None:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.remove_roles(role)
                    print(f'Знято роль {role.name} у користувача {member.display_name}')

# Створіть список для зберігання даних про сервери та канали
server_data = [
    #{'server_id': 748275815992656223, 'channel_id': 1159441002935889930},  
    {'server_id': 1141311464985083975, 'channel_id': 1158891013931278416},  
    #{'server_id': 1159287478629445643, 'channel_id': 1160166893735387206}, # проблемний сервер
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

@tasks.loop(minutes=1)
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

            # Використовуйте fetch_members для отримання інформації про всіх користувачів на сервері
            await guild.chunk()

            for member in guild.members:
                if member.status == discord.Status.online:
                    if any(activity.type == discord.ActivityType.playing for activity in member.activities):
                        playing_activities = [activity.name for activity in member.activities if
                                              activity.type == discord.ActivityType.playing]
                        online_members.append(
                            f'**{member.name}** - **online** - грає у **{" / ".join(playing_activities)}**')
                    else:
                        online_members.append(f'**{member.name}** - **online** - не грає у жодну гру')
                elif member.status == discord.Status.idle:
                    if any(activity.type == discord.ActivityType.playing for activity in member.activities):
                        playing_activities = [activity.name for activity in member.activities if
                                              activity.type == discord.ActivityType.playing]
                        idle_members.append(f'**{member.name}** - **idle** - грає у **{" / ".join(playing_activities)}**')
                    else:
                        idle_members.append(f'**{member.name}** - **idle** - не грає у жодну гру')
                elif member.status == discord.Status.offline:
                    offline_members.append(f'**{member.name}** - **offline**')
                elif member.status == discord.Status.dnd:
                    if any(activity.type == discord.ActivityType.playing for activity in member.activities):
                        playing_activities = [activity.name for activity in member.activities if
                                              activity.type == discord.ActivityType.playing]
                        dnd_members.append(
                            f'**{member.name}** - **don\'t disturb** - грає у **{" / ".join(playing_activities)}**')
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

@tasks.loop(minutes=1)
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


# Зміна імені команди !help на !hlp
@bot.command(name='rules')
async def help_command(ctx):
    embed = discord.Embed(
        title='Список доступних команд:',
        color=discord.Color.blue()
    )
    embed.add_field(name='&rules', value='Навігація по боту', inline=False)
    embed.add_field(name='&botinfo', value='Інформація про бота', inline=False)
    embed.add_field(name='&members', value='Відображення списку учасників серверу', inline=False)
    embed.add_field(name='&clear', value='Очищення повідомлень в текстовому каналі', inline=False)
    embed.add_field(name='&hello', value='Привітання від бота', inline=False)
    await ctx.send(embed=embed)



@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(
        title='Інформація про бота',
        description='Бот для відслідковування активності учасників серверу.',
        color=discord.Color.blue()
    )
    embed.add_field(name='Автор', value='Kroll', inline=False)
    embed.add_field(name='Версія бота', value='4.0', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def members(ctx):
    members = [member.display_name for member in ctx.guild.members]
    members_list = '\n'.join(members)
    await ctx.send(f'Список учасників серверу:\n{members_list}')


@bot.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'{amount} повідомлень було видалено.', delete_after=5)


@bot.command(name='hello')
async def hello_command(ctx):
    await ctx.send(f'Привіт, {ctx.author.mention}!')


@bot.event
async def on_shutdown():
    await bot.close()

bot.add_listener(on_shutdown, "on_shutdown")        
# Запуск бота
bot.run('MTE1ODUyNTMwMDU3ODE5NzU1Ng.GihVl-.MlLpAw6OoSxiP5rpyY0f0PZyOW6xamWMBOT5iM')  # Замініть на свій токен бота
# token - MTE1ODUyNTMwMDU3ODE5NzU1Ng.GKd1hG.78HVUIG66f9CUuKNra6ZHwaQt4d0J7bUA3wgUY
# YOUR_TOKEN
# id каналу - 1158891013931278416 
# id серверу - 1141311464985083975
