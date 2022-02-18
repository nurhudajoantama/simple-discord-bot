import discord
from discord.ext import commands
import psycopg2


class Database():
    def __init__(self, connection):
        self.conn = connection
        self.c = self.conn.cursor()

    def find_res(self, guild_id, command):
        self.c.execute("SELECT * FROM command WHERE guild_id = %s AND command = %s",
                       (guild_id, command))
        return self.c.fetchone()

    def find_all_res(self, guild_id):
        self.c.execute(
            "SELECT * FROM command WHERE guild_id = %s", (guild_id,))
        return self.c.fetchall()

    def create_res(self, guild_id, command, res):
        self.c.execute("INSERT INTO command (guild_id, command, res) VALUES (%s, %s, %s)",
                       (guild_id, command, res))
        self.conn.commit()

    def update_res(self, id, res):
        self.c.execute("UPDATE command SET res = %s WHERE id = %s",
                       (res, id))
        self.conn.commit()

    def delete_res(self, id):
        self.c.execute("DELETE FROM command WHERE id = %s", (id,))
        self.conn.commit()


class CustomCommands(commands.Cog, name='Custom commands'):

    def __init__(self, bot, DB_POOL):
        self.bot = bot
        self.DB_POOL = DB_POOL
        # self.DB = Database(DB_URI)

    @commands.command(name="c", help="Run custom command")
    async def c(self, ctx, arg):
        res = None
        async with ctx.typing():
            connection = self.DB_POOL.getconn()
            DB = Database(connection)
            try:
                db_res = DB.find_res(ctx.guild.id, arg)
            finally:
                self.DB_POOL.putconn(connection)

            if db_res is None:
                res = "command not found"
            else:
                res = db_res[3].replace("[name]", ctx.author.name)
        await ctx.send(res)

    @commands.command(name="clist", help="To list custom commands")
    async def clist(self, ctx):
        res = ''
        async with ctx.typing():
            connection = self.DB_POOL.getconn()
            DB = Database(connection)
            try:
                db_res = DB.find_all_res(ctx.guild.id)
            finally:
                self.DB_POOL.putconn(connection)

            if db_res is None:
                res = "No custom commands found"
            else:
                for command in db_res:
                    res += f"{command[2]} - {command[3]}\n"
        await ctx.send(res)

    @commands.command(name="csave", help="To add or update custom commands")
    async def csave(self, ctx, arg, *args):
        res = ' '.join(args)
        if arg == " " or res == " ":
            await ctx.send("Please fill all the fields")
            return
        respon = ''
        async with ctx.typing():
            connection = self.DB_POOL.getconn()
            DB = Database(connection)
            try:
                db_res = DB.find_res(ctx.guild.id, arg)
                if db_res is None:
                    DB.create_res(ctx.guild.id, arg, res)
                    respon = f"{arg}:{res} Successfully created"
                else:
                    DB.update_res(db_res[0], res)
                    respon = f"{arg}:{res} Successfully updated"
            finally:
                self.DB_POOL.putconn(connection)
        await ctx.send(respon)

    @commands.command(name="crmv", help="To remove saved custom comands")
    async def crmv(self, ctx, arg):
        async with ctx.typing():
            connection = self.DB_POOL.getconn()
            DB = Database(connection)
            db_res = DB.find_res(ctx.guild.id, arg)
            if db_res is None:
                await ctx.send("command not found")
                return
            try:
                DB.delete_res(db_res[0])
            finally:
                self.DB_POOL.putconn(connection)
        await ctx.send(f"{arg} Successfully deleted")
