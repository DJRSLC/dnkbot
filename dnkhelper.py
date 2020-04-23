#!/usr/bin/python3

import os
import time
import boto3
import re
import sys
import pytz
import requests
import subprocess
import json
import urllib, hashlib
import socket
from botocore.exceptions import ClientError
from slackclient import SlackClient
from datetime import datetime
from datetime import timedelta
from pprint import pprint


#constants
if len(sys.argv) >1:
    name=sys.argv[1]
utc=pytz.UTC
ec2 = boto3.resource('ec2')
ec2client = boto3.client('ec2')
print ('Argument List:', str(sys.argv))
dnkdict = {}
viplist={'master-17','master-18','master-19','dlp331','rpp-13725','master-16','dlp87intx','djr-dnk-final','ddp-int','psirt-330','ioactive', 'master-13', 'redtail', 'perf-mastr', 'perf','m261','dlp-331','ddp-331'}
all_instances = boto3.resource('ec2').instances.all()
prefixlist={'api', 'cont', 'jenkins', 'kafka', 'mon', 'nifi', 'postgres', 'rabbit', 'redis', 'rose', 'ui', 'ups', 'vpn', 'conv', 'es', 'mds', 'qw'}

#Finds all ec2 instances
def find_all_instances():
    result = sanitize_instances(all_instances)
    return result

#Takes the given ec2 instances and leaves just the instance ID
def sanitize_instances(ec2inst):
    result=''
    for instance in ec2inst:
        idstr = str(instance)
        justid = idstr.split("\'")[1]
        result+=justid +'\n'
    return result

#Finds all instances where the Protected tag is DNK and returns them as a
#dictionary

def finddnk():
    customfilter = [{
        'Name':'tag:Protected',
        'Values':['DNK','vip']
        }]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        protected=""
        instancename=""

        #for tags in ec2instance.tags:
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
                #instancename = instance
            if tags["Key"] == 'Protected':
                protected = tags["Value"]
        if protected=='DNK' or protected=='vip':
            dnkdict[instancename] = protected
    return(dnkdict)

def finddnkstacks():
    customfilter = [{
        'Name':'tag:Protected',
        #'Values':['DNK','vip']
        'Values':['*']
        }]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        protected=""
        instancename=""
        stackname=""

        #for tags in ec2instance.tags:
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
                if "-" in instancename:
                    for prefix in prefixlist:
                        if instancename.startswith(prefix):
                            stackname = instancename.split('-',1)[1]
                #instancename = instance
            if tags["Key"] == 'Protected':
                protected = tags["Value"]
        #if protected=='DNK' or protected=='vip':
        if stackname != '':
            dnkdict[stackname] = protected
    return(dnkdict)

def findallstacks():
    customfilter = [{
        'Name':'tag:Name',
        'Values':['*']
        }]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        protected=""
        instancename=""
        stackname=""

        #for tags in ec2instance.tags:
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
                if "-" in instancename:
                    for prefix in prefixlist:
                        if instancename.startswith(prefix):
                            stackname = instancename.split('-',1)[1]
                #instancename = instance
            if tags["Key"] == 'Protected':
                protected = tags["Value"]
        #if protected=='DNK' or protected=='vip':
        if stackname != '':
            dnkdict[stackname] = protected
    return(dnkdict)

def findstack(searchname):
    dnkdict={}
    customfilter = [{
        'Name':'tag:Name',
        'Values':['*-'+searchname]}]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        protected=""
        instancename=""
        stackname=""

        #for tags in ec2instance.tags:
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
                if "-" in instancename:
                    for prefix in prefixlist:
                        if instancename.startswith(prefix):
                            stackname = instancename.split('-',1)[1]
                #instancename = instance
            if tags["Key"] == 'Protected':
                protected = tags["Value"]
        #if protected=='DNK' or protected=='vip':
        if stackname != '':
            dnkdict[stackname] = protected
    return(dnkdict)

#removes DNK tag from all instances that were marked more than 2 days ago. Leaves vip tag in place.
def removednktag():
    customfilter = [{
        'Name':'tag:Protected',
        'Values':['DNK']}]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        idstr = str(instance)
        justid = idstr.split("\'")[1]
        ec2instance = ec2.Instance(justid)
        protected=""

        for tags in instance.tags:
            if tags["Key"] == 'LastDnk':
                tag_time = datetime.strptime(tags["Value"],"%Y-%m-%d %H:%M:%S.%f")
                #if checkdnktime(tag_time) and checkrunningtime(instance):
                if checkdnktime(tag_time):
                    ec2.create_tags(Resources=[justid], Tags=[{'Key':'Protected','Value':'TagExpired'}])
                    pprint("tag has expired")
                else:
                    print("Instance " +
                    instance.launch_time.strftime("%Y-%m-%d %H:%M:%S") + " marked DNK too recently")

