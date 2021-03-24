from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, jsonify, request
import smtplib
import json
from random import randint

from databaseHelper import *
from serverHelper import *
from classes import *


webSockets = {}

app = Flask(__name__, static_url_path = '/static')


@app.route('/')
def hello_world():
    return app.send_static_file('client.html')

@app.route('/signIn', methods = ['POST'])
def signIn():
    WebSocket()
    data = request.get_json()
    valid = validate(data, ["email", "password"])
    if not valid["success"]:
        return jsonify({"success": False, "message": valid["message"]}), 400
    result = findUser(data["email"])
    if not result["success"]:
        return jsonify({"success": False, "message": "Email not found."})
    if not (verifyPassword(data["email"], data["password"])):
        return jsonify({"success": False, "message": "Wrong password."})

    publicToken = makeToken()
    privateToken = makeToken()
    result = logIn(data["email"], publicToken, privateToken)
    oldToken = result["data"]
    if oldToken:
        ws = webSockets[oldToken]
        ws.send("GTFO!")
        webSockets.pop(oldToken)
    if not result["success"]:
        return jsonify({"success" : False, "message" : "Already signed in."}), 403

    tokens = {"public" : publicToken, "private" : privateToken}
    return jsonify({"success": True, "message": "Successfully signed in.", "data": tokens}), 200

@app.route('/signUp', methods = ['POST'])
def signUp():
    data = request.get_json()
    valid = validate(data, ["email", "password", "firstName", "lastName", "gender", "city", "country"])
    if not valid["success"]:
        return jsonify({"success": False, "message": valid["message"]})
    user = User(data["email"], hash(data["password"]), data["firstName"], data["lastName"], data["gender"], data["city"], data["country"])

    result = findUser(data["email"])
    if result["success"]:
        return jsonify({"success": False, "message": "User already exists."}), 200

    addUser(user)
    publicToken = makeToken()
    privateToken = makeToken()
    result = logIn(data["email"], publicToken, privateToken)
    tokens = {"public" : publicToken, "private" : privateToken}
    return jsonify({"success": True, "message": "Successfully signed in.", "data": tokens}), 200

@app.route('/signOut', methods = ['DELETE'])
def signOut():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    result = logOut(publicToken)

    if not result:
        return jsonify({"success" : False, "message" : "The user is not logged in."})
    return jsonify({"success" : True, "message" : "Successfully logged out."})

@app.route('/changePassword', methods = ['POST'])
def changePassword():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    data = request.get_json()
    valid = validate(data, ["oldPassword", "password"])
    if not valid["success"]:
        return jsonify({"success" : False, "message" : valid["message"]})
    if not findEmailByToken(publicToken)["success"]:
        return jsonify({"success" : False, "message" : "Not logged in."})
    email = findEmailByToken(publicToken)["data"]
    if not verifyPassword(email, data["oldPassword"]):
        return jsonify({"success" : False, "message" : "Wrong password."})
    changeThePassword(email, data["password"])
    return jsonify({"success" : True, "message" : "Password successfully changed."})

@app.route('/getUserDataByToken', methods = ['GET'])
def getUserDataByToken():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    if not findEmailByToken(publicToken)["success"]:
        return jsonify({"success" : False, "message" : "Not logged in."})
    email = findEmailByToken(publicToken)["data"]
    user = findUser(email)["data"]
    userJson = {"email" : user.email, "firstName" : user.firstName, "lastName" : user.lastName, "gender" : user.gender, "city" : user.city, "country" : user.country}
    return jsonify({"success" : True, "message" : "User data retrieved.", "data" : userJson})

@app.route('/getUserDataByEmail', methods = ['POST'])
def getUserDataByEmail():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    if not findEmailByToken(publicToken)["success"]:
        return jsonify({"success" : False, "message" : "Not logged in."})
    data = request.get_json()
    valid = validate(data, ["email"])
    if not valid["success"]:
        return jsonify({"success" : False, "message" : valid["message"]})
    user = findUser(data["email"])["data"]
    userJson = {"email" : user.email, "firstName" : user.firstName, "lastName" : user.lastName, "gender" : user.gender, "city" : user.city, "country" : user.country}
    return jsonify({"success" : True, "message" : "User data retrieved.", "data" : userJson})

@app.route('/getUserMessagesByToken', methods = ['GET'])
def getUserMessagesByToken():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    result = findEmailByToken(publicToken)
    if not result["success"]:
        return jsonify({"success" : False, "message" : "Not logged in."})
    email = result["data"]
    messages = findAllMessages(email)
    if not messages["success"]:
        return jsonify({"success" : False, "message" : "User does not exist."})
    return jsonify({"success" : True, "message" : "Messages successfully retrieved.", "data" : messages["data"]})

