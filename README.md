This is the dnkbot. To access the running code:

To be able to run code:
```
cd ~/projects/dnkbot/
source bin/activate
```
The main file running/listening to slack is `dnkbot.py` and you can get it to run in the backround using:
```
nohup python dnkbot.py &
```
test_dnk.py is used for testing out various functions.
dnkbothelper.py is the bulk of the code, other files just make function calls to it.
All of the shell scripts are what are being run by chron jobs.
The cronjobs running are
```
#script to remove dnk from all non-vip ec2 instances at noon, monday-friday.
0 19 * * 1-5 /home/dnkbotuser/projects/dnkbot/removednkcron.sh
#script to turn off all ec2 instances not marked dnk or vip at 6pm, m-f.
0 1 * * 2-6 /home/dnkbotuser/projects/dnkbot/stopuntaggedinstances.sh
#script to keep correct stuff pinned in slack. Runs at noon and 6pm MST hours on the first minute.
1 19 * * 1-5 /home/dnkbotuser/projects/dnkbot/pinslack.sh
1 1 * * 2-6 /home/dnkbotuser/projects/dnkbot/pinslack.sh
0 * * * * /home/dnkbotuser/projects/dnkbot/markvip.sh
```
Various parts of the code are in use, but some are just artifacts of testing. Priorities got shifted before code was cleaned up, so much was left.