def checkdnktime(tag):
    #tag += timedelta(days=3)
    #pprint("tagtime = " + str(tag))
    #pprint("current time = " + str(datetime.now()))
    if tag < datetime.now():
        return True

def checkrunningtime(instance):
    start = instance.launch_time
    tdelta= datetime.strptime(str(utc.localize(datetime.now()))[:19], "%Y-%m-%d %H:%M:%S") - datetime.strptime(str(start)[:19], "%Y-%m-%d %H:%M:%S")
    tdeltahours = tdelta.seconds//3600
    if tdelta.days > 0 and tdeltahours > 5:
        return True
    else:
        return False

def checkrunningtest():
    customfilter = [{
        'Name':'tag:Protected',
        'Values':['DNK']
        }]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        #checkrunningtime(instance)
        for tags in instance.tags:
            if tags["Key"] == 'LastDnk':
                tag_time = datetime.strptime(tags["Value"],"%Y-%m-%d %H:%M:%S.%f")
                timeuntilexpire(tag_time)



def markvip():
    result=''
    for instance in all_instances:
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
                if "-" in instancename:
                    if instancename.split('-',1)[1] in viplist:
                        ec2.create_tags(Resources=[instance.id],
                                Tags=[{'Key':'Protected','Value':'vip'}])

#if an instance is not marked as vip or dnk, stop the instance. 
def stopuntagged():
    for instance in all_instances:
        try:
            for tags in instance.tags:
                if tags["Key"] == 'Name':
                    instancename=tags["Value"]
                    if "-" in instancename:
                        if re.search('es.+',instancename.split('-',1)[0]) :
                            print('node ' + instancename + 'is an es node, keep it alive!')
                        else:
                            idstr = str(instance)
                            justid = idstr.split("\'")[1]
                            ec2instance = ec2.Instance(justid)
                            if (checkrunningtime(instance)):
                                if (checkvip(instance) or checkdnk(instance)):
                                    print('check failed, ' + instancename + ' is marked as vip or dnk.')
                                else:
                                    print('here')
                                    #dry run!
                                    #try:
                                    #    response = ec2client.stop_instances(InstanceIds=[justid], DryRun=True)
                                    #except ClientError as e:
                                    #    if 'DryRunOperation' not in str(e):
                                    #        raise
                                    #    print(e)
                                    #    print(instancename + "is the node that would have been shut down")
                                    #for real here!
                                    try:
                                        response = ec2client.stop_instances(InstanceIds=[justid], DryRun=False)
                                        print(response)
                                    except ClientError as e:
                                        print(e)
                                        print(instancename + "has been shut down")
        except:
            print("no stack tags")

def startstack(stackname):
    customfilter = [{
        'Name':'tag:Name',
        'Values':["*-"+str(stackname)]}]
    pprint("debug1")
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        for tags in instance.tags:
            if tags["Key"] == 'Name':
                instancename = tags["Value"]
                if "-" in instancename:
                    if instancename.split('-',1)[1] == stackname:
                        idstr = str(instance)
                        justid = idstr.split("\'")[1]
                        ec2instance = ec2.Instance(justid)
                        #try:
                        #    response = ec2client.start_instances(InstanceIds=[justid], DryRun=True)
                        #except ClientError as e:
                        #    if 'DryRunOperation' not in str(e):
                        #        raise
                        try:
                            response = ec2client.start_instances(InstanceIds=[justid], DryRun=False)
                        except ClientError as e:
                            print(e)

#check to see if an ec2 instance is vip
def checkvip(instance):
    for tags in instance.tags:
        if tags["Key"] == 'Protected':
            if tags["Value"] == 'vip':
                return True
            else: return False

#check to see if an ec2 instance is DNK
def checkdnk(instance):
    for tags in instance.tags:
        if tags["Key"] == 'Protected':
            if tags["Value"] == 'DNK':
                return True

def findlastpin(channelid,readtoken):
    lastpinresponse = requests.get("https://slack.com/api/pins.list?token="+readtoken+"&channel="+channelid+"&pretty=1")
    lprjson_data = json.loads(lastpinresponse.text)
    lpr1 = str(lprjson_data).replace("\'","").split()
    #this will only fail if there wasn't a message previously posted by a bot.
    try:
        lastpinid = str(lpr1[lpr1.index("bot_id:")-3].replace(",","").replace("\'",""))
        botid = str(lpr1[lpr1.index("bot_id:")+1].replace(",","").replace("\'",""))
    except:
        return("0")
    #pprint(lastpinid)
    if botid =="BP4LQ3YM6":
        return(lastpinid)
    else:
        return("0")

