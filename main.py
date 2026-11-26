import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from prompt_gemini import prompt_gemini_async

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
owner_id = int(os.getenv('OWNER_ID'))

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# secret_role = "Gamer"

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == bot.user:
        return

    # Let !commands go to the command handler instead of Gemini
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # Send whatever the owner writes to Gemini and reply with its answer
    if message.author.id == owner_id and message.content.strip():
        async with message.channel.typing():
            try:
                reply = await prompt_gemini_async(message.content)
            except Exception as e:
                logging.exception("Gemini request failed")
                await message.reply(f"Sorry, something went wrong talking to Gemini: {e}")
                return

        if not reply.strip():
            reply = "(Gemini returned an empty response)"

        # Discord messages are capped at 2000 characters, so send in chunks
        for i in range(0, len(reply), 2000):
            await message.reply(reply[i:i + 2000])

# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server {member.name}")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if "shit" in message.content.lower():
#         await message.delete()
#         await message.channel.send(f"{message.author.mention} - dont use that word!")
 
#     await bot.process_commands(message)

# @bot.command()
# async def hello(ctx):
#     await ctx.send(f"Hello {ctx.author.mention}!")

# @bot.command()
# async def assign(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=secret_role)
#     if role:
#         await ctx.author.add_roles(role)
#         await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
#     else:
#         await ctx.send("Role doesn't exist")

# @bot.command()
# async def remove(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=secret_role)
#     if role:
#         await ctx.author.remove_roles(role)
#         await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
#     else:
#         await ctx.send("Role doesn't exist")

# @bot.command()
# async def dm(ctx, *, msg):
#     await ctx.author.send(f"You said {msg}")

# @bot.command()
# async def reply(ctx):
#     await ctx.reply("This is a reply to your message!")

# @bot.command()
# async def poll(ctx, *, question):
#     embed = discord.Embed(title="New Poll", description=question)
#     poll_message = await ctx.send(embed=embed)
#     await poll_message.add_reaction("👍")
#     await poll_message.add_reaction("👎")

# @bot.command()
# @commands.has_role(secret_role)
# async def secret(ctx):
#     await ctx.send("Welcome to the club!")

# @secret.error
# async def secret_error(ctx, error):
#     if isinstance(error, commands.MissingRole):
#         await ctx.send("You do not have permission to do that!")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)