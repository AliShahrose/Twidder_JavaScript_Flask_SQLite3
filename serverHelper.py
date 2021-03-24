from classes import User
from random import randint
from databaseHelper import *

from flask import Flask, jsonify, request
import json

def randomChar():
    chars = 'abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return chars[randint(0, len(chars) - 1)]

def makeToken():
    token = ""
    for I in range(0, 60):
        token += randomChar()
    return token

def validate(data, names):
    for name in names:
        if name == "password":
            if len(data["password"]) < 8:
                return {"success": False, "message": "Password length below 8."}
        if not (name in data.keys()):
            return {"success": False, "message": name + " is missing."}

    return {"success": True, "message": "Data validated."}

def formatQuotes(data):
    if type(data) is str:
        data = '"' + data + '"'
    else:
        data = str(data)
    return data

def stringify(data):
    counter = 0
    jsonString = '{'
    for key in data.keys():
        counter += 1
        jsonString += '"' + key + '":' + formatQuotes(data[key])
        if counter != len(data.keys()):
            jsonString += ','
    jsonString += '}'
    return jsonString

def checkToken(request):
    jsonString = ""
    data = request.get_json(False, True, True)
    result = findPrivateToken(request.headers.get("token"))
    if not result["success"]:
        return False
    privateToken = result["data"]
    dataHash = request.headers.get("tokenDataHash")
    if dataHash is None:
        return False
    if data is None:
        jsonString += "null" + privateToken
    else:
        jsonString += stringify(data) + privateToken
    if hash(jsonString) != dataHash:
        return False
    return True
