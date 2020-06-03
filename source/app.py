# app.py
from flask import Flask
from flask_cors import CORS, cross_origin
import os
import json

app = Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/MaskDetector", methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def index():
    os.system("detect_mask_video.py 1")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
if __name__ == "__main__":
    app.run()