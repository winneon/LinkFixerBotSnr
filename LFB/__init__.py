#######################################
# LinkFixerBotSnr, by /u/WinneonSword #
#######################################
import praw, time, sys, os, json, re, getpass
from warnings import filterwarnings

filterwarnings("ignore", category = DeprecationWarning)
filterwarnings("ignore", category = ResourceWarning)

# Loads the config.json file when called. #
def loadConfig():
	config = json.loads(open('config.json').read())
	return config

# Loads the config with the loadConfig() function, and then defines the bot version. #
config = loadConfig()
version = "v1.1"

# The user agent that is sent to Reddit when fetching information. #
userAgent = (
	"/u/WinneonSword's very own /u/LinkFixerBotSnr," + version +
	"For more info: http://github.com/WinneonSword/LinkFixerBotSnr"
)

# The cache of comments so the bot won't reply to the same comment. #
cache = set()

# The regex code to search for broken Reddit links. #
rFind = re.compile(' r/[A-Za-z0-9_]+')
uFind = re.compile(' u/[A-Za-z0-9_]+')

# This is a list of subreddits not allowed to be posted on, for various reasons. #
bannedSubs = set()
bannedSubs.add('loans')
bannedSubs.add('nba')
bannedSubs.add('aww')
bannedSubs.add('subredditdrama')
bannedSubs.add('againstmensrights')
bannedSubs.add('australia')
bannedSubs.add('shitpoliticssays')
bannedSubs.add('scotch')
bannedSubs.add('metacananda')
bannedSubs.add('news')
bannedSubs.add('nfl')
bannedSubs.add('breakingbad')
bannedSubs.add('theredpill')
bannedSubs.add('whatisthisthing')
bannedSubs.add('conspiratard')
bannedSubs.add('comics')
bannedSubs.add('mls')
bannedSubs.add('twoxchromosomes')
bannedSubs.add('politics')
bannedSubs.add('badhistory')
bannedSubs.add('49ers')
bannedSubs.add('yugioh')
bannedSubs.add('mac')

# This is a list of subreddits not allowed to be linked to, for more various reasons. #
prohibitedSubs = set()
prohibitedSubs.add('gonewild')
prohibitedSubs.add('gonewildplus')
prohibitedSubs.add('nsfw')
prohibitedSubs.add('spacedicks')
prohibitedSubs.add('frugal')

# This checks to see if the rate limit for PRAW and Reddit are in check when called. #
def handleRateLimit(func, *args):
	while True:
		try:
			func(*args)
			break
		except praw.errors.RateLimitExceeded as error:
			print("\tRate Limit exceeded! Sleeping for %d seconds to comply with the Reddit API..." % error.sleep_time)
			time.sleep(error.sleep_time)

# This prevents anything going into it to be doubled accidentally. #
def preventDoubles(func, *args):
	while True:
		func(*args)
		break

# This function checks a comment for any broken links when called. #
def checkComment(comment):
	text = comment.body
	broken = set(re.findall(rFind, text))
	broken.union( set(re.findall(uFind, text)) )
	condition = False
	if broken:
		condition = True
	return condition, broken

# This function checks and posts a comment that has been identified with a broken link. #
def postComment(comment, text):
	print("\tFound valid comment at comment id '" + comment.id + "'! Fixing broken link...")
	message = ''
	for char in text:
		message += "/" + char[1:] + " "
		if message.endswith(comment.subreddit.display_name.lower() + " "):
			print("\tThe broken link is the same as the subreddit! Skipping...")
			return
		if (any(message.endswith(x.lower() + " ") for x in prohibitedSubs)):
			print("\tThe broken link is a prohibited subreddit! Skipping...")
			return
	reply = (
		"" + message + "\n\n"
		"*****" + "\n\n"
		"^This ^is ^an [^automated ^bot](http://github.com/WinneonSword/LinkFixerBotSnr)^. ^For ^reporting ^problems, ^contact ^/u/WinneonSword."
	)
	handleRateLimit(comment.reply, reply)
	cache.add(comment.id)
	print("\tComment posted! Fixed link: " + message)

# This is the main function that searches for comments every 30 seconds. #
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
					if c.subreddit.display_name.lower() not in bannedSubs:
						if c.id not in cache:
							validComment = (
								"\tFound valid comment at comment id '" + c.id + "'! Fixing broken link..."
							)
							preventDoubles(print, validComment)
							try:
								postComment(c, text)
							except:
								print("\tCould not post comment! Check reddit.com for errors.")
						else:
							print("\tThe broken link has already been fixed! Skipping...")
					else:
						print("\tThe comment found is in the banned subreddit '" + c.subreddit.display_name + "'! Skipping...")
			print("\tFinished checking comments! Sleeping for 30 seconds...")
			time.sleep(30)
	except KeyboardInterrupt:
		print("[ wsLFB ] - Stopped LinkFixerBotSnr!")
