import discord
import asyncio
import praw
import codecs

client = discord.Client()
reddit = praw.Reddit(client_id="client_id", client_secret="client_secret", password="password", user_agent="CMHOC Clerk Prototype", username="username")
mincomments = 25
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#note: write command to lookup user by reddit username when using bot account

@client.event
async def on_message(message):
	if message.author.id == "174827375639396352":
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
			tmp = message.content.split(" ")[2]
			tmp2 = message.mentions[0]
			with codecs.open("users.txt", "a") as file:
				file.write(tmp2.id + "=" + tmp + "\r\n")
			embed=discord.Embed(title="CMHOC Clerk")
			embed.add_field(name="Userpair Database", value="✅ User " + tmp2.name + " added under reddit name " + tmp + ".", inline=False)
			await client.send_message(message.channel, embed=embed)
			
def startBot():
	client.run("email", "password")
	
async def verifyUser(user, message):
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
