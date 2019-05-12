# blocklist2unbound

Author -- Duncan Bellamy
---
Convert host file blocklists to unbound blocklists.

Based on: 
https://github.com/Aracktus/DNS-Unbound-Blocklist-Downloader

Updated to python 3 and changed blocklist to Steve Black at: 
https://github.com/StevenBlack/hosts
---
If server supports it will check if blocklist needs updating first, so the list can be updated from a cron job.

````
usage: blocklist2unbound.py [-h] [-s] [-o OUTPUTDIR] [-r] [BL [BL ...]] positional arguments:
  BL blocklist(s) to generate optional arguments:
  -h, --help show this help message and exit
  -s, --show show availible blocklists
  -o OUTPUTDIR, --outputdir OUTPUTDIR directory to write files to (default /etc/unbound/unbound.conf.d)
  -r, --reload          reload unbound after generating files
````

TODO:
* Remove duplicates if more than 1 blocklist
* Allow passing of URL on commandline for blocklist