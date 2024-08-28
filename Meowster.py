from logging import exception
from PIL import Image, ImageDraw, ImageFont
import discord, json, random, re, math, os, pygame
from discord.ext import commands
from datetime import datetime, time, timedelta
from discord import ActionRow, Button, ButtonStyle, components, Embed

#
# Made by ThatOneKidSky 
# I am sorry
#
# Added: Aug 28, 2024
#  - Removed pretty much all the comments...
#    some of them did not age well...
#  - Removed variables like the token, channel id's, and user ids
#    you need to set them if you want to copy this bot (look for comments)
#

# Inits and magic numbers
#region

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

token = '' # I aint dumb lol
generalChannelID = 
guildID = 
horseChannelID = 

dataFileLocation = 'data.json'

spamThreshold = 10
reactionCooldown = 5

# Make sure when adding anything you also add it to the create_data function's items too
# This is default values, except i wanted to punish one fella so it needs to be set in 2 places (i was lazy)
datavalues = {
	"Name": "Unset", 
	"Points": 0, 
	"UserCard": "basic", 
	"LastReaction": 0, 
	"ReactionsSpam": 0,
	"Daily": 0, 
	"MusicChannel": 0
}

#endregion

# [Functions] Data management ()
#region

data = {}
def load_data():
	global data
	with open(dataFileLocation, 'r', encoding='utf-8') as file:
		data = json.load(file)

def save_data():
	global data
	with open(dataFileLocation, 'w') as file:
		json.dump(data, file, indent=4)

with open(dataFileLocation, 'r') as file:
	data = json.load(file)

@commands.command(name='forceloaddata')
async def force_load_data(ctx):
	if ctx.author.id == # USER WITH DEV PERMS #:
		try:
			load_data()
			await ctx.send('data updated!')
		except Exception as e:
			await ctx.send(f'data could not be updated: {e}')
	else:
		await ctx.send('go fuck yourself')
	return True
bot.add_command(force_load_data)

#endregion

# Bot events
#region

@bot.event
async def on_ready():
	mainChannel = bot.get_channel(generalChannelID)
	loadAllNonSavedPlayers()
	print(f'{bot.user.name}> Loaded')
	return True

@bot.event
async def on_message(message):			
	if message.content.startswith('!'):
		await bot.process_commands(message)

#endregion
	
# Message events
#region

#endregion

# Reaction add / remove
#region

@bot.event
async def on_reaction_add(reaction, user):
	if user.bot:
		return False
	if isinstance(reaction.message.channel, discord.DMChannel):
		if shoops[str(user.id)] != None:
			await shoops[str(user.id)].select(reaction)
	else:
		await add_social_point_react(reaction, user)
	return True

@bot.event
async def on_reaction_remove(reaction, user):
	if isinstance(reaction.message.channel, discord.DMChannel):
		pass
	else:
		await remove_social_point_react(reaction, user)

#endregion

# [Functions] Player data
#region

# Point add & remove
#region 

# Social points!
async def add_social_point_react(reaction, user):
	try:
		if user.id == reaction.message.author.id or reaction.message.author.bot:
			return False
				
		currentTime = datetime.now().time()
		
		currentMinutes = currentTime.hour * 60 + currentTime.minute
		reactorLastReaction = data['Players'][str(user.id)]['LastReaction']
				
		if reactorLastReaction <= currentMinutes - reactionCooldown:
			set_player_data(str(user.id), 'ReactionsSpam', 0)
		
		reactorCounter = data['Players'][str(user.id)]['ReactionsSpam']
		if reactorCounter >= spamThreshold:
			await reaction.remove(user)
			return False
		
		if reaction.emoji.name == 'plus1':
			change_player_data(str(reaction.message.author.id), 'Points', 1)
			
			change_player_data(str(user.id), 'ReactionsSpam', 1)
			set_player_data(str(user.id), 'LastReaction', currentMinutes)
		elif reaction.emoji.name == 'minus1':
			change_player_data(str(reaction.message.author.id), 'Points', - 1)
			
			change_player_data(str(user.id), 'ReactionsSpam', 1)
			set_player_data(str(user.id), 'LastReaction', currentMinutes)
		return True
	except Exception as e:
		print(e)
		return False
	
