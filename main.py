import discord
from discord.ext import commands
import os
from database import Database
from commands import StockCommands
import logging
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

TOKEN = os.environ['DISCORD_TOKEN']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('stockbot')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    Database.setup()
    await bot.add_cog(StockCommands(bot))
    print('Stock tracker is ready!')
    print('Available commands:')
    print('!stock <ticker> - Get current price')
    print('!alert <ticker> <price> <above/below> - Set price alert')
    print('!addstock <ticker> <shares> - Add to portfolio')
    print('!removestock <ticker> - Remove from portfolio')
    print('!portfolio - View your portfolio')
    print('!updateshares <ticker> <shares> - Update shares')
    print('!news <ticker> - Get latest news')

@bot.event
async def on_command_error(ctx, error):
    logger.error(f'Error: {str(error)}')
    await ctx.send("An error occurred. Please try again.")

if __name__ == "__main__":
    bot.run(TOKEN)

