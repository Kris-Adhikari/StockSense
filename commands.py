from discord.ext import commands
from database import Database
import discord
import yfinance as yf
from datetime import datetime
from GoogleNews import GoogleNews


class StockCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_current_price(self, ticker):
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        return None if data.empty else data['Close'][0]

    @commands.command(name='stock')
    async def get_stock_price(self, ctx, ticker: str):
        ticker = ticker.upper()
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')

        if data.empty:
            await ctx.send(f"Could not find stock {ticker}")
            return

        current_price = data['Close'][0]
        open_price = data['Open'][0]
        daily_change = ((current_price - open_price) / open_price) * 100

        color = discord.Color.green() if daily_change >= 0 else discord.Color.red()
        emoji = "\U0001F7E2" if daily_change >= 0 else "\U0001F534"

        embed = discord.Embed(
            title="\U0001F4CA " + ticker + " Stock Info",
            description="Current data for " + ticker,
            color=color,
            timestamp=datetime.now()
        )

        embed.add_field(name="\U0001F4B5 Current Price", value="${:.2f}".format(current_price), inline=True)
        embed.add_field(name="\U0001F4C8 Daily Change", value=emoji + " {:+.2f}%".format(daily_change), inline=True)

        chart_url = "https://finviz.com/chart.ashx?t=" + ticker + "&ty=c&ta=1&p=d&s=l"
        embed.set_image(url=chart_url)
        embed.set_footer(text="Data from Yahoo Finance")

        await ctx.send(embed=embed)

    @commands.command(name='addstock')
    async def add_stock(self, ctx, ticker: str, shares: str):
        if not shares.replace('.', '').isdigit():
            await ctx.send("Shares must be a number!\nExample: !addstock AAPL 10")
            return

        ticker = ticker.upper()
        shares = float(shares)
        current_price = self.get_current_price(ticker)

        if current_price:
            Database.add_stock(str(ctx.author.id), ticker, shares, current_price)
            await ctx.send("Added {} shares of {} at ${:.2f}".format(shares, ticker, current_price))
        else:
            await ctx.send("Could not find stock " + ticker)

    @commands.command(name='portfolio')
    async def view_portfolio(self, ctx):
        user_id = str(ctx.author.id)
        stocks = Database.get_portfolio(user_id)

        if not stocks:
            await ctx.send("Your portfolio is empty!")
            return

        total_value = 0
        total_change = 0

        embed = discord.Embed(
            title="\U0001F4BC " + ctx.author.name + "'s Portfolio",
            description="Your current stock holdings",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        for ticker, shares, buy_price in stocks:
            current_price = self.get_current_price(ticker)
            if not current_price:
                continue

            position_value = shares * current_price
            total_value += position_value
            gain_loss = ((current_price - buy_price) / buy_price) * 100
            total_change += gain_loss

            emoji = "\U0001F4C8" if gain_loss >= 0 else "\U0001F4C9"
            color_emoji = "\U0001F7E2" if gain_loss >= 0 else "\U0001F534"

            embed.add_field(
                name=emoji + " " + ticker,
                value="Shares: {}\n\U0001F4B5 Current: ${:.2f}\n\U0001F4B0 Value: ${:.2f}\n{} {:+.2f}%".format(
                    shares, current_price, position_value, color_emoji, gain_loss
                ),
                inline=True
            )

        last_values = Database.get_last_two_values(user_id)
        if len(last_values) == 2:
            daily_change = ((total_value - last_values[1][0]) / last_values[1][0]) * 100
            daily_change_str = "${:+.2f} ({:+.2f}%)".format(total_value - last_values[1][0], daily_change)
        else:
            daily_change_str = "N/A (First day)"

        Database.update_portfolio_history(user_id, total_value)

        embed.add_field(
            name="\U0001F4CA Portfolio Summary",
            value="\U0001F4B5 Total Value: ${:.2f}\n\U0001F4C8 Daily Change: {}\n{} Overall Change: {:+.2f}%".format(
                total_value, daily_change_str, "\U0001F7E2" if total_change >= 0 else "\U0001F534", total_change / len(stocks)
            ),
            inline=False
        )

        embed.set_footer(text="Updated just now")
        await ctx.send(embed=embed)

    @commands.command(name='removestock')
    async def remove_stock(self, ctx, ticker: str):
        ticker = ticker.upper()
        if Database.remove_stock(str(ctx.author.id), ticker):
            await ctx.send("Removed " + ticker + " from your portfolio")
        else:
            await ctx.send("You don't have " + ticker + " in your portfolio")

    @commands.command(name='news')
    async def get_stock_news(self, ctx, ticker: str):
        ticker = ticker.upper()
        googlenews = GoogleNews(lang='en', region='US')
        googlenews.search(ticker + " stock")
        news = googlenews.result()

        if not news:
            await ctx.send("No news found for " + ticker)
            return

        embed = discord.Embed(
            title="\U0001F4F0 Latest News for " + ticker,
            description="Recent market updates and news",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for i, article in enumerate(news[:5], 1):
            embed.add_field(
                name="\U0001F4CC " + article['title'],
                value="\U0001F517 [Read More]({})\n\U0001F4C5 {}".format(article['link'], article['date']),
                inline=False
            )

        embed.set_footer(text="Data from Google News")
        await ctx.send(embed=embed)
