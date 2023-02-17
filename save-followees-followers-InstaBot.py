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
    followees, followers = insta_bot.get_followees_followers_list() # getting followees and followers from instagram account
    print(len(followers), len(followees))
    
    return insta_bot.update_current_followees_followers(event, s3_client, followees, followers) # saving new file on S3 Bucket