# Social pointsn't!
async def remove_social_point_react(reaction, user):
	try:
		if user.id == reaction.message.author.id or reaction.message.author.bot:
			return False
		
		currentTime = datetime.now().time()
		
		currentMinutes = currentTime.hour * 60 + currentTime.minute
		reactorLastReaction = data['Players'][str(user.id)]['LastReaction']
				
		if reactorLastReaction <= currentMinutes - reactionCooldown:
			set_player_data(str(user.id), 'ReactionsSpam', 0)
		
		reactorCounter = data['Players'][str(user.id)]['ReactionsSpam']
		if reactorCounter >= spamThreshold:
			await reaction.remove(user)
			return False
		
		if reaction.emoji.name == 'plus1':
			change_player_data(str(reaction.message.author.id), 'Points', - 1)
		elif reaction.emoji.name == 'minus1':
			change_player_data(str(reaction.message.author.id), 'Points', 1)
		return True
	except Exception as e:
		print(e)
		return False
	
#endregion

# Reading player points
#region

@commands.command(name='playerdata')
async def player_data_command(ctx, targetplayer: discord.Member = None):
	player = ctx.author if targetplayer == None else targetplayer
			
	if player.bot:
		await ctx.send('That a bot you fucking dumb ass.')
		return False

	if str(player.id) not in data['Players']:
		await ctx.send('Data not detected,\ncreating new player data...')
		try:
			create_new_data(player.id, player.display_name)
			await ctx.send('Data successfully created.')
		except Exception as e:
			await ctx.send(f"There is an unexpected error creating data.")
			print(f'{bot.user.name}> ERROR in player data command block 0: {e}')
			return False
			
	if isinstance(player, discord.Member):
		image = generate_image(player.id)
			
		tempImagePath = 'temp/tempid.png'
		image.save(tempImagePath)
			
		with open(tempImagePath, 'rb') as file:
			await ctx.send(file=discord.File(file, 'id.png'))
		return True
	else:
		await ctx.send("Error: Unable to retrieve author information.")
		print(f'{bot.user.name}> ERROR in player data command block 1: Could not retrieve author info')
		return False
bot.add_command(player_data_command)

@commands.command(name='lb')
async def player_leaderboard(ctx):
	leaderboard = {}
	for player in data['Players']:
		leaderboard[data['Players'][player]['Name']] = data['Players'][player]['Points']		
	leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))
	
	embed = discord.Embed(title="Leaderboard", color=discord.Color.red())
	boardValues = ''
	for name, points in leaderboard.items():
		boardValues += f'{name}: {points}\n'
	embed.add_field(name='', value=boardValues, inline=False)
	await ctx.channel.send(embed=embed)
bot.add_command(player_leaderboard)

def generate_image(playerID):
	ID = data['Players'][str(playerID)]['UserCard']
	name = data['Players'][str(playerID)]['Name']
	points = data['Players'][str(playerID)]['Points']
	font_path = data['Id'][ID]['font']

	templatePath = data['Id'][ID]['file']
	image = Image.open(templatePath)
	draw = ImageDraw.Draw(image)
		
	font = ImageFont.truetype(font_path, size=data['Id'][ID]['nameScale'])
	textPos = (data['Id'][ID]['namex'], data['Id'][ID]['namey'])
	text = str(name)[:data['Id'][ID]['nameMaxLen']]
	draw.text(textPos, text, fill='black', font=font)
		
	font = ImageFont.truetype(font_path, size=data['Id'][ID]['pointsScale'])
	textPos = (data['Id'][ID]['pointsx'], data['Id'][ID]['pointsy'])
	text = str(points)[:data['Id'][ID]['nameMaxLen']]
	draw.text(textPos, text, fill='black', font=font)
			
	return image

#endregion

# Setting data
#region

@commands.command(name='setname')
async def player_set_name_command(ctx, newName = ''):
	player = ctx.author.id
	if str(ctx.author.id) not in data['Players']:
		await ctx.send('Data not detected,\ncreate new data by running !playerdata')
	elif newName == '':
		await ctx.send('No name arguments given.\nUse: !setname [name]')
	elif len(newName) > 32:
		await ctx.send("Name too long, limit is 32 characters.")
	else:
		try:
			set_player_data(player, 'Name', newName)
			await ctx.send("Name changed successfully.")
		except Exception as e:
			await ctx.send(f"There is an unexpected error setting your name.")
			print(f'{bot.user.name}> ERROR in set name command: {e}')
	return True
bot.add_command(player_set_name_command)

