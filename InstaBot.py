import instaloader
import requests
import json
import boto3

class InstaBot:
    def __init__(self, USERNAME: str, PASSWORD: str, TELEGRAM_API_TOKEN: str, TELEGRAM_CHAT_ID: str) -> None:
        self.USERNAME = USERNAME
        self.l = instaloader.Instaloader(max_connection_attempts=1) # creating an Instaloader object
        self.l.login(USERNAME, PASSWORD)
        self.profile = instaloader.Profile.from_username(self.l.context, self.USERNAME) # getting Profile object
        self.TELEGRAM_API_TOKEN = TELEGRAM_API_TOKEN # to create your telegram bot https://sendpulse.com/knowledge-base/chatbot/telegram/create-telegram-chatbot
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID # send a message to your bot and get chat id https://api.telegram.org/bot<YourBOTToken>/getUpdates
        self.TELEGRAM_API_URL_MESSAGE = f"https://api.telegram.org/bot{self.TELEGRAM_API_TOKEN}/sendMessage"
        self.S3_BUCKET = "insta-followees-followers"
        
    def get_followees_followers_list(self) -> list[str]:
        """Return a list of all followees and followers usernames in alphabetical order"""
        followees = self.profile.get_followees() # return and object with all followees
        followers = self.profile.get_followers() # return and object with all followers
        return sorted([f.username for f in followees]), sorted([f.username for f in followers]) # .username return the username of that follower object
                                                       # sorted for alphabetical order
    
    def send_telegram_message(self, message: str) -> None:
        """Send the input text to the telegram chat id"""
        requests.post(self.TELEGRAM_API_URL_MESSAGE, json={'chat_id': self.TELEGRAM_CHAT_ID, 'text': message})
    
    def update_current_followees_followers(self, event, s3_client: boto3.client, followees: list[str], followers: list[str]) -> dict:
        """
        Receive the followees and followers, put the object 
        in Amazon S3 bucket and return a dict with response
        and event.
        """
        data = { # making dict format to store
            "username": self.USERNAME,
            "followees": followees,
            "followers": followers
        }

        response = s3_client.put_object(
            Bucket = self.S3_BUCKET, # name of the bucket target
            Key = f"{self.USERNAME}.json", # file name to be storage
            Body = json.dumps(data) # json.dumps to make a json format
        )

        return {
            "statusCode": 200,
            "body": "File uploaded.",
            "event": event,
            "response": response
        }

    def get_saved_followees_followers(self, event, s3_resource: boto3.resource) -> list:
        """
        Receive the boto3.resource object and get the data from
        the S3 Object.
        """
        data = s3_resource.Object(
            bucket_name = self.S3_BUCKET,
            key = self.USERNAME + ".json"
        ).get()["Body"].read() # return a byte string
        
        dict_data = json.loads(data.decode('utf-8')) # decoding

        return dict_data["followees"], dict_data["followers"], event

    def get_unfollowers(self, followers: list[str], current_followers: list[str]) -> str:
        """
        Return a string with the link of all followers.
        Case has no new unfollower return an empty string.
        Case has a change in the followers will update the 'current_followers.json' and 'current_followees.json' file.
        """
        unfollowers_list = []
        unfollowers = ""
        if current_followers != followers: # if the saved followers are not equal to the new followers
            for follower in current_followers:
                if follower not in followers: # if the elements in the saved list are not in the new list create a list with those missing elements
                    unfollowers_list.append(follower)
            if len(unfollowers_list) > 0: # if have missing elements
                for user in unfollowers_list:
                    unfollowers += "instagram.com/" + user + "\n"
        return unfollowers

    def get_not_follow_back(self, current_followees: list[str], current_followers: list[str]) -> str:
        """
        Return a string with the link of all that don't follow back.
        Case has none, return a empty string.
        """
        not_re_follow = ""
        for followees in current_followees:
            if followees not in current_followers:
                not_re_follow += "instagram.com/" + followees + "\n"
        return not_re_follow
        