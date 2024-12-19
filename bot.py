import discord
from discord.ext import commands
from dotenv import load_dotenv

from EloSystem import *
from my_token import *

# Load bot token from .env file
load_dotenv()



# Initialize Elo system
elo_system = EloSystem()

# Set up Discord bot
intents = discord.Intents.default()
intents.messages = True  # Allow the bot to read messages
intents.message_content = True  # Allow access to message content
bot = commands.Bot(command_prefix=">.", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is connected and ready!")

@bot.command(name="record")
@commands.has_role("Overlord Tilt")
async def record_match(ctx, player1: str, player2: str, score1: int, score2: int):
    """Record a match between two players."""
    player1 = player1.strip().lower()
    player2 = player2.strip().lower()
    elo_system.update_ratings(player1, player2, score1, score2)
    await ctx.send(f"Match recorded: {player1} ({score1}) vs {player2} ({score2}). Elo ratings updated!")

@bot.command(name="howmuchelo")
async def how_much_elo(ctx, elo1: float, elo2: float, score1 : int, score2: int):
    await ctx.send("```" + EloSystem.str_elo_change(elo1, elo2, score1, score2) + "```")

@bot.command(name="stats")
async def player_stats(ctx, player: str):
    """Display stats for a specific player."""
    stats = elo_system.calculate_stats_from_history()
    if player not in elo_system.players:
        await ctx.send(f"No data found for player '{player}'.")
        return

    rating = round(elo_system.players[player], 2)
    player_stats = stats[player]
    games = player_stats["games"]
    wins = player_stats["wins"]
    losses = player_stats["losses"]
    draws = player_stats["draws"]
    win_rate = (wins / games * 100) if games > 0 else 0.0

    await ctx.send(
        f"```Stats for {player}:\n"
        f"- Elo Rating: {rating}\n"
        f"- Games Played: {games}\n"
        f"- Wins: {wins}\n"
        f"- Losses: {losses}\n"
        f"- Draws: {draws}\n"
        f"- Win Rate: {win_rate:.2f}%```"
    )

@bot.command(name="leaderboard")
async def leaderboard(ctx):
    """Display the leaderboard of players by Elo rating."""
    leaderboard = sorted(elo_system.players.items(), key=lambda x: x[1], reverse=True)
    message = "Leaderboard:\n```"
    for i, (player, rating) in enumerate(leaderboard, start=1):
        if(i > 10): break
        message += f"{i}. {player}: {round(rating, 2)}\n"
    message += "```"
    await ctx.send(message)

@bot.command(name="leaderboardfull")
@commands.has_permissions(administrator=True)
async def leaderboardfull(ctx):
    """Display the leaderboard of players by Elo rating."""
    leaderboard = sorted(elo_system.players.items(), key=lambda x: x[1], reverse=True)
    message = "Leaderboard:\n```"
    for i, (player, rating) in enumerate(leaderboard, start=1):
        message += f"{i}. {player}: {round(rating, 2)}\n"
    message += "```"
    await ctx.send(message)
# Run the bot
bot.run(TOKEN)