@app.route('/getUserMessagesByEmail', methods = ['POST'])
def getUserMessagesByEmail():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    if not findEmailByToken(publicToken)["success"]:
        return jsonify({"success" : False, "message" : "Not logged in."})
    data = request.get_json()
    valid = validate(data, ["email"])
    if not valid["success"]:
        return jsonify({"success" : False, "message" : valid["message"]})
    result = findAllMessages(data["email"])
    if not result["success"]:
        return jsonify({"success" : False, "message" : "User does not exist."})
    return jsonify({"success" : True, "message" : "Messages successfully retrieved.", "data" : result["data"]})

@app.route('/postMessage', methods = ['POST'])
def postMessage():
    publicToken = request.headers.get("token")
    if not checkToken(request):
        return jsonify({"success" : False, "message" : "Missing token from request."})
    result = findEmailByToken(publicToken)
    if not result["success"]:
        return jsonify({"success" : False, "message" : "Not logged in."})
    data = request.get_json()
    valid = validate(data, ["email", "content"])
    if not valid["success"]:
        return jsonify({"success" : False, "message" : valid["message"]})

    if not findUser(result["data"])["success"]:
        return jsonify({"success" : False, "message" : "Sender does not exist."})
    if not findUser(data["email"])["success"]:
        return jsonify({"success" : False, "message" : "Recipient does not exist."})

    addMessage(Message(data["email"], result["data"], data["content"]))
    return jsonify({"success" : True, "message" : "Message posted."})

@app.route('/webSocket')
def WebSocket():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        publicToken = ""
        while True:
            message = ws.receive()
            if not message:
                webSockets.pop(publicToken)
                break
            data = json.loads(message)
            if data["type"] == "token":
                publicToken = data["data"]
                webSockets[publicToken] = ws
    return jsonify({"success" : "who knows?", "meaning of life" : "Ice cream"}), 418

@app.route('/requestCode',  methods = ['POST'])
def forgetPassword():
    data = request.get_json()
    valid = validate(data, ["email"])
    if not valid["success"]:
        return jsonify({"success": False, "message": valid["message"]})
    result = findUser(data["email"])
    if not result["success"]:
        return jsonify({"success" : False, "message" : "Email does not exist."})

    code = randint(10000, 99999)

    fUser = getForgetfulUser(result["data"].email)
    if fUser["success"]:
        removeForgetfulUser(result["data"].email)
    addForgetfulUser(result["data"].email, code)

    subject = "Recover your Twidder password"
    body = "Enter the following code in your Twidder account: \n\n {0}".format(code)
    message = 'Subject: {}\n\n{}'.format(subject, body)
    emailFrom = "twidderapplication1@gmail.com"
    password = "laktosfrimjolk"
    emailTo = result["data"].email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(emailFrom, password)
    server.sendmail(emailFrom, emailTo, message)
    server.quit()
    return jsonify({"success" : True, "message" : "Email sent"})

@app.route('/validateCode', methods = ['POST'])
def validateCode():
    data = request.get_json()
    valid = validate(data, ["code", "email"])
    if not valid["success"]:
        return jsonify({"success": False, "message": valid["message"]})
    result = getForgetfulUser(data["email"])

    if not result["success"]:
        return jsonify({"success" : False, "message" : "User has not requested password reset."})

    if result["code"] != int(data["code"]):
        return jsonify({"success" : False, "message" : "Code invalid."})
    return jsonify({"success" : True, "message" : "Code valid."})

@app.route('/resetPassword', methods = ['POST'])
def resetPassword():
    data = request.get_json()
    valid = validate(data, ["email", "password", "code"])
    if not valid["success"]:
        return jsonify({"success": False, "message": valid["message"]})

    result = getForgetfulUser(data["email"])

    if not result["success"]:
        return jsonify({"success" : False, "message" : "User has not requested password reset."})

    if result["code"] != int(data["code"]):
        return jsonify({"success" : False, "message" : "Code invalid."})

    removeForgetfulUser(data["email"])
    changeThePassword(data["email"], data["password"])
    return jsonify({"success" : True, "message" : "Password changed successfully"})



@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(u_path):
    return jsonify({"success" : False, "message" : "Nothing posted."}), 404

if __name__ == "__main__":
    resetLoggedInUsers()
    app.debug = True
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
