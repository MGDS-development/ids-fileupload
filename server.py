#!/usr/bin/env python3

from flask import Flask, send_file, jsonify, Response
from flask_restful import Resource, Api, reqparse
from werkzeug import datastructures
import tempfile
import os
import uuid
import hashlib
import json

key = os.environ.get("IDS_FILEUPLOAD_APIKEY")

p1 = reqparse.RequestParser()
p1.add_argument('file',type=datastructures.FileStorage, location='files')
p1.add_argument('Authorization', location='headers')

p2 = reqparse.RequestParser()
p2.add_argument('id', type=str, location='args')
p2.add_argument('Authorization', location='headers')


app = Flask(__name__)
api = Api(app)

root_path = '/opt/ids/dynamic-data/'

'''
with open(file, 'rb') as f: # Open the file to read it's bytes
    fb = f.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
    while len(fb) > 0: # While there is still data being read from the file
        file_hash.update(fb) # Update the hash
        fb = f.read(BLOCK_SIZE) # Read the next block from the file
'''

class Download(Resource):
    def get(self):
        
        data = p2.parse_args()
        
        json_response = {'error': 'none'}
        
        if data['Authorization'] == key:        
        
            for f in os.listdir(root_path):
                
                if f.split(".")[0] == data['id']:
                    
                    print(f)
            
                    return send_file(root_path + f, as_attachment=True)
                    
        else:
            
            json_response['error'] = 'Not authorized'
            
            return Response(json.dumps(json_response), status=401, mimetype='application/json')


class Upload(Resource):
    def post(self):
        
        data = p1.parse_args()
        
        hash_file = hashlib.sha256()
        
        json_response = {'error': 'none', 'data': {'id': str(uuid.uuid4()), 'sha256sum': 0}}
        
        if data['Authorization'] == key:
        
            if data['file'] is None or data['file'].filename == '':
                
                json_response['error'] = 'No data, use "file" form parameter'
                json_response['data'] = 'none'
                
                return Response(json.dumps(json_response), status=401, mimetype='application/json')
                
            else:
                            
                file_name = root_path + json_response['data']['id'] + "." + data['file'].filename.rsplit('.', 1)[1].lower()
                
                print(file_name)
                
                data['file'].save(file_name)
                
                return Response(json.dumps(json_response), status=200, mimetype='application/json')
                
        else:
            
            json_response['error'] = 'Not authorized'
            
            return Response(json.dumps(json_response), status=401, mimetype='application/json')

            

api.add_resource(Download, "/download")
api.add_resource(Upload, "/upload")


def run(host="0.0.0.0", port=60084):
    
    app.run(debug=False, host=host, port=port)

if __name__ == '__main__':
    run()
