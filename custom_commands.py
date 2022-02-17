import discord
from discord.ext import commands
import sqlite3


class Database():
    def __init__(self, DB_URI):
        self.DB_URI = DB_URI
        self.conn = sqlite3.connect(self.DB_URI)
        self.c = self.conn.cursor()
        self.c.execute(
            'CREATE TABLE IF NOT EXISTS commands (id INTEGER PRIMARY KEY, guild_id BIGINT, command VARCHAR, res TEXT)')

    def find_res(self, guild_id, command):
        self.c.execute("SELECT * FROM commands WHERE guild_id = ? AND command = ?",
                       (guild_id, command))
        return self.c.fetchone()

    def find_all_res(self, guild_id):
        self.c.execute(
            "SELECT * FROM commands WHERE guild_id = ?", (guild_id,))
        return self.c.fetchall()

    def create_res(self, guild_id, command, res):
        self.c.execute("INSERT INTO commands (guild_id, command, res) VALUES (?, ?, ?)",
                       (guild_id, command, res))
        self.conn.commit()

    def update_res(self, id, res):
        self.c.execute("UPDATE commands SET res = ? WHERE id = ?",
                       (res, id))
        self.conn.commit()

    def delete_res(self, id):
        self.c.execute("DELETE FROM commands WHERE id = ?", (id,))
        self.conn.commit()


class CustomCommands(commands.Cog, name='Custom commands'):

    def __init__(self, bot, DB_URI):
        self.bot = bot
        self.DB = Database(DB_URI)

    @commands.command(name="c", help="Run custom command")
    async def c(self, ctx, arg):
        db_res = self.DB.find_res(ctx.guild.id, arg)
        if db_res is None:
            await ctx.send("command not found")
            return
        res = db_res[3].replace("[name]", ctx.author.name)
        await ctx.send(res)

    @commands.command(name="clist", help="To list custom commands")
    async def clist(self, ctx):
        db_res = self.DB.find_all_res(ctx.guild.id)
        if db_res is None:
            await ctx.send("No custom commands found")
            return
        res = ""
        for command in db_res:
            res += f"{command[2]} - {command[3]}\n"
        await ctx.send(res)

    @commands.command(name="csave", help="To add or update custom commands")
    async def csave(self, ctx, arg, *args):
        res = ' '.join(args)
        if arg == " " or res == " ":
            await ctx.send("Please fill all the fields")
            return

        db_res = self.DB.find_res(ctx.guild.id, arg)
        if db_res is None:
            self.DB.create_res(ctx.guild.id, arg, res)
            await ctx.send(f"{arg}:{res} Successfully created")
            return
        self.DB.update_res(db_res[0], res)
        await ctx.send(f"{arg}:{res} Successfully updated")

    @commands.command(name="crmv", help="To remove saved custom comands")
    async def crmv(self, ctx, arg):
        db_res = self.DB.find_res(ctx.guild.id, arg)
        if db_res is None:
            await ctx.send("command not found")
            return
        self.DB.delete_res(db_res[0])
        await ctx.send(f"{arg} Successfully deleted")
