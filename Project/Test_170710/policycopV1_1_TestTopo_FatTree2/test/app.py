from flask import Flask, url_for
from flask import request
from flask import Response
from flask import jsonify
from flask import json
import thread

app = Flask(__name__)

def flaskThread():
	app.run()
flood=False
@app.route('/')
def api_root():
	return 'Welcome\n'

@app.route('/user')
def api_user():
	global flood
	if 'flood' in request.args:
		print request.args['flood']
	if request.args['flood'] == 'true':
		flood=True
	elif request.args['flood'] == 'false':
		flood=False
	return 'flood: ' + str(flood)+'\n'
@app.route('/controller')
def api_controller():
	global flood
	if flood==False:
		return 'drop'
	else:
		return 'flood'

if __name__ == '__main__':
	thread.start_new_thread(flaskThread,())
	print 123
	while True:
		print 1