def removeoldpin(channelid,readtoken,writetoken):
    #ts=gettimestamp()
    ts=findlastpin(channelid,readtoken)
    rmresponse = requests.post("https://slack.com/api/pins.remove?token="+readtoken+"&channel="+channelid+"&timestamp="+ts+"&pretty=1")
    delresponse = requests.post("https://slack.com/api/chat.delete?token="+writetoken+"&channel="+channelid+"&ts="+ts+"&pretty=1")
    #pprint(delresponse)

def buildallurl():
    stackmessage ="```"
    stacks = str(findallstacks()).replace('\'','').replace('{','').replace('}','').replace(' ','').split(',')
    for item in stacks:
        stackname = item.split(':')
        if stackname[1] == '':
            stackname[1] = 'untagged'
        stackip = getip(stackname[0])
        stacknamebase = "<https://jenkins-"+stackname[0]+".ro.internal:8443|"+stackname[0]+">"
        stackmessage += stacknamebase + " : " + str(getowner(stackname[0])).split('@')[0].replace('.',' ') + " : " + stackip + stackname[1]
        stackmessage = str(stackmessage) + "\n"
    stackmessage+="```"
    #pprint(stackmessage)
    return(stackmessage)

def buildurl(searchname):
    #stackmessage ="```"
    stackmessage =""
    stacks =""
    stacks = str(findstack(searchname)).replace('\'','').replace('{','').replace('}','').replace(' ','').split(',')
    for item in stacks:
        stackname = item.split(':')
        if stackname[1] == '':
            stackname[1] = 'untagged'
        stackip = getip(stackname[0])
        stacknamebase = "<https://jenkins-"+stackname[0]+".ro.internal:8443|"+stackname[0]+">"
        stackmessage += "```"+stacknamebase + " : " + str(getowner(stackname[0])).split('@')[0].replace('.',' ') + " : " + stackip + stackname[1]
        stackmessage = str(stackmessage) + "``` \n"
    stackmessage = stackmessage[:-1]
    #stackmessage+="```"
    #pprint(stackmessage)
    return(stackmessage)

def getip(stackname):
    try:
        sip = socket.gethostbyname("jenkins-"+stackname)
        sip += " : "
        return sip
    except:
        return ""

def getexpire(searchname):
    customfilter = [{
        'Name':'tag:Name',
        'Values':['*-'+searchname]}]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        for tags in instance.tags:
            if tags["Key"] == 'LastDnk':
                tag_time = datetime.strptime(tags["Value"],"%Y-%m-%d %H:%M:%S.%f")
                timeuntilexpire(tag_time)

def timeuntilexpire(tag):
    tdelta = datetime.strptime(str(tag)[:19], "%Y-%m-%d %H:%M:%S") - datetime.strptime(str(utc.localize(datetime.now()))[:19], "%Y-%m-%d %H:%M:%S") 
    tdeltahours = tdelta.seconds//3600
    tdeltaminutes = (tdelta.seconds//60)%60
    if tdeltaminutes/10 <1:
        tdeltaminutes = "0"+str(tdeltaminutes)
    difference = str(tdelta.days)+ " days, "+ str(tdeltahours) + ":" + str(tdeltaminutes)
    #pprint("difference = " + difference)
    return difference

def getowner(searchname):
    customfilter = [{
        'Name':'tag:Name',
        'Values':['*-'+searchname]}]
    all_matches = ec2.instances.filter(Filters=customfilter)
    for instance in all_matches:
        for tags in instance.tags:
            try:
                if tags["Key"] == 'Created_by':
                    return tags["Value"]
            except:
                return "No Owner"

#posts a message
def postdata(channelid,writetoken):
    stacks=buildallurl()
    response = requests.post("https://slack.com/api/chat.postMessage?token="+writetoken+"&channel="+channelid+"&text="+stacks+"&pretty=1")


#helper method, gets the timestamp/postid from the most recent post.
def gettimestamp(channelid,readtoken):
    tsresponse = requests.get("https://slack.com/api/conversations.history?token="+readtoken+"&channel="+channelid+"&limit=1&pretty=1")
    tsjson_data = json.loads(tsresponse.text)
    with open("data_file.json", "w") as write_file:
        json.dump(tsjson_data, write_file)
    ts1 = str(tsjson_data).replace("\'","").split()
    tsfinal = str(ts1[ts1.index("ts:")+1].replace(",","")).replace("\'","")
    #pprint(tsfinal)
    return(tsfinal)

#pin the most recent post made in the channel, should be post made from postdata().
def pindata(channelid,readtoken,ts):
    pinresponse = requests.post("https://slack.com/api/pins.add?token="+readtoken+"&channel="+channelid+"&timestamp="+ts+"&pretty=1")
    pinjson_data = json.loads(pinresponse.text)
    pinjson_string = str(pinjson_data)
    #pprint(pinjson_data)
    return(pinjson_data)
