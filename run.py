#######################################
# LinkFixerBotSnr, by /u/WinneonSword #
#######################################
import praw, time, sys, os, json, argparse

# This is the default config template. #
defaultConfig = {
	'reddit': {
		'username': '',
		'password': '',
		},
}

# This function writes the config template to config.json.
def writeConfig(conf):
	config = json.dumps(conf, indent = 4, sort_keys = True)
	with open('config.json', 'w') as f:
		f.write(config)

# This is what gets called first. It checks for a config.json, if not, creates one, and then starts the stript at LFB.py. #
if __name__ == "__main__":
	if not os.path.isfile('config.json'):
		writeConfig(defaultConfig)
		print("[ wsLFB ] - Created default configuration. Please edit the values before you start this again.")
	elif 'updateconf' in sys.argv:
		with open('config.json', 'r') as f:
			config = json.loads(f.read())
		defaultConfig.update(config)
		writeConfig(defaultConfig)
	else:
		import LFB
		LFB.main()
