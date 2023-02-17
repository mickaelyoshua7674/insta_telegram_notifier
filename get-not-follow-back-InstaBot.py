import boto3
from InstaBot import InstaBot # my class
import os

INSTA_USERNAME = os.environ.get("INSTA_USERNAME")
INSTA_PASSWORD = os.environ.get("INSTA_PASSWORD")
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    insta_bot = InstaBot(INSTA_USERNAME, INSTA_PASSWORD, TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID)
    
    followees, followers = insta_bot.get_followees_followers_list()
    insta_bot.update_current_followees_followers(event, s3_client, followees, followers)

    not_re_follow = insta_bot.get_not_follow_back(followees, followers)
    print(not_re_follow)
    if len(not_re_follow) > 0:
        insta_bot.send_telegram_message("Not following back:\n" + not_re_follow)
    else:
        insta_bot.send_telegram_message("All follow back.", TELEGRAM_CHAT_ID)
    
    print(len(followers), len(followees))
    
    return {
        "statusCode": 200,
        "body": "Message sent.",
        "event": event
    }
