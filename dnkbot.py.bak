import os
import time
import boto3
import re
import websocket
from dnkhelper import *
from slackclient import SlackClient
from datetime import datetime
from threading import Timer


SLACK_BOT_TOKEN='xoxb-13044867472-788553855815-i5wQDZGY1BMrypGUM7bNAJUU'

# instantiate Slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)
# dnkbot's user ID in Slack: value is assigned after the bot starts up
dnkbot_id = None
readtoken="xoxp-13044867472-777639246324-775216687635-c7ded79a3e75125f5ac7b5ac7c9f34ec"
writetoken="xoxb-13044867472-788553855815-i5wQDZGY1BMrypGUM7bNAJUU"
commandts=""
webhookurl="https://hooks.slack.com/services/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"


# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
READ_WEBSOCKET_DELAY = 5
EXAMPLE_COMMAND = "do"
ec2 = boto3.resource('ec2')
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == dnkbot_id:
                return message, event["channel"], event["event_ts"]
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def search_for_instances(target):
    customfilter = [{
        'Name':'tag:Name',
        'Values':['*'+target]}]
    all_matches = ec2.instances.filter(Filters=customfilter)
    #sanitize the string and prep the ID for return
    result=''
    for instance in all_matches:
        idstr = str(instance)
        justid = idstr.split("\'")[1]
        result+=justid +'\n'
    return result

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    #default_response = "Invalid command. Currently only *check*, *dnk* and *removednk* are valid ways to start commands. See confluence for details."
    default_response = ""
    # Find and executes the given command, filling in response
    response = None
    if command.startswith('destroy2'):
        channel= "CP6GN7TM5"
        target = command.split('destroy2',1)[1].strip()
        url = "https://jenkins-qa.ro.internal/job/destroy-stack-resources/build"
        auth = ('dnkbot', 'DnkPassword1')
        payload = {"parameter": [{"name":"ro_unique_name_san", "value":"'+target+'"}]}
        r = requests.post(url, data=payload, auth=("TOKEN"),verify=False)
        print(r.status_code)
        print(r.text)
        #curl -X POST https://jenkins-qa.ro.internal/job/destroy-stack-resources/build \
        #        --user dnkbot:dnkbotpass \
        #        --form json ='{"parameter": [{"name":"ro_unique_name_san", "value":"'+target+'"}]}'
        response=target

    if command.startswith('destroy'):
        channel= channel
        target = command.split('destroy',1)[1].strip()
        message= target
        myblocks =[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Are you sure you want @dnkbot to destroy "+target+"?"
                    }
                },
                {
                    "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Do not destroy "+target+""
                                },
                                "value": "cancel",
                                "action_id": "cancelbutton"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Destroy "+target+""
                                },
                                "style": "danger",
                                "value": "kill",
                                "action_id": "killbutton",
                                "url": "https://jenkins-qa.ro.internal/job/destroy-stack-resources/parambuild/?ro_unique_name_san="+target+"",
                            }
                        ]
                }
              ]
        json.dumps(slack_client.api_call("chat.postMessage",
                              channel=channel,
                              blocks=myblocks))
        response=""
        #response=commandts
        #response=requests.post("https://slack.com/api/chat.update?token="+writetoken+"&channel="+channel+"&ts="+commandts+"&text="+"Test message"+"&pretty=1")

    if command.startswith('getts'):
        response = commandts

    #dnk sets all matching instances to dnk
    if command.startswith('dnk'):
        instanceexists = False
        current_time = datetime.now()
        try:
            target = command.split()[1].strip()
        except:
            response = "ERROR: dnkbot is looking for format \"[dnk,removednk] [stackname]\""
        try:
            tagtime = int(command.split()[2])
        except:
            tagtime = 3
        try:
            tagunit = command.split()[3]
            if tagunit == "day":
                tagunit="days"
            elif tagunit !="hours" and tagunit!="hour":
                tagunit="days"
        except:
            tagunit = "days"

        if target in viplist:
            response = target + " is in the vip list, unable to change protection value."
        else:
            found_instances = search_for_instances(target).splitlines()
            if tagunit=="hours":
                current_time+= timedelta(hours=(tagtime))
            elif tagunit=="days":
                current_time+= timedelta(days=(tagtime))
            current_time = str(current_time)
            for found_instance in found_instances:
                instanceexists = True
                current_time = str(current_time)
                ec2.create_tags(Resources=[found_instance],
                        Tags=[{'Key':'Protected','Value':'DNK'},
                            {'Key':'LastDnk','Value':current_time}])
            if instanceexists:
                response = target + " is marked as DNK for "+str(tagtime)+" " +tagunit+"."
            else:
                response = "ERROR: Stack " + target + " not found. Please check for typos."

    #removednk removes the dnk flag from the stack named by user
    if command.startswith('removednk'):
        instanceexists = False
        target = command.split('removednk',1)[1].strip()
        if target in viplist:
            response = target + " is in the vip list, unable to change protection value."
        else:
            found_instances = search_for_instances(target).splitlines()
            for found_instance in found_instances:
                instanceexists = True
                ec2.create_tags(Resources=[found_instance],
                        Tags=[{'Key':'Protected','Value':'OkayToDestroy'},
                            {'Key':'LastDnk','Value':''}])
            if instanceexists:
                response = target + " is no longer marked as dnk"
            else:
                response = "ERROR: Stack " + target + " not found. Please check for typos."
    #search command. Finds instances with names containing supplied substring. Mostly debugging.
    #if command.startswith('search'):
    #    target = command.split('search ',1)[1]
    #    response=search_for_instances(target)

    if command.startswith('help'):
        response = "valid commands are currently: start, check, destroy, dnk, and removednk. Please see <https://confluence.websense.com/x/sQbWBg|confluence> for details."

    #replies with the state of the stack asked about.
    if command.startswith('check'):
        build=''
        try:
            target = command.split('check',1)[1].strip()
            build = buildurl(target)
        except IndexError as error:
            response="Please specify a stack."
        if build =='':
            response="Please check for typos and verify your stack is fully up and running."
        else:
            response=build
#        response=postdata("CP6GN7TM5","xoxb-13044867472-788553855815-i5wQDZGY1BMrypGUM7bNAJUU")
    # Sends the response back to the channel

    if command.startswith('start'):
        stack=''
        try:
            target = command.split('start',1)[1].strip()
            stack = startstack(target)
        except IndexError as error:
            response="Please specify a stack."
        if stack =='':
            response ="something went wrong"
        else:
            response = target + " has been turned back on."

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("DNK Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        dnkbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            try:
                command, channel, commandts = parse_bot_commands(slack_client.rtm_read())
                if command:
                    handle_command(command.lower(), channel)
                time.sleep(RTM_READ_DELAY)
            #except Exception as e:
            #    print(e)
            except:
                print('Caught slack connect error, trying to reconnect...')
                time.sleep(READ_WEBSOCKET_DELAY)
                slack_client.rtm_connect()
