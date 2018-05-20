import discord
import asyncio
import praw
import prawcore
import codecs
from discord.ext import commands
from discord.ext.commands import Bot
bot = commands.Bot(command_prefix="%")
client = discord.Client()
reddit = ""
mincomments = 25
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
	print('I need poutine')
    print('------')

@client.event
async def on_message(message):
	if message.content.startswith('%verify'):
		await verifyUser(message.content.split(" ")[1], message)
	elif message.content.startswith("%mincomments"):
		embed=discord.Embed(title="CMHOC Clerk")
		tmp = message.content.split(" ")[1]
		if(tmp != "current"):
			global mincomments
			mincomments = tmp
			embed.add_field(name="Minimum Comments Required", value="✅ Minimum comments required for verification is now " + str(tmp) + ".", inline=False)
			await client.send_message(message.channel, embed=embed)
		else:
			embed.add_field(name="Minimum Comments Required", value="Minimum comments required for verification is currently " + str(mincomments) + ".", inline=False)
			await client.send_message(message.channel, embed=embed)
	elif message.content.startswith("%adduserpair"):
		embed=discord.Embed(title="CMHOC Clerk")
		tmp = message.content.split(" ")[2]
		tmp2 = message.mentions[0]
		if(len(message.content.split(" ")) == 4):
			with codecs.open("users.txt", "a") as file:
				file.write(tmp2.id + "=" + tmp + "=" + format(int(message.content.split(" ")[3]), "#010b") + "\r\n")
				embed.add_field(name="Userpair Database", value="✅ User " + tmp2.name + " added under reddit name " + tmp + " with perm matrix " + format(int(message.content.split(" ")[3]), "#010b") + " .", inline=False)
		else: 
			with codecs.open("users.txt", "a") as file:
				file.write(tmp2.id + "=" + tmp + "=" + format(0, "#010b") + "\r\n")
				embed.add_field(name="Userpair Database", value="✅ User " + tmp2.name + " added under reddit name " + tmp + " with perm matrix " + format(0, "#010b") + " .", inline=False)
		await client.send_message(message.channel, embed=embed)
			
def startBot(cid, secret, password, username, token):
	global reddit
	reddit = praw.Reddit(client_id=cid, client_secret=secret, password=password, user_agent="CMHOC Clerk Prototype", username=username)
	client.run(token)
	
async def verifyUser(user, message):
	try:
		tmp2 = reddit.redditor(name=user)
		counter = 0
		embed=discord.Embed(title="CMHOC Clerk")
		for x in tmp2.comments.new(limit=None):
			if(x.subreddit.display_name == "cmhoc"):
				counter += 1
		if(counter >= 25):
			embed.add_field(name="Verification Tool", value="✅ User " + user + " verified.", inline=False)
		else:
			embed.add_field(name="Verification Tool", value="❌ User " + user + " not verified.", inline=False)
		await client.send_message(message.channel, embed=embed)
	except prawcore.NotFound as e:
		embed.add_field(name="Command Failed", value="❌ User " + user + " does not exist on Reddit (or is shadowbanned.)")
		await client.send_message(message.channel, embed=embed)
			embed=discord.Embed(title="CMHOC Clerk")
			for x in tmp2.comments.new(limit=None):
				if(x.subreddit.display_name == "cmhoc"):
					counter += 1
			if(counter >= 25):
					embed.add_field(name="Verification Tool", value="✅ User " + user + " verified.", inline=False)
			else:
					embed.add_field(name="Verification Tool", value="❌ User " + user + " not verified.", inline=False)
			await client.send_message(message.channel, embed=embed)

				if(x.subreddit.display_name == "cmhoc"):
					counter += 1
			if(counter >= 25):
					embed.add_field(name="Verification Tool", value="✅ User " + user + " verified.", inline=False)
			else:
					embed.add_field(name="Verification Tool", value="❌ User " + user + " not verified.", inline=False)
			await client.send_message(message.channel, embed=embed)

bot.command(pass_context=true)
async def wikipedia(ctx,*,args):
	    if args=="help":
        embed=discord.Embed(title="the Wikipedia Function",color=0xe198ff)
        embed=add_field(name="How to wiki",value="Just type the word you want to search after $wikipedia.",inline=True)
        await bot.say(embed=embed)
    else:
        await bot.say("http://wikipedia.org/wiki/"+args.replace(" ","_"))