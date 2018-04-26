import tweepy
import json
import ffmpeg
import wget
import urllib.request
import io
import os
import re
import requests
import subprocess
import sys
from PIL import Image
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

from pymongo import MongoClient
import pprint
import bson

# Twitter API credentials
consumer_key = 'mwzfDqMTCwRxBrGtJnWiBq0Ir'
consumer_secret = 'PbmHcqAHpoAF5NqT4MjdhLCKOQXdXRYt6v6IFltypENsInrGsd'
access_key = '920695116150525953-Uf1blZlllGja7CDAHPQrVD5ZriAZNMb'
access_secret = 'u0WN80vQtLhxT1JfOCd4GU7fXBTolwfxkzzyl1kxlPtF6'



@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status

def call_api():
    # authorize twitter, initialize tweepy
    screen_name = "NBA"
    lable_output = "label.json"
    Image_Number = 4
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

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

    count = 0

    for media_file in media_files:
        #print(media_file)
        wget.download(media_file,'image'+str(count)+media_file[-4:])

        count += 1
        if count == Image_Number:
            break

    # Instantiates a client, specify the cert file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/local/lib/googlecloudsdk/EC500hw1-70f8d0b192a0.json"
    client = vision.ImageAnnotatorClient()

    data = {}
    data['Pictures'] = []
    data['Account'] = screen_name
    pictures = [pic for pic in os.listdir(".") if pic.endswith('jpg')]
    picNum = 0
    order = 0
    for i in pictures:

        file = os.path.join(os.path.dirname(__file__),i)
        new = str(picNum) +'.jpg'
        os.renames(file, new)
        Subject = {}
        picNum = picNum + 1

        # Loads the image into memory
        with io.open(new, 'rb') as image_file:
             content = image_file.read()

        image = types.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations

        label_list = []
        for label in labels:
           label_list.append(label.description)

        Subject[str(order)] =  label_list
        data['Pictures'].append(Subject)

        order = order + 1
        
    #Create json file
    with open(lable_output,'w') as JSONObject:
        json.dump(data, JSONObject, indent = 4, sort_keys = True)
    #Initialize MongoDB
    client = MongoClient()
    db = client.picture.database
    collection = db.picture_collection
    db.posts.insert(data)

    pprint.pprint(db.posts.find_one({'Account':screen_name}))

    os.system("cat *.jpg | ffmpeg -f image2pipe -framerate .5 -i - -vf 'crop=in_w-1:in_h' -vcodec libx264 video.mp4")

if __name__ == '__main__':
    call_api()
