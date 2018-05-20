import discord
import asyncio
import praw
import prawcore
import codecs
import re

client = discord.Client()
reddit = ""
mincomments = 25
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
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
	elif message.content.startswith("%checkvotes"):
		embed=discord.Embed(title="CMHOC Clerk")
		tmp = message.content.split(" ")[1]
		print(tmp)
		try:
			submission = reddit.submission(url=tmp)
			await countVotes(submission, message)
		except Exception as e:
			embed.add_field(name="Command Failed", value=e.value + " " + e.args, inline=False)
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

async def checkPermissions(user, permrequired):
	if(permrequired == "777"):
		with codecs.open("superusers.txt", "r") as file:
			if(user in file.readlines()):
				return True
			else:
				return False
	else:
		with codecs.open("superusers.txt", "r") as file:
			if(user in file.readlines()):
				return True
			else:
				return False
		with codecs.open("users.txt", "r") as file:
			userperms = [line for line in file.readlines() if user in line]
			perms = userperms.split("=")[3]
			if(int(perms, 2) & int(permrequired, 2) >= int(permrequired, 2)):
				return True
			else:
				return False	

async def countVotes(submission, message):
	embed=discord.Embed(title="CMHOC Clerk")
	votedict = {"Bills": [x.replace("Y", "").replace(": ", "") for x in re.findall("([CSM]\-\d\d:\sY)", submission.selftext)], "Unknown Votes": {}}
	for x in [x.replace("Y", "").replace(": ", "") for x in re.findall("([CSM]\-\d\d:\sY)", submission.selftext)]:
		votedict[x] = {"Yea": 0, "Nay": 0, "Abstain": 0}
	for x in re.findall("((C|S|M)-(\d+):\s)([Yy]ea|[Nn]ay|[Aa]bstain|[Oo]ui|[Nn]on|[Aa]bstention)", "".join([y for y in [x.body.replace("\n", "") for x in submission.comments] if not re.match("^P", y)])):
		if(x[0].replace(": ", "") in votedict["Bills"]):
			if(x[3] in ["Yea", "yea", "Oui", "oui"]):
				votedict[x[0].replace(": ", "")]["Yea"] += 1
			elif(x[3] in ["Nay", "nay", "Non", "non"]):
				votedict[x[0].replace(": ", "")]["Nay"] += 1
			elif(x[3] in ["Abstain", "abstain", "Abstention", "abstention"]):
				votedict[x[0].replace(": ", "")]["Abstain"] += 1
	for x in submission.comments:
		if(re.search("((C|S|M)-(\d+):\s)([Yy]ea|[Nn]ay|[Aa]bstain|[Oo]ui|[Nn]on|[Aa]bstention)", x.body) is None):
			votedict["Unknown Votes"][x.author.name] = x.body
	for x in votedict["Bills"]:
		embed.add_field(name=x, value=x + ": " + str(votedict[x]["Yea"]) + " Yea, " + str(votedict[x]["Nay"]) + " Nay, " + str(votedict[x]["Abstain"]) + " Abstentions", inline=False)
	if(len(votedict["Unknown Votes"]) > 1):
		embed.add_field(name="Unknown Votes Detected", value="Unknown votes have been found. To view them, type %viewunknowns.")
		await client.send_message(message.channel, embed=embed)
		msg = await client.wait_for_message(timeout=15, author=message.author, content="%viewunknowns")
		if(msg is not None):
			embed=discord.Embed(title="CMHOC Clerk")
			for k, v in votedict["Unknown Votes"].items():
				if(k != "AutoModerator"):
					embed.add_field(name=k, value=v)
			await client.send_message(message.channel, embed=embed)
