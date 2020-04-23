#!/usr/bin/python3

from dnkhelper import *

if sys.argv[1]=='help':
    print("""valid arguments: removednk, poweroff  or kill. To change list of VIP stacks, edit vipfile.py
        removednk: removes dnk from stacks marked DNK. Will allow them to be deleted in next pass.
        poweroff: powers off all stacks not marked VIP.
        kill: kills all stacks not marked VIP or DNK.""")
    sys.exit(0)

#finds all instances on AWS and prints them to console, debugging.
if sys.argv[1]=='search':
    instances=find_all_instances()
    print(instances)

if sys.argv[1]=='finddnk':
    dnkdict=finddnk()
    pprint(dnkdict)

if sys.argv[1]=='removednktag':
    removednktag()

if sys.argv[1]=='markvip':
    markvip()

if sys.argv[1]=='stopuntagged':
    stopuntagged()

#if sys.argv[1]=='destroy':
    #todo

if sys.argv[1]=='finddnkstacks':
    dnkdict=finddnkstacks()
    pprint(dnkdict)

sys.exit(0)
