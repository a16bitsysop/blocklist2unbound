#!/usr/bin/env python3
import argparse, sys
import urllib.request
import os.path
import subprocess

modstring = '#MTIME:'
outputpostfix = '.block.conf'
outputdir = '/etc/unbound/unbound.conf.d'
dot = '. '

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

def check_file(file, url, force, ishostnamelist):
	print('Checking:', url)
	#check if local file exists if force update not used
	if os.path.isfile(file) and not force:
		# read timestamp from local file was [1]
		oldfile = open(file, 'r')
		lastmod = oldfile.readline().split(modstring,1)[-1].rstrip()
		oldfile.close()
	else:
		# local file doesn't exist or force update used so make date null
		lastmod = ''

	try:
		#try and open blocklist url
		data = urllib.request.urlopen(url)
	except urllib.error.HTTPError as e:
		if hasattr(e, 'reason'):
			sys.exit('We failed to reach a server: ' + e.reason)
		elif hasattr(e, 'code'):
			sys.exit('The server couldn\'t fulfill the request: ' + e.code)
		else:
			sys.exit('unknown error')
	except urllib.error.URLError as e:
		if hasattr(e, 'reason'):
			sys.exit('URL Error: ' + e.reason)
		else:
			sys.exit('unknown error')

	modified = data.getheader('last-modified')
	if modified and modified == lastmod:
		print('\tLocal file up to date')
		return False
	else:
		try:
			output = open(file, 'w')
		except PermissionError:
			sys.exit('File Error: Permission denied writing to: ' + file)
		if modified:
			print('\tNeeds update')
			output.write(modstring + modified + '\n')
		else:
			print('\tNo modified header from server')
		#Start creating unbound conf file
		output.write('server:\n')
		print('\tDownloading...')
		download_blocklist(output, data, ishostnamelist)
	print('\tDone')
	return True



def download_blocklist(Poutput, Pdata, Pishostnamelist):

	for line in Pdata:
		string_line = line.decode('utf-8').strip()
		#Strip comment lines (for hostname list files)
		if string_line.startswith('#'):
			continue
		#Only interested in lines starting with '0.0.0.0'
		if string_line and (string_line.startswith('0.0.0.0') or Pishostnamelist):
			#Remove '0.0.0.0' and anything after domain name was [0]
			string_line = string_line.strip('0.0.0.0').lstrip().split(' ',1)[0]
			#Write out unbound format to unbound conf file with trailing dot if needed
			if len(string_line) > 4: Poutput.write('local-data: \"' + string_line + dot + 'IN A 127.0.0.1\"\n')
	return

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show', action='store_true', help='show availible blocklists')
parser.add_argument('-o', '--outputdir', type=str, help='directory to write files to (default /etc/unbound/unbound.conf.d')
parser.add_argument('-n', '--nodot', action='store_true', help='do not add a trailing \'.\' to domain name')
parser.add_argument('-f', '--force', action='store_true', help='do not check if needs update')
parser.add_argument('-r', '--reload', action='store_true', help='reload unbound after generating files')
parser.add_argument('-u', '--url', type=str, help='url of blocklist to download')
parser.add_argument('-l', '--list', action='store_true', help='URL is a list of hostnames not a host file')
parser.add_argument('blocklist', metavar='BL', type=str, nargs='*', help='blocklist(s) to generate')
args = parser.parse_args()

if len(sys.argv) == 1:
	parser.print_help()
	sys.exit('No arguments specified')

if args.show:
	print('Availible blocklists are:')
	for record in blocklists:
		print(record,end='')
		bllen = len(record)
		if bllen > 4 and bllen < 8 : print(end='\t')
		if bllen > 4 and bllen < 15 : print(end='\t')
		print('\t-- Description: ', blocklists[record]['desc'])
if args.outputdir:
	if os.path.isdir(args.outputdir):
		args.outputdir = args.outputdir.rstrip('\/')
		outputdir = args.outputdir
	else:
		sys.exit('Output directory: ' + args.outputdir + ' does not exist')
if args.nodot:
	dot = ' '

needsreload = False
if args.blocklist:
	for record in args.blocklist:
		if record in blocklists:
			blfile = outputdir + '/' + record + outputpostfix
			print('Generating Blocklist:\t', record)
			print('Desc:\t', blocklists[record]['desc'])
			print('File:\t', blfile)
			print('URL:\t', blocklists[record]['url'])
			if check_file(blfile, blocklists[record]['url'], args.force, False):
				needsreload = True

		else:
			sys.exit('Error! No blocklist with id: ' + record)

if args.url:
	print('Checking url: ', args.url)
	urlparsed = urllib.parse.urlsplit(args.url)
	hostname = urlparsed.hostname.replace('.', '_')
	path = urlparsed.path.replace('/', '')
	print('hostname: ', hostname)
	print('path: ', path)
	blfile = outputdir + '/' + hostname + '.' + path + outputpostfix
	print('saving as: ', blfile)
	if check_file(blfile, args.url, args.force, args.list):
		needsreload = True

if args.blocklist and args.reload and needsreload:
	print('Reloading unbound')
	subprocess.run(['unbound-control', 'reload'])

