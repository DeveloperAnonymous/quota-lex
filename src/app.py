import config
import discord, asyncio
from discord.ext import commands
from tinydb import TinyDB, Query
from random import randint

bot = commands.Bot(command_prefix='ql')
db = TinyDB('../db/quotes.json')

async def is_owner(ctx):
    return ctx.author.id == config.OWNER

@bot.event
async def on_ready():
    print('Logged as {0}'.format(bot.user))
    bot.loop.create_task(presence_task())

async def presence_task():
    while True:
        await bot.change_presence(activity=discord.Game("{0} quotes on {1} servers".format(db.count(Query().id.exists()), len(bot.guilds))))
        await asyncio.sleep(60)

@bot.command()
async def quote(ctx, user = None, msg = None):
    nb_quote = db.count(Query().guild == ctx.guild.id)
    if user == None or msg == None:
        quote_id = randint(0, nb_quote-1)
        quote = db.get((Query().id == quote_id) & (Query().guild == ctx.guild.id))
        await ctx.send('{0} a déjà dit : {1}'.format(quote['user'], quote['msg']))
        return

    db.insert({'id': nb_quote, 'user': user, 'msg': msg, 'guild': ctx.guild.id})
    print('[{0}] {1}: {2}'.format(ctx.guild.id, user, msg))
    await ctx.send('La citation a été ajouté au lexique.')

@bot.command()
async def last(ctx):
    nb_quote = db.count(Query().guild == ctx.guild.id)

    last_message = (await ctx.history(limit=2).flatten())[1]
    user = last_message.author.mention
    msg = last_message.content

    db.insert({'id': nb_quote, 'user': user, 'msg': msg, 'guild': ctx.guild.id})
    print('[{0}] {1}: {2}'.format(ctx.guild.id, user, msg))
    await ctx.send('La citation a été ajouté au lexique.')

@bot.command()
@commands.check(is_owner)
async def info(ctx):
    nb_quote = db.count(Query().id.exists())
    nb_guild = len(bot.guilds)
    await ctx.send('Nombre de citations : {0}\nNombre de serveurs : {1}'.format(nb_quote, nb_guild))

@info.error
async def info_error(ctx, error):
    await ctx.send('Pas de tes affaires.')

bot.run(config.TOKEN)