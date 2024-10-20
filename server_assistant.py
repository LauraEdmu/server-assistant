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

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Configure logging to log to a file
logger = logging.getLogger(__name__) # Create a logger

console_handler = logging.StreamHandler() # Create a console handler
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Create a formatter and set it for the console handler
console_handler.setFormatter(formatter)

logger.addHandler(console_handler) # Add the console handler to the logger

import openai
with open("openai.priv", "r") as key_file:
	api_key = key_file.read().strip()

openai.api_key = api_key

@client.event
async def on_ready():
	await tree.sync()

	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Game("Here to Help!")
	)

help_pattern = re.compile(r'^assistant', re.IGNORECASE)

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	# if help_pattern.search(message.content):


@client.event
async def on_member_join(member):
	try:
		await member.send(
			fr"Welcome to the server, {member.display_name}! "
			"If you need help, please feel free to ask!"
		)

		logger.debug(f"Send onboarding message to {member.display_name}")
	except discord.Forbidden as e:
		logger.error(f'Failed to message {member.name} on join. E: {e}')
	except Exception as e:
		logger.critical(e)




@tree.command(name="help")
async def randexperiment(interaction, question: str):
	await interaction.response.send_message(f"Your question: `{question}` is being processed.")

	system_message = r"""You are Server Assistant. A discord bot designed to be of assistance to discord users.
	You are installed on a server called Pride & Pixels. It is a server for LGBTYS (LGBT Youth Scotland).
	If there are any queries relating to LGBTYS, refer them to one of the admins, or to https://lgbtyouth.org.uk/
	
	You are happy and eager to respond to any query, and keep your answers concise."""

	completion = openai.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": system_message},
			{"role": "user", "content": question}
		]
	)

	
	await interaction.followup.send(completion.choices[0].message.content, wait=True)

@tree.command(name="accessibilityhelp")
async def randexperiment(interaction, question: str):
	await interaction.response.send_message(f"Your question: `{question}` is being processed.")

	system_message = r"""You are Server Assistant. A discord bot designed to be of assistance to discord users.
	You are installed on a server called Pride & Pixels. It is a server for LGBTYS (LGBT Youth Scotland).
	If there are any queries relating to LGBTYS, refer them to one of the admins, or to https://lgbtyouth.org.uk/
	
	You are happy and eager to respond to any query, and keep your answers concise."""

	completion = openai.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": system_message},
			{"role": "user", "content": question}
		]
	)

	speech_file_path = Path(__file__).parent / "speech.mp3"
	response = openai.audio.speech.create(
		model="tts-1",
		voice="shimmer",
		input=completion.choices[0].message.content,
		response_format="mp3"
	)
	response.stream_to_file(speech_file_path)

	audio_file = discord.File("speech.mp3", filename="speech.mp3")
	await interaction.followup.send(completion.choices[0].message.content, wait=True, file=audio_file)

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
