from flask import Flask,jsonify,request,Response, make_response
from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps

RestServer = Flask(__name__)

mysql = MySQL()

RestServer.config['MYSQL_DATABASE_USER'] = 'liam.morgan'
RestServer.config['MYSQL_DATABASE_PASSWORD'] = 'EF9Q6RE6'
RestServer.config['MYSQL_DATABASE_DB'] = 'liammorgan'
RestServer.config['MYSQL_DATABASE_HOST'] = 'cs2s'
RestServer.config['SECRET_KEY'] = 'simplekey'
mysql.init_app(RestServer)
conn = mysql.connect()
cursor = conn.cursor()

def read_token(f):
	@wraps(f)
	def tokenised(*args, **kwargs):
		token = request.args.get('token')
		
		if not token:
			return jsonify({'response': 'Token is missing'}), 403
		try:
			data = jwt.decode(token, RestServer.config['SECRET_KEY'])
		except:
			return jsonify({'response': 'Token is invalid'}), 403
		return f(*args,**kwargs)
	return tokenised
	
@RestServer.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type-Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT, POST, DELETE, OPTIONS')
	return response
	
@RestServer.route("/")
def test():
	if request.authorization and request.authorization.username == 'test' and request.authorization.password == 'test':
		return "Hello"
	else:
		return make_response('Authorization failed', 401, {'WWW-Authenticate': 'Basic realm ="Login Required"'})

@RestServer.route("/sendData", methods=['POST'])
def sendData():
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	output = firstName + lastName
	sql = "INSERT INTO restDatabase(firstName, lastName) VALUES (%s, %s)"""
	cursor.execute(sql, (firstName, lastName))
	conn.commit()
	return jsonify({'output': output})
	
@RestServer.route("/getData1", methods=['GET'])
def getData():
	resultList = []
	nameToSearch = request.form['SpecData']
	cursor.execute("SELECT * FROM restDatabase WHERE firstName = nameToSearch")
	result = cursor.fetchall()
	for k in result:
		dataout = {'firstName' : k[0], 'lastName' : k[1]}
		resultList.append(dataout)
	return jsonify(resultList)

@RestServer.route("/getData2", methods=['GET'])
def getMultipleData():
	resultList = []
	cursor.execute("SELECT * FROM restDatabase")
	result = cursor.fetchall()
	for k in result:
		dataout = {'firstName' : k[0], 'lastName' : k[1]}
		resultList.append(dataout)
	return jsonify(resultList)	
	
@RestServer.route("/delete", methods=['DELETE'])
def deleteData():
	delete = request.form['Delete']
	sql = "DELETE FROM restDatabase WHERE firstName = delete"""
	cursor.execute(sql)
	conn.commit()
	
@RestServer.route("/gettoken")
def gettoken():
	if request.authorization and request.authorization.username == 'test' and request.authorization.password == 'test':
		token = jwt.encode({'user' : request.authorization.username, 'exp' : datetime.utcnow() + datetime.timedelta(minutes=30)}, RestServer.config['SECRET_KEY'])
		return jsonify({'token' : token})
	else:
		return make_response('Authorization failed', 401, {'WWW-Authenticate': 'Basic realm ="Login Required"'})

if __name__=='__main__':
	RestServer.run(host='cs2s.yorkdc.net', port=5016, debug=True)