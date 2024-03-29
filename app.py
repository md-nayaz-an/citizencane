from flask import Flask
from flask import request, jsonify, redirect, url_for
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import requests
import numpy as np
#import scipy
import cv2
import os
#from skimage.transform import resize, pyramid_reduce
import PIL
from PIL import Image
import torch
import torch.nn.functional as F
import numpy as np
import json
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import skimage.transform
import argparse
from PIL import Image
from caption import caption_image_beam_search
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#upload model

UPLOAD_FOLDER = os.path.basename('uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model='./data/checkpoint.pth.tar'

checkpoint = torch.load(model,map_location = device)
decoder = checkpoint['decoder']
decoder = decoder.to(device)
decoder.eval()
encoder = checkpoint['encoder']
encoder = encoder.to(device)
encoder.eval()
with open('./data/word_map.json', 'r') as j:
    word_map = json.load(j)
rev_word_map = {v: k for k, v in word_map.items()}  # ix2word

@app.route('/')
def student():
   return render_template('index.html')

#blind-ears
@app.route('/result',methods = ['POST'])
def hello_world():
#    print(request.files)
    print(request.files['image'])
    file = request.files['image']

#    for param_name, param in decoder.named_parameters():
#        print(f"{param_name}: {param.device}")
#    for param_name, param in encoder.named_parameters():
#        print(f"{param_name}: {param.device}")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    img_path= './uploads'+ '/' + file.filename
    #print(img_path)
    seq, alphas = caption_image_beam_search(encoder, decoder,img_path , word_map, 1)
    words = [rev_word_map[ind] for ind in seq]
    words = words[1:]
    words = words[:len(words)-1]
    words = ' '.join(words)
    print(words)
    f=open("./templates/result.html","w")
    f.write(words)
    return words

@app.route('/return')
def setres():
    return render_template('result.html')

if __name__ == '__main__':
#    print("predicting") 
   app.debug=True
   app.run(host = '0.0.0.0',port=8888,debug=True)
