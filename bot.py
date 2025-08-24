import os, threading, time, re
import asyncio
import discord
from dotenv import load_dotenv
from termcolor import colored
from multiprocessing import Process
from discord.ext import commands, tasks
from src.tasks import *
from src.news import *

# Load environment variables
load_dotenv()
TOKEN = os.getenv('BOT-TOKEN')
GUILD_ID = os.getenv('GUILD-ID')
OWNER_ID = os.getenv('OWNER-ID')
BLOG_ID = os.getenv('BLOG-ID')
POSTS_ID = os.getenv('POSTS-ID')

ASTROBOT_PROFILE_ASSET = "https://i.ibb.co/KzD8vrjM/Screenshot-2025-03-27-202917.png"

# Initialize Discord bot
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(colored("Bot is online", "green"))
    # reminder_loop.start()
    # handle_create_task.start()

@bot.slash_command(name="pi", description="just pi")
async def pi(ctx):
    
    await ctx.respond("3.141592653589793238462643")

@bot.slash_command(name="add-member", description="Create new user profile", guild_ids=[GUILD_ID])
@discord.default_permissions(administrator=True)
async def handle_add_member(ctx, member: discord.Member):
    
    add_member(member.display_name)

    member_embed = discord.Embed(
        title=f"Added user {member.display_name}",
        color=member.accent_color
    )

    member_embed.set_author(name="Astrobot", icon_url=ASTROBOT_PROFILE_ASSET)
    member_embed.set_thumbnail(url=member.avatar)

    await ctx.respond(embed=member_embed)
    
@bot.slash_command(name="news", description="Command to start news", guild_ids=[GUILD_ID])
@discord.default_permissions(administrator=True)
async def handle_news(ctx):
    posts_owner = await bot.fetch_user(POSTS_ID)
    await ctx.defer()
    
    await news()
    
    await ctx.followup.send("Posted news for today, check back in 24hrs for particle to update")
    for news_article in os.listdir("data/out/articles/"):
        await posts_owner.send(f"Here's the files to post on insta for {news_article}:",\
            files=[discord.File(f"data/out/articles/{news_article}/{image}") \
                for image in os.listdir(f"data/out/articles/{news_article}/") \
                    if image.endswith('.png')])

    await posts_owner.send("Tysmmmmmmmmmmmmmm - Decrescent")
    
@tasks.loop(hours=14*24)
async def handle_create_task():
            
    announcement_channel_id = 1393901179490275491
    active_role_id = 1393515184072691794
    announcement_channel = bot.get_channel(announcement_channel_id)
    create_task_embed = discord.Embed(
                title="Announcement!",
                description = f"<@&{active_role_id}> new tasks assigned",
            )
    create_task_embed.set_author(name="Astrobot", icon_url=ASTROBOT_PROFILE_ASSET)
    create_task()
    await announcement_channel.send(embed = create_task_embed)
        
@tasks.loop(hours=12*24)
async def reminder_loop():
    announcement_channel_id = 1393901179490275491
    active_role_id = 1393515184072691794
    announcement_channel = bot.get_channel(announcement_channel_id)
    create_task_embed = discord.Embed(
                title="Announcement!",
                description = f"<@&{active_role_id}> Tasks due in 2 days",
            )
    create_task_embed.set_author(name="Astrobot", icon_url=ASTROBOT_PROFILE_ASSET)
    await announcement_channel.send(embed = create_task_embed)

@bot.slash_command(name="view-task", description="View your assigned tasks")
async def handle_view_task(ctx):
    
    try:
        
        if check_submit(ctx.author.display_name) == False:
            
            if check_due(ctx.author.display_name) > 0:
                task_embed = discord.Embed(
                    title=view_task(ctx.author.display_name),
                    color=ctx.author.accent_color
                )
                task_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
                
                await ctx.respond(embed=task_embed)
                
            else:
                
                overdue_embed = discord.Embed(
                    title="Your task is overdue!",
                    color=ctx.author.accent_color
                )
                overdue_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
                
                await ctx.respond(embed=overdue_embed)
        else:
            
            submitted_embed = discord.Embed(
                title="You've submitted your task! Nothing to do for now.",
                color=ctx.author.accent_color
            )
            submitted_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
            
            await ctx.respond(embed=submitted_embed)

    except FileNotFoundError:
        
        error_embed = discord.Embed(
            title="Oops! You're not a registered member.",
            color=ctx.author.accent_color
        )
        error_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
        
        await ctx.respond(embed=error_embed)

class ButtonView(discord.ui.View):
    
    def __init__(self, ctx, link):
        
        super().__init__(timeout=None)
        self.author = ctx.author
        self.link = link
        self.embed = discord.Embed(
            title=f"{self.author.display_name} submitted for review:\n{self.link}",
            color=self.author.accent_color
        )
        self.embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)

    async def update_message_review(self, user, button):
        
        self.embed = discord.Embed(
            title=f"{self.author.display_name}'s task under review by {user}:\n{self.link}",
            color=self.author.accent_color
        )
        self.embed.set_author(name=user.name, icon_url=user.avatar.url)
        button.style = discord.ButtonStyle.success
        button.label = "Finished!"
        
        await self.message.edit(embed=self.embed, view=self)

    async def update_message_finished(self, user, button):
        
        blog_owner = await bot.fetch_user(BLOG_ID)
        self.embed = discord.Embed(
            title=f"{user.display_name} finished reviewing {self.author.display_name}'s task:\n{self.link}",
            color=self.author.accent_color
        )
        self.embed.set_author(name=user.display_name, icon_url=user.avatar.url)
        self.remove_item(button)
        
        await self.message.edit(embed=self.embed, view=self)
        await blog_owner.send(f'Please post this on medium:\n{self.link}\n(Thank youuuuuuuuuuuuuuuuuuuuuu - Decrescent)')

    @discord.ui.button(label="Review", style=discord.ButtonStyle.secondary)
    async def button_callback(self, button, interaction):
        
        await interaction.response.defer()
        
        if button.label == "Review":
            
            await self.update_message_review(interaction.user, button)
            
        elif button.label == "Finished!":
            
            await self.update_message_finished(interaction.user, button)

@bot.slash_command(name="submit", description="Submit your tasks", guild_ids=[GUILD_ID])
async def handle_submit(ctx, link):
    
    submit_channel_id = 1397207767898394755
    submit_channel = bot.get_channel(submit_channel_id)

    def extract_doc_id(url):
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        else:
            return None

    if extract_doc_id(link):
        
        submit_task(ctx.author.display_name)

        submitted_embed = discord.Embed(
            title="Submitted your task!",
            color=ctx.author.accent_color
        )
        submitted_embed.set_author(name="Astrobot", icon_url=ASTROBOT_PROFILE_ASSET)

        await ctx.respond(embed=submitted_embed)

        button_view = ButtonView(ctx, link)
        
        await submit_channel.send(embed=button_view.embed, view=button_view)
        
    else:
        
        await ctx.respond("That link does not work!")
    
@bot.slash_command(name="add-topics", description="Create new topics for blogs or roundups")
@discord.default_permissions(administrator=True)
async def handle_add_topics(ctx, ttype, name):
    
    t4 = threading.Thread(target=add_topics, args=(ttype, name))
    t4.start()
    t4.join()
    
    member_embed = discord.Embed(
        title=f"Added new topic!",
    )

    member_embed.set_author(name="Astrobot", icon_url=ASTROBOT_PROFILE_ASSET)

    await ctx.respond(embed=member_embed)

if __name__ == "__main__":
# Run the bot
    bot.run(TOKEN)
    news_loop.start()