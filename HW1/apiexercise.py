import tweepy 
import json
import ffmpeg
import wget
import urllib.request
import io
import os
import subprocess
import sys
import glob
from PIL import Image
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Twitter API credentials
consumer_key = 'mwzfDqMTCwRxBrGtJnWiBq0Ir'
consumer_secret = 'PbmHcqAHpoAF5NqT4MjdhLCKOQXdXRYt6v6IFltypENsInrGsd'
access_key = '920695116150525953-Uf1blZlllGja7CDAHPQrVD5ZriAZNMb'
access_secret = 'u0WN80vQtLhxT1JfOCd4GU7fXBTolwfxkzzyl1kxlPtF6'


def get_func():
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    screen_name = "NBA" # You can change the twitter account name here
    Image_Number = 4 # Define the number of images to download
    # Get the tweets from a user up to 200
    tweets = api.user_timeline(screen_name = screen_name,
                               count = 200, include_rts = False,
                               exclude_replies = True)

    last_id = tweets[-1].id
    while (True):
        more_tweets = api.user_timeline(screen_name = screen_name,
                                       count = 200,
                                       include_rts = False,
                                       exclude_replies = True,
                                       max_id = last_id - 1)
        # If there are no more tweets
        if (len(more_tweets) == 0):
            break
        else:
            last_id = more_tweets[-1].id - 1
            tweets = tweets + more_tweets

    # Obtain the full path for the images
    media_files = set()
    for status in tweets:
        media = status.entities.get('media', [])
        if(len(media) > 0):
            media_files.add(media[0]['media_url'])

    # Error Control
    if (len(media_files) == 0):
        print("User current doesn't have any picture.")
        sys.exit()


    # Download at most Image_Number images
    count = 0

    for media_file in media_files:
        wget.download(media_file,'image'+str(count)+media_file[-4:])
        count += 1
        if count == Image_Number:
            break

    # Specify the path of credential file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/local/lib/googlecloudsdk/EC500hw1-70f8d0b192a0.json"
    vision_client = vision.ImageAnnotatorClient()

    #You need to change the following path to where this python code is stored
    path = glob.glob("/Users/brutto/Desktop/500/website/*.jpg") + glob.glob("/Users/brutto/Desktop/500/website/*.png")
    f = open('discription.txt', 'w') #prepare to write this file
    for file in path:
        with io.open(file,'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)
        # Performs label detection on the image file
        response = vision_client.label_detection(image=image)
        labels = response.label_annotations
        f.write("Labels:"+"\n")
        for label in labels:
            f.write(label.description+"\n")
    f.close() #finish writing the description file

    os.system("cat *.jpg | ffmpeg -f image2pipe -framerate .5 -i - -vf 'crop=in_w-1:in_h' -vcodec libx264 output.mp4")

if __name__ == '__main__':
    get_func()
