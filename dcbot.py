import discord
import os
import config
import fmt
import tempfile

from pathlib import Path
from dotenv import load_dotenv

from depl import deployer


load_dotenv()

TOKEN: str = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged {client.user}')


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    match message.channel.name:
        case config.SUBMIT_CHANNEL:
            for attachment in message.attachments:
                if Path(attachment.filename).suffix == ".wasm":
                    await message.channel.send(fmt.info(f"downloading submission `{attachment.filename}`"))

                    try:
                        with tempfile.NamedTemporaryFile(dir=config.DOWNLOAD_PATH) as f:
                            await attachment.save(f.name)
                            deployer.BotSandbox(f.name)

                            
                        await message.channel.send(fmt.success(f"successfully downloaded and verified `{attachment.filename}`"))

                    except Exception as e:
                        await message.channel.send(fmt.error(str(e)))


    for attachment in message.attachments:
        pass

client.run(TOKEN)
