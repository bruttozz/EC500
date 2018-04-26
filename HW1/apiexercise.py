import tweepy
import json
import ffmpeg
import wget
import urllib.request
import io
import os
import sys
import glob

from PIL import Image

from google.cloud import vision
from google.cloud.vision import types

# Twitter API credentials
consumer_key = 'mwzfDqMTCwRxBrGtJnWiBq0Ir'
consumer_secret = 'PbmHcqAHpoAF5NqT4MjdhLCKOQXdXRYt6v6IFltypENsInrGsd'
access_key = '920695116150525953-Uf1blZlllGja7CDAHPQrVD5ZriAZNMb'
access_secret = 'u0WN80vQtLhxT1JfOCd4GU7fXBTolwfxkzzyl1kxlPtF6'

# Reference:
    # https://miguelmalvarez.com/2015/03/03/download-the-pictures-from-a-twitter-feed-using-python/
def getimg(account):
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    # Get the tweets from a user up to 200
    tweets = api.user_timeline(account = account,
                               count = 200, include_rts = False,
                               exclude_replies = True)

    last_id = tweets[-1].id
    while (True):
        more_tweets = api.user_timeline(account = account,
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

    f = open('pictures_urls.txt', 'w')
    for media_file in media_files:
        wget.download(media_file,'image'+str(count)+media_file[-4:])
        f.write(media_file)
        count += 1
        if count == Image_Number:
            break

def description():
    # Specify the path of credential file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/local/lib/googlecloudsdk/EC500hw1-70f8d0b192a0.json"
    vision_client = vision.ImageAnnotatorClient()
    path = glob.glob("/Users/brutto/Desktop/500/*.jpg") + glob.glob("/Users/brutto/Desktop/500/*.png")
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

if __name__ == '__main__':
    account = input("Please Enter a Twitter Account Name")
    Image_Number = input("Please Enter How Many Pictures You Want to Display ")
    getimg(account)
    description()
    os.system("cat *.jpg | ffmpeg -f image2pipe -framerate .5 -i - -vf 'crop=in_w-1:in_h' -vcodec libx264 output.mp4")
    print("Finished!")
