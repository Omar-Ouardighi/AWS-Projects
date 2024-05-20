import json
import boto3
import urllib3
import os
import logging
from utils import hash_message, get_message, set_message
from bedrockLLM import LLM
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

slackUrl = 'https://slack.com/api/chat.postMessage'
slackToken = os.environ.get('SLACK_TOKEN')
SlackChatHistoryUrl = 'https://slack.com/api/conversations.replies'
table = boto3.resource('dynamodb').Table('SlackBotTable')
http = urllib3.PoolManager()
model_id = 'mistral.mistral-7b-instruct-v0:2'
bedrock = LLM(model_id)

    
def handler(event, context):
    headers = {
        'Authorization': f'Bearer {slackToken}',
        'Content-Type': 'application/json',
    }
    slackBody = json.loads(event['body'])
    print(json.dumps(slackBody))
    slackText = slackBody.get('event').get('text')
    slackUser = slackBody.get('event').get('user')
    channel =  slackBody.get('event').get('channel')
    thread_ts = slackBody.get('event').get('thread_ts')
    ts = slackBody.get('event').get('ts')
    eventType = slackBody.get('event').get('type')
    subtype = slackBody.get('event').get('subtype')
    bot_id = slackBody.get('event').get('bot_id')
    is_last_message_from_bot = False
    bedrockMsg = []
    
    if eventType == 'message' and bot_id is None and subtype is None and thread_ts is not None:
        if get_message() != hash_message(slackText):
            set_message(slackText)
            # We got a new message in the thread lets pull from history
            historyResp = http.request('GET', f"{SlackChatHistoryUrl}?channel={channel}&ts={thread_ts}", headers=headers)
            messages = historyResp.json().get('messages')
            for message in messages:
                cleanMsg = re.sub(r'<@.*?>', '', message.get('text'))
                bot_profile = message.get('bot_profile')
                if bot_profile is None:
                    bedrockMsg.append(f'Human: {cleanMsg}')
                    is_last_message_from_bot = False
                else:
                    bedrockMsg.append(f'\n\nAssistant: {cleanMsg}')
                    is_last_message_from_bot = True
            bedrockMsg.append('\n\nAssistant:') # Message must always end with \n\nAssistant:
 
            if not is_last_message_from_bot: # Do not respond if the last message was a response
                msg = bedrock.invoke(bedrockMsg)
                data = {'channel': channel, 'text': f"<@{slackUser}> {msg}", 'thread_ts': thread_ts}
                response = http.request('POST', slackUrl, headers=headers, body=json.dumps(data))
        
    if (eventType == 'app_mention' and bot_id is None and thread_ts is None):
        # send an init message and thread the convo
        initMsg = re.sub(r'<@.*?>', '', slackText)
        bedrockMsg.append(f'Human: {initMsg} \n\nAssistant:')
        msg = bedrock.invoke(bedrockMsg)
        data = {'channel': channel, 'text': f"<@{slackUser}> {msg}", 'thread_ts': ts}
        response = http.request('POST', slackUrl, headers=headers, body=json.dumps(data))
    
    return {
        'statusCode': 200,
        'body': json.dumps({'msg': "message received"})
    }








