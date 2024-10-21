import discord
from discord import app_commands
import json
import logging
import aiofiles
import datetime
from collections import defaultdict
import os
import re
from datetime import timedelta
from pathlib import Path

needed_intents = discord.Intents.default()
needed_intents.message_content = True
needed_intents.members = True
client = discord.Client(intents=needed_intents)
tree = app_commands.CommandTree(client)

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Configure logging to log to a file
logger = logging.getLogger(__name__) # Create a logger

console_handler = logging.StreamHandler() # Create a console handler
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Create a formatter and set it for the console handler
console_handler.setFormatter(formatter)

logger.addHandler(console_handler) # Add the console handler to the logger

import openai
with open("openai.priv", "r") as key_file:
	api_key = key_file.read().strip()

openai.api_key = api_key

logger.debug("Read the API key, and passed it to the openai object")

@client.event
async def on_ready():
	await tree.sync()

	game="Here to Help!"
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Game(game)
	)

	logger.debug(f"Performed on ready actions (setting online and game status = {game})")


@client.event
async def on_message(message):
	if message.author == client.user:
		return

# @client.event
# async def on_member_join(member):
# 	try:
# 		await member.send(
# 			fr"Welcome to the server, {member.display_name}! "
# 			"If you need help, please feel free to ask!"
# 		)

# 		logger.debug(f"Send onboarding message to {member.display_name}")
# 	except discord.Forbidden as e:
# 		logger.error(f'Failed to message {member.name} on join. E: {e}')
# 	except Exception as e:
# 		logger.critical(e)




@tree.command(name="help")
async def randexperiment(interaction, question: str):
	await interaction.response.send_message(f"Your question: `{question}` is being processed.")
	logger.debug("Initial help response, alerting user that the question is being processed")

	file_path = os.path.join("chat_history", f"chat_system")
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			system_message = f.read().strip()
			logger.debug(f"Read system message: {system_message}")
	else:
		logger.critical(f"Missing system message at {file_path}")
		await interaction.response.followup.send("Could not find system message!", ephemeral=True)
		return

	completion = openai.chat.completions.create(
		model="gpt-4o",
		messages=[
			{"role": "system", "content": system_message},
			{"role": "user", "content": question}
		]
	)

	logger.debug(f"Completion complete with a {len(completion.choices[0].message.content)} character response (~{len(completion.choices[0].message.content)/4}) tokens")
	
	await interaction.followup.send(completion.choices[0].message.content, wait=True)
	logger.debug("Sent resopnse to user")

	# estimated cost for gpt-4o
	logger.debug(f"Estimated Cost: ${((len(completion.choices[0].message.content)/4)*0.0000025)}")

@tree.command(name="accessibilityhelp") # TODO: read in system message from file & add logging
async def randexperiment(interaction, question: str):
	await interaction.response.send_message(f"Your question: `{question}` is being processed.")
	logger.debug("Initial help response, alerting user that the question is being processed")

	file_path = os.path.join("chat_history", f"chat_system")
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			system_message = f.read().strip()
			logger.debug(f"Read system message: {system_message}")
	else:
		logger.critical(f"Missing system message at {file_path}")
		await interaction.response.followup.send("Could not find system message!", ephemeral=True)
		return

	completion = openai.chat.completions.create(
		model="gpt-4o",
		messages=[
			{"role": "system", "content": system_message},
			{"role": "user", "content": question}
		]
	)

	logger.debug(f"Completion complete with a {len(completion.choices[0].message.content)} character response (~{len(completion.choices[0].message.content)/4}) tokens")
	
	speech_file_path = Path(__file__).parent / "speech.mp3"
	response = openai.audio.speech.create(
		model="tts-1",
		voice="shimmer",
		input=completion.choices[0].message.content,
		response_format="mp3"
	)
	response.stream_to_file(speech_file_path)

	logger.debug("Recieved speech response")

	audio_file = discord.File("speech.mp3", filename="speech.mp3")
	await interaction.followup.send(completion.choices[0].message.content, wait=True, file=audio_file)

	# estimated cost for gpt-4o and tts-1
	logger.debug(f"Sent all info to user. Estimated Cost: ${((len(completion.choices[0].message.content)/4)*0.0000025)+(len(completion.choices[0].message.content)*0.000015)}")

# @tree.command(name="accessibilityhelp") # TODO: read in system message from file & add logging
# async def randexperiment(interaction, question: str):
# 	await interaction.response.send_message(f"Your question: `{question}` is being processed.")

# 	system_message = r"""You are Server Assistant. A discord bot designed to be of assistance to discord users.
# 	You are installed on a server called Pride & Pixels. It is a server for LGBTYS (LGBT Youth Scotland).
# 	If there are any queries relating to LGBTYS, refer them to one of the admins, or to https://lgbtyouth.org.uk/
	
# 	You are happy and eager to respond to any query, and keep your answers concise."""

# 	completion = openai.chat.completions.create(
# 		model="gpt-4o-mini",
# 		messages=[
# 			{"role": "system", "content": system_message},
# 			{"role": "user", "content": question}
# 		]
# 	)

# 	speech_file_path = Path(__file__).parent / "speech.mp3"
# 	response = openai.audio.speech.create(
# 		model="tts-1",
# 		voice="shimmer",
# 		input=completion.choices[0].message.content,
# 		response_format="mp3"
# 	)
# 	response.stream_to_file(speech_file_path)

# 	audio_file = discord.File("speech.mp3", filename="speech.mp3")
# 	await interaction.followup.send(completion.choices[0].message.content, wait=True, file=audio_file)

if __name__ == '__main__':
	logger.debug("Starting bot")
	try:
		with open("key.priv", 'r') as token_file:
			token = token_file.read()
		logger.debug("Read token")
		
		client.run(token)
	except FileNotFoundError:
		logger.critical("Could not find token")
	except Exception as e:
		logger.critical(e)