@commands.command(name='updatedataitems')
async def player_set_name_command(ctx, newName = ''):
	if ctx.author.id != 309847108444487682:
		await ctx.send('🖕')
	for playerid, playerdata in data['Players'].items():
		for item, value in datavalues.items():
			if item not in playerdata:
				data['Players'][playerid][item] = value
				print(f'Item not detected for user {playerid}: {item}')
	save_data()
	await ctx.send('Updated')
bot.add_command(player_set_name_command)

def set_player_data(playerId, index, value):
	data['Players'][str(playerId)][index] = value
	save_data()
	return True

def change_player_data(playerId, index, rate):
	data['Players'][str(playerId)][index] = data['Players'][str(playerId)][index] + rate
	save_data()
	return True

#endregion

# Creating data
#region

def create_new_data(playerId, playerName = 'Not Set', playerPoints = 0):
	playerData = {
		"Name": playerName,
		"Points": playerPoints,
		"UserCard": "basic", 
		"LastReaction": 0, 
		"ReactionsSpam": 0,
		"Daily": 0, 
		"MusicChannel": 0
	}
	
	data['Players'][str(playerId)] = playerData
	
	save_data()
	print(f'Created new data for {str(playerId)} AKA: {str(playerName)}')
	return True

def loadAllNonSavedPlayers():
	for guild in bot.guilds:
		for member in guild.members:
			if not member.bot and str(member.id) not in data['Players']:
				create_new_data(member.id, member.display_name)
	return True

@bot.event
async def on_member_join(member):
	print(f'{bot.user.name}> New member has joined: {member.display_name}')
	if not member.bot and str(member.id) not in data['Players']:
		create_new_data(member.id, member.display_name)
	return True

#endregion

#endregion

# Shoop
#region

