#######################################
# LinkFixerBotSnr, by /u/WinneonSword #
#######################################
import praw, time, sys, os, json, re, getpass
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
bannedSubs.add('Loans')
bannedSubs.add('nba')
bannedSubs.add('aww')
bannedSubs.add('SubredditDrama')
bannedSubs.add('againstmensrights')
bannedSubs.add('australia')
bannedSubs.add('ShitPoliticsSays')
bannedSubs.add('Scotch')
bannedSubs.add('metacananda')
bannedSubs.add('news')
bannedSubs.add('nfl')
bannedSubs.add('breakingbad')
bannedSubs.add('TheRedPill')
bannedSubs.add('whatisthisthing')
bannedSubs.add('conspiratard')
bannedSubs.add('comics')

prohibitedSubs = set()
prohibitedSubs.add('gonewild')
prohibitedSubs.add('GoneWildPlus')
prohibitedSubs.add('NSFW')

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
		message += "/" + char[1:]
		if message.endswith(comment.subreddit.display_name):
			print("\tThe broken link is the same as the subreddit! Skipping...")
			return
		if (any(message.endswith(x) for x in prohibitedSubs)):
			print("\tThe broken link is a prohibited subreddit! Skipping...")
			return
	reply = (
			"" + message + "\n\n"
			"*****" + "\n\n"
			"^This ^is ^an [^automated ^bot](http://github.com/WinneonSword/LinkFixerBotSnr)^. ^For ^reporting ^problems, ^contact ^/u/WinneonSword."
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
			comments = r.get_all_comments(limit = 500)
			for c in comments:
				botMet, text = checkComment(c)
				if botMet:
					if c.subreddit.display_name not in bannedSubs:
						print("\tFound valid comment at comment id '" + c.id + "'! Fixing broken link...")
						try:
							postComment(c, text)
						except:
							print("\tCould not post comment! Check reddit.com for errors.")
					else:
						print("\tThe comment found is in the banned subreddit '" + c.subreddit.display_name + "'! Skipping...")
			print("\tFinished checking comments! Sleeping for 30 seconds...")
			time.sleep(30)
	except KeyboardInterrupt:
		print("[ wsLFB ] - Stopped LinkFixerBotSnr!")
