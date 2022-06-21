from cmath import e
import datetime
import json
import discord
from discord.ext import commands
from asyncio import sleep
import helper as h

json_data = json.load(open("settings.json"))

bot = commands.Bot(command_prefix=json_data["prefix"], strip_after_prefix=True, case_insensitive=True, intents=discord.Intents.all())
bot.remove_command("help")

@bot.event
async def on_ready():
    print("Ready!")
    while True:
        for i in h.do_to_database("SELECT * FROM users"):
            setts = h.do_to_database("SELECT * FROM guilds_settings WHERE guild_id=?", i[1])[0]
            if (datetime.date.today().month == i[2].month and datetime.date.today().day == i[2].day) and datetime.datetime.time(datetime.datetime.now()) == setts[3]:
                await bot.get_guild(i[1]).get_channel(i[setts[1]]).send(setts[2].replace("{user}", bot.get_user(i[0]).mention))
        await sleep(10)

@bot.event
async def on_guild_join(guild: discord.Guild):
    egg = json_data["default"]["guilds_settings"]
    k = map(int, egg['celebrate_time'].split(":"))
    h.do_to_database("INSERT INTO guilds_settings VALUES (?, ?, ?, ?)", guild.id, egg["channel"], egg["message"], datetime.time(hour=k[0], minute=k[1]), False)
    del egg, k

@bot.command()
async def set_birthday(ctx: commands.Context, date: str, memb: discord.Member = None):
    if memb == None: memb = ctx.author
    k = map(int, date.split("."))
    h.do_to_database("INSERT INTO users VALUES (?, ?, ?)", memb.id, ctx.guild.id, datetime.date(month="", day=""))

@bot.command()
@commands.has_permissions(administrator=True)
async def setting(ctx: commands.Context):
    setts = h.do_to_database("SELECT * FROM guilds_settings WHERE guild_id=?", ctx.guild.id)[0]
    emb = h.embed_builder("Your settings")
    emb.add_field(name="id", value=str(setts[0]))
    emb.add_field(name="🎚️ channel", value=str(bot.get_channel(setts[1]).name))
    emb.add_field(name="✉️ message", value=str(setts[2]))
    emb.add_field(name="🕛 celebrate time", value=str(setts[3]))
    mess = await ctx.send(embed=emb)
    mess.add_reaction('🎚️')
    mess.add_reaction('✉️')
    mess.add_reaction('🕛')
    del mess
    reaction, _ = bot.wait_for("reaction_add", check=lambda reaction, user: reaction.emoji in ('✉️', '🎚️', '🕛') and user == ctx.author)
    if reaction.emoji == "🎚️":
        await ctx.send("Please, enter id of the channel where notifications will be sent")
        mess = bot.wait_for('message', check=lambda message: message.author == ctx.author)
        h.do_to_database("UPDATE guilds_settings SET channel=? WHERE guild_id=?", int(mess.content), ctx.guild.id)
        return await mess.add_reaction("👍")
    if reaction.emoji == "✉️":
        await ctx.send("Please, enter the new message that will be used in the notifications({user} replaced to birthday ping)")
        mess = bot.wait_for('message', check=lambda message: message.author == ctx.author)
        h.do_to_database("UPDATE guilds_settings SET message=? WHERE guild_id=?", mess.content, ctx.guild.id)
        return await mess.add_reaction("👍")
    if reaction.emoji == "🕛":
        now = datetime.datetime.time(datetime.datetime.now())
        await ctx.send(f"Please, enter the time(hour:minute format) in the bot's timezone. Now is {now.hour}:{now.minute}")
        mess = bot.wait_for('message', check=lambda message: message.author == ctx.author)
        t = datetime.time()
        t.hour, t.minute = map(int, mess.content.split(":"))
        h.do_to_database("UPDATE guilds_settings SET clebrate_time=? WHERE guild_id=?", t, ctx.guild.id)

bot.run(json_data['token'])