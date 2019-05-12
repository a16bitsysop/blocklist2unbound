#!/usr/bin/env python3
import argparse, sys
import urllib.request
import os.path

modstring = "#MTIME:"
outputpostfix = ".block.conf"
outputdir = "/etc/unbound/unbound.conf.d"

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

def check_file(file,url):
	print('Checking:',url)
	exists = os.path.isfile(file)
	if exists:
		# read timestamp
		oldfile = open(file,'r')
		lastmod = oldfile.readline().split(modstring,1)[1].rstrip()
		oldfile.close()
	else:
		# nothing to read!
		lastmod = ''

	data = urllib.request.urlopen(url)
	modified = data.getheader('last-modified')
	if modified and modified == lastmod:
		print('\tLocal file up to date')
	else:
		output = open(file,'w')
		if modified:
			print('\tNeeds update')
			output.write(modstring + modified + '\n')
		else:
			print('\tNo modified header from server')
		output.write('server:\n')
		print('\tDownloading...')
		download_blocklist(output,data)
	print('\tDone')
	return



def download_blocklist(Poutput,Pdata):

	for line in Pdata:
		string_line = line.decode('utf-8').strip()
		if string_line and string_line.startswith('0.0.0.0'):
			string_line = string_line.strip('0.0.0.0').lstrip().split(' ',1)[0]
			if len(string_line) > 4: Poutput.write('local-data: \"' + string_line + '. IN A 127.0.0.1\"\n')
	return

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show', action='store_true', help='show availible blocklists')
parser.add_argument('-o', '--outputdir', type=str, help='directory to write files to (default /etc/unbound/unbound.conf.d')
parser.add_argument('blocklist', metavar='BL', type=str, nargs='*', help='blocklist(s) to generate')
args = parser.parse_args()

if len(sys.argv) == 1:
	print('No arguments specified')
	parser.print_help()
	sys.exit()

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
		outputdir = args.outputdir
	else:
		sys.exit('Output directory: ' + args.outputdir + ' does not exist')
if args.blocklist:
	for record in args.blocklist:
		if record in blocklists:
			print('Generating Blocklist:\t', record)
			print('Desc:\t', blocklists[record]['desc'])
			print('File:\t', outputdir + '/' + record + outputpostfix)
			print('URL:\t', blocklists[record]['url'])
			check_file( outputdir + '/' + record + outputpostfix, blocklists[record]['url'])

		else:
			sys.exit('Error! No blocklist with id: ' + record)

