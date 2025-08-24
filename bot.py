import os, threading, time
import schedule
import discord
from dotenv import load_dotenv
from termcolor import colored
from discord.ext import commands, tasks
from src.tasks import *
from src.posts import *
from src.news import *

# Load environment variables
load_dotenv()
TOKEN = os.getenv('BOT-TOKEN')
GUILD_ID = os.getenv('GUILD-ID')
OWNER_ID = os.getenv('OWNER-ID')

ASTROBOT_PROFILE_ASSET = "https://i.ibb.co/KzD8vrjM/Screenshot-2025-03-27-202917.png"

scheduler = schedule.Scheduler()
scheduler.every().day.at("09:00").do(news)
def run_schedules():
    
    print(colored("Activated news and task schedule", "green"))
    
    while True:
        
        scheduler.run_pending()
        time.sleep(60)
        
t1 = threading.Thread(target=run_schedules)
t1.start()
    
# Initialize Discord bot
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(colored("Bot is online", "green"))
    reminder_loop.start()
    handle_create_task.start()

@bot.slash_command(name="pi", description="just pi")
async def pi(ctx):
    
    await ctx.respond("3.141592653589793238462643")

@bot.slash_command(name="add-member", description="Create new user profile")
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
        
        owner = await bot.fetch_user(OWNER_ID)
        self.embed = discord.Embed(
            title=f"{user.display_name} finished reviewing {self.author.display_name}'s task:\n{self.link}",
            color=self.author.accent_color
        )
        self.embed.set_author(name=user.display_name, icon_url=user.avatar.url)
        self.remove_item(button)
        
        await self.message.edit(embed=self.embed, view=self)
        
        t2 = threading.Thread(target=read_article, args=(extract_doc_id(self.link),))
        t2.start()
        t2.join()

    @discord.ui.button(label="Review", style=discord.ButtonStyle.secondary)
    async def button_callback(self, button, interaction):
        
        await interaction.response.defer()
        
        if button.label == "Review":
            
            await self.update_message_review(interaction.user, button)
            
        elif button.label == "Finished!":
            
            await self.update_message_finished(interaction.user, button)

@bot.slash_command(name="submit", description="Submit your tasks", guild_ids=[GUILD_ID])
async def handle_submit(ctx, link):
    
    submit_channel_id = 1394020514804273163 #1397207767898394755
    submit_channel = bot.get_channel(submit_channel_id)

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

# Run the bot
bot.run(TOKEN)