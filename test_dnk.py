from dnkhelper import *

"""
Send a message to slack at a certain cron'd time based on a config.json
"""

readtoken="xoxp-13044867472-777639246324-775216687635-c7ded79a3e75125f5ac7b5ac7c9f34ec"
writetoken="xoxb-13044867472-788553855815-i5wQDZGY1BMrypGUM7bNAJUU"

#channelid of dnkbot-test
channelid="CP6GN7TM5"

#channelid of jenkins-build
#channelid="C3801UAFP"

#findlastpin(channelid,readtoken)
#removeoldpin(channelid,readtoken,writetoken)
#buildallurl()
#postdata(channelid,writetoken)
#ts=gettimestamp(channelid,readtoken)
#pinned=pindata(channelid,readtoken,ts)

#stopuntagged()
#startstack("feature-rpp-13551")
checkrunningtest()
