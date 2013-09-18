#--------------------#
#   LinkFixerBotSnr  #
# By /u/WinneonSword #
#--------------------#

import praw, time, sys, os, json, re
from warnings import filterwarnings

filterwarnings("ignore", category = DeprecationWarning)
filterwarnings("ignore", category = ResourceWarning)

def loadConfig():
	config = json.loads(open('config.json').read())
	return config

config = loadConfig()
version = "v1.0"

userAgent = (
			"/u/WinneonSword's very own /u/LinkFixerBotSnr," + version +
			"For more info: http://github.com/WinneonSword/LinkFixerBotSnr"
)

cache = []

rFind = re.compile(' r/[A-Za-z0-9]+')
uFind = re.compile(' u/[A-Za-z0-9]+')

bannedSubs = set()
bannedSubs.add('loans')

def handleRateLimit(func, *args):
	while True:
		try:
			func(*args)
			break
		except praw.errors.RateLimitExceeded as error:
			print("\tRate Limit exceeded! Sleeping for %d seconds to comply with the Reddit API..." % error.sleep_time)
			time.sleep(error.sleep_time)

def checkComment(comment):
	text = comment.body
	broken = set(re.findall(rFind, text))
	broken.union( set(re.findall(uFind, text)) )
	condition = False
	if broken:
		condition = True
	return condition, broken

def postComment(comment, text):
	print("\tFound valid comment at comment id '" + comment.id + "'! Fixing broken link...")
	message = ''
	for char in text:
		message += "/" + char[1:] + "\n"
	reply = (
				"" + message + "\n\n"
				"*****" + "\n\n"
				"^This ^bot ^is ^a ^fill-in ^for ^/u/LinkFixerBot2 ^until ^it ^gets ^back ^up ^and ^running. ^If ^you ^have ^any ^problems, ^then ^feel ^free ^to ^contact ^/u/WinneonSword."
	)
	handleRateLimit(comment.reply, reply)
	print("\tComment posted! Fixed link: " + message)

def main():
	username = config['reddit']['username']
	password = config['reddit']['password']
	print("[ wsLFB ] - Attempting to connect & login to Reddit...")
	try:
		r = praw.Reddit(user_agent = userAgent)
		r.login(username, password)
		print("\tSuccessfully connected & logged in to Reddit!")
	except:
		print("\tCould not connect to Reddit. Check reddit.com or your config for errors.")
		sys.exit()
	try:
		while True:
			print("[ wsLFB ] - Fetching new comments...")
			comments = r.get_comments('all', limit = 500)
			for c in comments:
				botMet, text = checkComment(c)
				if botMet:
					if c.subreddit.display_name not in bannedSubs:
						print("\tFound valid comment at comment id '" + c.id + "'! Fixing broken link...")
						postComment(c, text)
					else:
						print("\tThe comment found is in the banned subreddit '" + c.subreddit.display_name + "'! Skipping...")
			print("\tFinished checking comments! Sleeping for 30 seconds...")
			time.sleep(30)
	except KeyboardInterrupt:
		print("[ wsLFB ] - Stopped LinkFixerBotSnr!")