shoopFile = 'shoop/shoop.json'
shoopEmojies = ['0⃣', '1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
shoopArrows = ['⬅', '➡']
shoops = {}


@commands.command(name='openshoop')
async def open_shoop(ctx):
	user = ctx.author
	if user != bot.user:
		try: 
			await shoops[str(user.id)].close_shoop()
		except:
			print('shoop must not be open :]')
		print('Shoop is not open!')
		try:
			await open_shoop(user)
		except Exception as e:
			await ctx.send("I could not send a message to you, check your **Privacy & Safety** settings.\nYou should enable Allow direct messages from server members. #(you may need to rejoin the server)")
			print(e)
		
bot.add_command(open_shoop)

async def open_shoop(user):
	print(f'Attempting to open shoop for {user.id}')
	shoops[str(user.id)] = shoop(user)
	await shoops[str(user.id)].open_shoop()
	
class shoop():
	def __init__(self, user):
		print(f'opened shoop for {user.id}')
		self.user = user
		self.isOpen = True
		
		with open(shoopFile, 'r', encoding='utf-8') as file:
			self.shoopData = json.load(file)
		self.shoopPage = 'main0'
		
		self.shoopMessage = None
		self.view = discord.ui.View()
		
	async def create_button(self, emoji, buttonID, cost, condition = None):
		if cost == 0:
			costDisplay = ''
		else:
			costDisplay = f'{cost}p'


		if cost > data['Players'][str(self.user.id)]['Points']:
			button = discord.ui.Button(label=costDisplay, emoji=emoji, custom_id=str(buttonID), style=ButtonStyle.blurple, disabled=True)
		elif condition != None and await globals().get(condition)(self.user):
			button = discord.ui.Button(label=costDisplay, emoji=emoji, custom_id=str(buttonID), style=ButtonStyle.blurple, disabled=True)
		else:
			button = discord.ui.Button(label=costDisplay, emoji=emoji, custom_id=str(buttonID), style=ButtonStyle.blurple, disabled=False)
			
			
		button.callback = self.button_callback
		
		self.view.add_item(button)
		
	async def button_callback(self, interaction):
		interactionID = interaction.data['custom_id']
		
		if interactionID == '-1' or interactionID == '-2':
			interactionItem = self.shoopData[self.shoopPage]['arrows']['back'] if interactionID == '-1' else self.shoopData[self.shoopPage]['arrows']['next']
			await self.change_page(interactionItem)
		else:
			interactionItem = self.shoopData[self.shoopPage]['fields'][int(interactionID)]
			mainChannel = bot.get_channel(generalChannelID)
			
			if interactionItem['function']['type'] == 'goto':
				change_player_data(self.user.id, 'Points', -interactionItem['function']['cost'])
				await self.change_page(interactionItem['function']['page'])
				
			elif interactionItem['function']['type'] == 'function':
				change_player_data(self.user.id, 'Points', -interactionItem['function']['cost'])
				if interactionItem['function'].get('item', None):
					await globals().get(interactionItem['function']['result'])(self.user, interactionItem['function']['item'])
				else:
					await globals().get(interactionItem['function']['result'])(self.user)
				
				if interactionItem['function']['close']:
					await self.close_shoop()
				else:
					await self.change_page(self.shoopPage)
				
			elif interactionItem['function']['type'] == 'message':
				change_player_data(self.user.id, 'Points', -interactionItem['function']['cost'])
				
				message = random.choice(interactionItem['function']['result'])
				message = re.sub('{user}', data['Players'][str(self.user.id)]['Name'], message)
				
				if interactionItem['function']['main']:
					await mainChannel.send(message)
				else:
					self.user.send(message)
				
				if interactionItem['function']['close']:
					await self.close_shoop()
				else:
					await self.change_page(self.shoopPage)
				
			elif interactionItem['function']['type'] == 'close':
				await self.close_shoop()
							
		await interaction.response.defer()

	async def load_embed(self):
		embed = discord.Embed(
			title = self.shoopData[self.shoopPage]['title'],
			description = self.shoopData[self.shoopPage]['description'],
			color = self.shoopData[self.shoopPage]['color']
		)
		
		if self.shoopData[self.shoopPage]['arrows']['back'] != 'None':
			await self.create_button(shoopArrows[0], -1, 0)
		
		for i, field in enumerate(self.shoopData[self.shoopPage]['fields']):
			name = f"{field['emoji']} {field['name']}"
			value = field['value']
			inline = field['inline']
			cost = field['function'].get('cost', 0)
			condition = field['function'].get('condition', None)
			
			await self.create_button(field['emoji'], i, cost, condition)
			embed.add_field(name=name, value=value, inline=inline)
		
		if self.shoopData[self.shoopPage]['arrows']['next'] != 'None':
			await self.create_button(shoopArrows[1], -2, 0)
			
		
			
		return embed
	
	async def change_page(self, page):
		self.shoopPage = page
		
		del self.view
		self.view = discord.ui.View()
		
		self.shoopMessage = await self.shoopMessage.edit(embed=discord.Embed(title='Loading',description='Please wait'), view=None)
		self.shoopMessage = await self.shoopMessage.edit(embed=await self.load_embed(), view=self.view)
		

	async def open_shoop(self):
		self.shoopMessage = await self.user.send(embed=await self.load_embed(), view=self.view)
	
	async def close_shoop(self):
		await self.shoopMessage.delete()
		self.isOpen = False
		del self

# Shoop Functions
#region

# Music Channels
#region

async def buy_music_channel(user):
	guild = bot.guilds[0]
	category = guild.get_channel(1223029460769439774)
	name = data['Players'][str(user.id)]['Name']
	
	channel = await guild.create_text_channel(name=f"{name}s music top 10", category=category)
	data['Players'][str(user.id)]['MusicChannel'] = channel.id
	
	user_overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
	await channel.set_permissions(user, overwrite=user_overwrite)
	
	everyone_overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=False)
	await channel.set_permissions(guild.default_role, overwrite=everyone_overwrite)
	
	save_data()

async def buy_reset_channel_name(user):
	guild = bot.guilds[0]
	name = data['Players'][str(user.id)]['Name']
	channelId = data['Players'][str(user.id)]['MusicChannel']
	channel = guild.get_channel(channelId)
	
	await channel.edit(name=f"{name}s music top 10")
	
async def check_user_channel_false(user):
	channelId = data['Players'][str(user.id)]['MusicChannel']
	if channelId != 0:
		return False
	else:
		return True
	
async def check_user_channel_true(user):
	channelId = data['Players'][str(user.id)]['MusicChannel']
	if channelId != 0:
		return True
	else:
		return False
	
#endregion

#endregion


# Play sounds
#region

pygame.mixer.init()

loadedSounds = []
soundPath = 'shoop/sounds/'
async def buy_play_sound(user, sound):
	if not os.path.exists(soundPath + sound):
		print("couldnt find file")
		return False
	
	save_data()
	pygame.mixer.music.load(soundPath + sound)
	pygame.mixer.music.play()
	
#endregion

#endregion

#endregion

# Horse
#region

