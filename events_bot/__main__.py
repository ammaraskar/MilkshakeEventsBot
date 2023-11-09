import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_guild_available(self, guild):
        print(f"Guild available, {guild.name} {guild.id}")
        for forum in guild.forums:
            print(f"  Forum name: {forum.name}")
            for thread in forum.threads:
                print(f"   Thread: {thread.name}")

    async def on_thread_create(self, thread):
        pass


intents = discord.Intents.default()
intents.guilds = True

client = MyClient(intents=intents)
client.run("")
