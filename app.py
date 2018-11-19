#!flask/bin/python
from functools import wraps
from flask import Flask, jsonify, request, Response
import boto3
import os

app = Flask(__name__)
client = boto3.client(
	'ec2',
	aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
	aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'],
	region_name = 'us-east-2'
)

def check_auth(username, password):
	return username == os.environ['ACCESS_USERNAME'] and password == os.environ['ACCESS_PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return 'Healthy'

@app.route('/aws/api/v1.0/instances', methods=['GET'])
@requires_auth
def get_instances():
	response = client.describe_instances()
	print(response)
	return jsonify(response)

@app.route('/aws/api/v1.0/instances', methods=['POST'])
@requires_auth
def create_instance():
	print(request.data)
	if not request.data:
		return Response('Missing InstanceType and SubnetId', 400)
	req_data = request.get_json()

	instance_properties = {
		'ImageId': 'ami-0b59bfac6be064b78', #'ami-061e7ebbc234015fe',
		'InstanceType': req_data['InstanceType'],
		'MaxCount': 1,
		'MinCount': 1,
		'SubnetId': req_data['SubnetId']
	}

	print(instance_properties)
	response = client.run_instances(**instance_properties)
	return jsonify(response)

@app.route('/aws/api/v1.0/instances/<instanceid>', methods=['DELETE'])
@requires_auth
def delete_instance(instanceid):
	response = client.terminate_instances(InstanceIds=[instanceid])
	return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