async def dethrone(newMasters, lastMasters):
	main = bot.get_channel(horseChannelID)

	guild = bot.guilds[0]
	role = guild.get_role(# The stable mastery role #)

	newMastersIds = {str(master) for master in newMasters}
	lastMastersIds = {str(master) for master in lastMasters}

	toRemove = lastMastersIds - newMastersIds
	toAdd = newMastersIds - lastMastersIds

	throneLostList = ""
	throneGainList = ""

	for user_id in toRemove:
		member = guild.get_member(int(user_id))
		if member and user_id not in newMasters:
			data['Horse']['Leader'].remove(user_id)
			await member.remove_roles(role)
			throneLostList += f"<@{user_id}> has lost stable mastery!\n"

	for user_id in toAdd:
		member = guild.get_member(int(user_id))
		if member:
			data['Horse']['Leader'].append(user_id)
			await member.add_roles(role)
			throneGainList += f"<@{user_id}> gained stable mastery!\n"

	await main.send(f"{throneLostList}\n"f"{throneGainList}")
	save_data()
	
async def stableMastery(user):
	main = bot.get_channel(horseChannelID)
	leaders = set(data['Horse']['Leader'])

	userPoints = {
		userId: info['total']
		for userId, info in data['Horse'].items()
		if userId != 'Leader'
	}

	sortedUsers = sorted(userPoints.items(), key=lambda x: x[1], reverse=True)

	newLeaders = {str(userId) for userId, points, in sortedUsers if points == sortedUsers[0][1]}

	if newLeaders != set(leaders):
		await dethrone(newLeaders, leaders)


	user_points = data['Horse'].get(str(user.id), {"total": 0})["total"]
	await main.send(f"<@{user.id}> has a total of {user_points} horses!")

async def winHorse(user, items, buyMessage):
	totalWeight = sum(win["weight"] for win in items)
	choice = random.randint(1, totalWeight)

	if str(user.id) not in data["Horse"]:
		data["Horse"][str(user.id)] = {"total": 0, "Horses": {}, "Wins": 0, "Losses": 0, "BigLosses": 0}
	data["Horse"][str(user.id)]["total"] = data["Horse"][str(user.id)].get("total", 0) + 1
	data["Horse"][str(user.id)]["Wins"] = data["Horse"][str(user.id)].get("Wins", 0) + 1

	cumulativeWeight = 0
	for win in items:
		cumulativeWeight += win["weight"]
		if choice <= cumulativeWeight:
			horseType = win["type"]
			if horseType not in data["Horse"][str(user.id)]["Horses"]:
				data["Horse"][str(user.id)]["Horses"][horseType] = 0
			data["Horse"][str(user.id)]["Horses"][horseType] += 1

			await stableMastery(user)

			main = bot.get_channel(horseChannelID)
			message = f"{buyMessage} {win['text']}"
			await main.send(message.format(user=data["Players"][str(user.id)]["Name"]))
			return

async def majorLoseHorse(user, items, buyMessage, horselose):
	message = random.choice(items)

	userHorses = data["Horse"].get(str(user.id), {}).get("Horses", {})

	if not userHorses:
		await loseHorse(user, horselose, buyMessage)
		return
	
	horseType = random.choice(list(userHorses.keys()))

	if userHorses[horseType] > 0:
		userHorses[horseType] -= 1
		if userHorses[horseType] == 0:
			del userHorses[horseType]
		
		data["Horse"][str(user.id)]["BigLosses"] += 1
		data["Horse"][str(user.id)]["total"] -= 1

		await stableMastery(user)

		message = buyMessage + message
		main = bot.get_channel(horseChannelID)
		await main.send(message.format(user=data["Players"][str(user.id)]["Name"], lost=horseType))

async def loseHorse(user, items, buyMessage):
	message = random.choice(items)

	if str(user.id) not in data["Horse"]:
		data["Horse"][str(user.id)] = {"total": 0, "Horses": {}, "Wins": 0, "Losses": 0, "BigLosses": 0}
	data["Horse"][str(user.id)]["Losses"] = data["Horse"][str(user.id)].get("Losses", 0) + 1

	message = buyMessage + message
	main = bot.get_channel(horseChannelID)
	await main.send(message.format(user=data["Players"][str(user.id)]["Name"]))

async def buy_horse(user):
	with open("shoop/horse.json", 'r', encoding='utf-8') as file:
		_data = json.load(file)
		horsebuy = _data["purchase"]
		horsewin = _data["win"]
		horselose = _data["lose"]
		horsemajorlose = _data["majorlose"]

	buyMessage = horsebuy.format(user=data["Players"][str(user.id)]["Name"])

	outcome = random.randint(0, 10)

	if outcome == 0:
		await winHorse(user, horsewin, buyMessage)
	elif outcome == 1:
		await majorLoseHorse(user, horsemajorlose, buyMessage, horselose)
	else:
		await loseHorse(user, horselose, buyMessage)

	save_data()

async def read_horses(horses):
	if not horses or horses == {}:
		return "No horses... What a loser."
	return ", ".join([f"{n}: {v}" for n, v in horses.items()])
@commands.command(name='stable')
async def stable(ctx, targetplayer: discord.Member = None):
	player = ctx.author if targetplayer == None else targetplayer
	
	username = data["Players"][str(player.id)]["Name"]
	userData = data["Horse"][str(player.id)]
	total = f'Current horses: {userData["total"]}'
	wins = f'Total wins: {userData["Wins"]}'
	losses = f'Total losses: {userData["Losses"]}'
	bigLosses = f'Total lost horses: {userData["BigLosses"]}'

	embed = discord.Embed(title=f"{username}'s Stable!", color=discord.Color.red())

	horses = await read_horses(userData["Horses"])
	embed.add_field(name=f"Your stable:", value=horses, inline=False)

	rawStats = f"{total}\n{wins}\n{losses}\n{bigLosses}"
	embed.add_field(name=f"Raw Stats:", value=rawStats, inline=False)

	await ctx.channel.send(embed=embed)
bot.add_command(stable)

@commands.command(name='ss')
async def stable_stadium(ctx):
	leaderboard = ""

	scores = [
		(userId, horseData["total"]) for userId, horseData in data["Horse"].items() if userId != "Leader"
	]
	scores.sort(key=lambda x: x[1], reverse=True)

	for user, horses in scores:
		username = data["Players"][str(user)]["Name"]

		if user in data["Horse"]["Leader"]:
			leaderboard += f"\n👑 {username}:  {horses} "
		elif horses == 0:
			leaderboard += f"\n💀 {username}:  {horses} "
		else:
			leaderboard += f"\n🐴 {username}:  {horses} "

	embed = discord.Embed(title=f"Stable Stadium!", color=discord.Color.red())
	embed.add_field(name=f"", value=leaderboard, inline=False)

	await ctx.channel.send(embed=embed)
bot.add_command(stable_stadium)

@commands.command(name='cheathorse')
async def cheat_horse(ctx, targetplayer: discord.Member = None):
	if ctx.author.id != # USER WITH DEV PERMS #:
		await ctx.send('Fuck you doin lil bro, get you ass outa here')
		return False
	else:
		player = ctx.author if targetplayer == None else targetplayer
			
		await buy_horse(player)
bot.add_command(cheat_horse)

@commands.command(name='recalchorsemastery')
async def recalc_horse_mastery(ctx):
	if ctx.author.id != 309847108444487682:
		await ctx.send('Fuck you doin lil bro, get you ass outa here')
		return False
	else:
		await stableMastery(ctx.author)
bot.add_command(recalc_horse_mastery)

@commands.command(name='daily')
async def getdaily(ctx):
	currentDate = datetime.now().date()
	
	yesterday = currentDate - timedelta(days=1)
	
	if data['Players'][str(ctx.author.id)]['Daily'] == 0:
		data['Players'][str(ctx.author.id)]['Daily'] = yesterday.strftime("%Y-%m-%d")

	daily_date = datetime.strptime(data['Players'][str(ctx.author.id)]['Daily'], "%Y-%m-%d").date()
	
	try:
		if daily_date <= yesterday:
			todayStr = currentDate.strftime("%Y-%m-%d")
			data['Players'][str(ctx.author.id)]['Daily'] = todayStr
			await ctx.send('Daily claimed!')
			await buy_horse(ctx.author)
		else:
			await ctx.send('Shuduh nerd yo shi aint ready yet.')
		save_data()
	except KeyError:
		await ctx.send('Sky fucked up and there is a key error')
		print('Key Error')
	except ValueError:
		await ctx.send('Sky fucked up and the data format is invalid')
		print('Invalid date format')
bot.add_command(getdaily)

#endregion

def quick_embed(title, description, color, fields, footer):
	embed = discord.Embed(
		title=title,
		description=description,
		color=color
	)
	embed.set_footer(text=footer)
	
	for name, value in fields.items():
		embed.add_field(name=name, value=value)

	return embed

# Checks for global use
#region

async def does_channel_exist(channelId):
	return bot.get_channel(channelId) is not None

#endregion

bot.run(token)
