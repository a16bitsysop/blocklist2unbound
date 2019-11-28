#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import argv, exit
from urllib import parse, error, request
from os import path, remove, scandir
from subprocess import run
from re import compile

# domain validating regex from O'Reily regular expressions cookbook
DomainRegex = compile(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
IPregex = compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
ModString = '#MTIME:'
URLstring = '#URL '
MaxConfLines = 4
OutputPostfix = '.block.conf'
OutputDir = '/etc/unbound/unbound.conf.d/'
dot = '.'
blockIP = '0.0.0.0'
rDot = '-'
rSlash = '_'

# path used to start script (link path if link)
CallPath = path.abspath(__file__)
(CallPath, _) = path.split(CallPath)
if CallPath.startswith('/etc/cron.'):
	cron = True
	print('Cron mode enabled')
else:
	cron = False

blocklists = 	{
		'sbuni':{
		'desc': 'StevenBlack Unified',
		'url': 'http://sbc.io/hosts/hosts',
		},
		'sbfake':{
		'desc': 'StevenBlack Fakenews',
		'url': 'http://sbc.io/hosts/alternates/fakenews/hosts',
		},
		'sbgamble':{
		'desc': 'StevenBlack Gambling',
		'url': 'http://sbc.io/hosts/alternates/gambling/hosts',
		},
		'sbporn':{
		'desc': 'StevenBlack Porn',
		'url': 'http://sbc.io/hosts/alternates/porn/hosts',
		},
		'sbsocial':{
		'desc': 'StevenBlack Social',
		'url': 'http://sbc.io/hosts/alternates/social/hosts',
		},
		'sbfakegamble':{
		'desc': 'StevenBlack Fakenews+Gamble',
		'url': 'http://sbc.io/hosts/alternates/fakenews-gambling/hosts',
		},
		'sbfakeporn':{
		'desc': 'StevenBlack Fakenews+Porn',
		'url': 'http://sbc.io/hosts/alternates/fakenews-porn/hosts',
		},
		'sbfakesocial':{
		'desc': 'StevenBlack Fakenews+Social',
		'url': 'http://sbc.io/hosts/alternates/fakenews-social/hosts',
		},
		'sbgambleporn':{
		'desc': 'StevenBlack Gambling+Porn',
		'url': 'http://sbc.io/hosts/alternates/gambling-porn/hosts',
		},
		'sbgamblesocial':{
		'desc': 'StevenBlack Gamble+Social',
		'url': 'http://sbc.io/hosts/alternates/gambling-social/hosts',
		},
		'sbpornsocial':{
		'desc': 'StevenBlack Porn+Social',
		'url': 'http://sbc.io/hosts/alternates/porn-social/hosts',
		},
		'sbfakegambleporn':{
		'desc': 'StevenBlack Fakenews+Gamble+Porn',
		'url': 'http://sbc.io/hosts/alternates/fakenews-gambling-porn/hosts',
		},
		'sbfakegamblesocial':{
		'desc': 'StevenBlack Fakenews+Gamble+Social',
		'url': 'http://sbc.io/hosts/alternates/fakenews-gambling-social/hosts',
		},
		'sbfakepornsocial':{
		'desc': 'StevenBlack Fakenews+Porn+Social',
		'url': 'http://sbc.io/hosts/alternates/fakenews-porn-social/hosts',
		},
		'sbgamblepornsocial':{
		'desc': 'StevenBlack Gamble+Porn+Social',
		'url': 'http://sbc.io/hosts/alternates/gambling-porn-social/hosts',
		},
		'sbfakegamblepornsocial':{
		'desc': 'StevenBlack Fakenews+Gamble+Porn+Social',
		'url': 'http://sbc.io/hosts/alternates/fakenews-gambling-porn-social/hosts',
		}, }

def check_file(file, url, force, StoreUrl=False):
# use thses global variables do not create local ones
	global blockIP
	global dot

	GotList = False
# check if local file exists
	if path.isfile(file):
		OldFile = open(file, 'r')

# get timestamp and url from file
		loop = 0
		need = 1
		if cron and StoreUrl:
			need += 1
		for line in OldFile:
			line = line.strip()
			if line.startswith(ModString):
# read timestamp from local file
				LastMod = line.split(ModString,1)[-1].rstrip()
				need -= 1
			if cron and StoreUrl and line.startswith(URLstring):
				url = line.split(URLstring,1)[-1].rstrip()
# decrease by 2 incase no MTIME
				need -= 2
			loop += 1
			if loop > MaxConfLines or need >= 0:
				break
		if cron:
			for line in OldFile:
				line = line.strip()
# extract ip and and hostname from data line
				if line.startswith('local-data:'):
					line = line.replace('\"', '')
					result = line.partition('IN A')
# check if hostname has a trailing dot
					if result[0].rstrip()[-1] == '.':
						dot = '.'
					else:
						dot = ''
# set blockip from file
					blockIP = result[2].strip()
					break


		OldFile.close()
# force update used so make date null
		if force:
			LastMod = ''
	else:
		LastMod = ''
		print('\tPrevious local block file not found')
	print('Checking:', url)

	try:
# try and open blocklist url
		data = request.urlopen(url)
	except error.HTTPError as e:
		if hasattr(e, 'reason'):
			exit('Failed to reach a server: ' + str(e.reason))
		elif hasattr(e, 'code'):
			exit('The server couldn\'t fulfill the request: ' + e.code)
		else:
			exit('unknown error')
	except error.URLError as e:
		if hasattr(e, 'reason'):
			exit('URL Error: ' + str(e.reason))
		else:
			exit('unknown error')

	modified = data.getheader('last-modified')
	if modified and modified == LastMod:
		print('\tLocal file up to date')
	else:
		try:
			output = open(file, 'w')
		except PermissionError:
			exit('File Error: Permission denied writing to: ' + file)
		if modified:
			print('\tNeeds update')
# add modified timestamp to unbound conf file
			output.write(ModString + modified + '\n')
		else:
			print('\tNo modified header from server')
# add url to unbound conf file
		if StoreUrl:
			output.write(URLstring + url + '\n')
		output.write('server:\n')
		print('\tDownloading...')
		if download_blocklist(output, data):
			GotList = True
		else:
# remove file if no domains to block
			os.remove(file)
			print('\tNo domains found to add to blockist')
	print('\tDone')
	return GotList



def download_blocklist(Poutput, Pdata):
	GotItems = False

	for line in Pdata:
# turn line into string, strip 0.0.0.0 if present then return next word only
		StrLine = line.decode('utf-8').strip('0.0.0.0').lstrip().split(' ',1)[0]
# check there is a word and word has at least one '.' and is not a comment
		if StrLine and '.' in StrLine and not StrLine.startswith('#'):
			if StrLine:
# use domain validation regex only on stripped out word to avoid false positives
				parsed = DomainRegex.match(StrLine)
				if parsed:
					GotItems = True
# Write out unbound format to conf file with trailing dot if needed
					if len(parsed.group()) > 4:
						Poutput.write('local-zone: \"' + parsed.group() + dot + '\" redirect\n')
						Poutput.write('local-data: \"' + parsed.group() + dot + ' IN A ' + blockIP + '\"\n')
	return GotItems

parser = ArgumentParser()
parser.add_argument('-s', '--show', action='store_true',\
help='show availible blocklists')
parser.add_argument('-o', '--outputdir', type=str,\
help='default /etc/unbound/unbound.conf.d/')
parser.add_argument('-n', '--nodot', action='store_true',\
help='do not add a trailing \'.\' to domain name')
parser.add_argument('-i', '--ip', type=str,\
help='use IP in created blocklist instead of \"0.0.0.0\"')
parser.add_argument('-f', '--force', action='store_true',\
help='do not check if needs update')
parser.add_argument('-r', '--reload', action='store_true',\
help='reload unbound after generating files')
parser.add_argument('-u', '--url', type=str,\
help='url of blocklist to download')
parser.add_argument('blocklist', metavar='BL', type=str, nargs='*',\
help='blocklist(s) to generate')
args = parser.parse_args()

if args.show:
	print('Availible blocklists are:')
	for record in blocklists:
		print(record,end='')
		bllen = len(record)
		if bllen > 4 and bllen < 8 : print(end='\t')
		if bllen > 4 and bllen < 15 : print(end='\t')
		print('\t-- Description: ', blocklists[record]['desc'])

if args.outputdir:
	if path.isdir(args.outputdir):
		OutputDir = args.outputdir
# make sure path ends in /
		if OutputDir[-1] != '/':
			OutputDir = OutputDir + '/'
	else:
		exit('Output directory: ' + args.outputdir + ' does not exist')

NeedsReload = False
if cron:
	args.reload = True
	args.blockist = ''
	found = False
# scan unbound folder to find blocklists
	contents = scandir(OutputDir)
	for entry in contents:
		if entry.is_file() and entry.name.endswith('.block.conf'):
			print('found: ', entry.name)
			blname = entry.name.rsplit('.block.conf',1)[0]
			if blname in blocklists:
				print('entry found: ', blname)
				found = True
				args.blocklist.append(blname)
			else:
				found = True
				if check_file(OutputDir + entry.name, 'none', False, True):
					NeedsReload = True
					break
	if not found:
		exit('No blocklists found')
else:
	if len(argv) == 1:
		parser.print_help()
		exit('No arguments specified')

if args.nodot:
	dot = ''

if args.ip:
	parsed = IPregex.match(args.ip)
	if parsed:
# remove leading 0's in ip address
		blockIP = '.'.join(str(int(i)) for i in parsed.group().split('.'))
		print('Using blockip address: ', blockIP)
	else:
		exit('Invalid ip address: ' + args.ip)

if args.blocklist:
	for record in args.blocklist:
		if record in blocklists:
			blfile = OutputDir + record + OutputPostfix
			print('Generating Blocklist:\t', record)
			print('Desc:\t', blocklists[record]['desc'])
			print('File:\t', blfile)
			print('URL:\t', blocklists[record]['url'])
			if check_file(blfile, blocklists[record]['url'], args.force):
				NeedsReload = True

		else:
			exit('Error! No blocklist with id: ' + record)

if args.url:
	print('Checking url: ', args.url)
	urlparsed = parse.urlsplit(args.url)
	hostname = urlparsed.hostname.replace('.', rDot)
	localpath = urlparsed.path.replace('/', rSlash)
	print('\tProcessed hostname: ', hostname)
	print('\tProcessed path: ', localpath)
	blfile = OutputDir + hostname + '.' + localpath + OutputPostfix
	print('\tSaving as: ', blfile)
	if check_file(blfile, args.url, args.force, True):
		NeedsReload = True

if args.blocklist and args.reload and NeedsReload:
	print('Reloading unbound')
	subprocess.run(['/usr/bin/env', 'unbound-control', 'reload'])
