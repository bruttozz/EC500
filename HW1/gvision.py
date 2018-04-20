import io
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/usr/local/lib/googlecloudsdk/EC500hw1-70f8d0b192a0.json"
from google.cloud import vision
from google.cloud.vision import types
vision_client = vision.ImageAnnotatorClient()
file_name = 'image3.jpg'
with io.open(file_name,'rb') as image_file:
    content = image_file.read()
    image = types.Image(content=content)
response = vision_client.label_detection(image=image)
labels = response.label_annotations
for label in labels:
    print(label.description)
