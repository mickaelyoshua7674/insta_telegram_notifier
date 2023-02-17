from InstaBot import InstaBot # my class
import boto3
import os

INSTA_USERNAME = os.environ.get("INSTA_USERNAME")
INSTA_PASSWORD = os.environ.get("INSTA_PASSWORD")
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

s3_client = boto3.client("s3")
s3_resource = boto3.resource("s3")

def lambda_handler(event, context):
    
    insta_bot = InstaBot(INSTA_USERNAME, INSTA_PASSWORD, TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID)

    _, current_followers, _ = insta_bot.get_saved_followees_followers(event, s3_resource) # getting the saved list of followers on S3 Bucket
    followees, followers = insta_bot.get_followees_followers_list() # getting the current followees and followers from instagram account
    
    unfollowers = insta_bot.get_unfollowers(followers, current_followers) # comparing and getting unfollowers
    
    if len(unfollowers) > 0:
        insta_bot.send_telegram_message("Unfollower or changed username or deleted account:\n" + unfollowers)
    else:
        insta_bot.send_telegram_message("No unfollowers.") # case unfollowers is empty
        
    insta_bot.update_current_followees_followers(event, s3_client, followees, followers) # updating followees and followers saved on S3 Bucket
    
    print(len(followers), len(followees))
    
    return {
        "statusCode": 200,
        "body": "Message sent.",
        "event": event
    }
