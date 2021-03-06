# blocklist2unbound

### Author -- Duncan Bellamy
---
### Convert host file blocklists and domain name lists to unbound blocklists.

Based on: 
https://github.com/Aracktus/DNS-Unbound-Blocklist-Downloader

#### Updated to python 3 and changed blocklists to Steve Black at: 
#### https://github.com/StevenBlack/hosts
---
Creates blocklists with always_nxdomain unless an ip address is specified, when created with an ip address it is read from the saved blocklist when updating.
If the remote server supports it will check if the blocklist needs updating first, so it can be updated from a cron job as well.

To run from cron, create a symbolic link to blocklist2unbound.py from the required /etc/cron.daily|weekly|monthly 
folder.  This enables cronmode and /etc/unbound/unbound.conf.d is scanned for .block.conf files which are then
updated, if a blocklist is generated from a url it is stored in the file and used to update it.  Unbound is reloaded if any blocklists have been updated in cronmode.

Using a .py extenstion in the cron.daily|weekly|monthly folder can cause run-parts to not execute the script so the link should have no extension.

eg:
````
# sudo ln -s /usr/local/bin/blocklist2unbound.py /etc/cron.weekly/blocklist2unbound
````

````
usage: blocklist2unbound.py [-h] [-s] [-o OUTPUTDIR] [-n] [-i IP] [-f] [-r] [-u URL]
                            [BL [BL ...]]

positional arguments:
  BL                    blocklist(s) to generate

optional arguments:
  -h, --help            show this help message and exit
  -s, --show            show availible blocklists
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        directory to write files to (default
                        /etc/unbound/unbound.conf.d)
  -n, --nodot           do not add a trailing '.' to domain name
  -i IP, --ip IP        use IP in created blocklist instead of "0.0.0.0"
  -f, --force           do not check if needs update
  -r, --reload          reload unbound after generating files
  -u URL, --url URL     url of blocklist to download
````

TODO:
* Remove duplicates if more than 1 blocklist

