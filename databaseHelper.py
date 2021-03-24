import sqlite3
from classes import User, Message, hash

DATABASE_URI = "database.db"

def executeDB(statement):
    connection = sqlite3.connect(DATABASE_URI)
    c = connection.cursor()
    c.execute(statement)
    connection.commit()
    connection.close()

def findOneDB(statement):
    connection = sqlite3.connect(DATABASE_URI)
    c = connection.cursor()
    c.execute(statement)
    data = c.fetchone()
    connection.close()
    return data

def findAllDB(statement):
    connection = sqlite3.connect(DATABASE_URI)
    c = connection.cursor()
    c.execute(statement)
    data = c.fetchall()
    connection.close()
    return data

def findTokenByEmail(userEmail):
    userTuple = findOneDB('SELECT * from loggedInUsers where email = "{}"'.format(userEmail))
    if (userTuple == None):
        return {"success" : False}
    return {"success" : True, "data" : userTuple[1]}

def findEmailByToken(publicToken):
    userTuple = findOneDB('SELECT * from loggedInUsers where publicToken = "{}"'.format(publicToken))
    if userTuple == None:
        return {"success" : False, "message" : "Token not found."}
    return {"success" : True, "data" : userTuple[0]}


def logOut(publicToken):
    if not (findEmailByToken(publicToken)["success"]):
        return False
    executeDB('DELETE FROM loggedInUsers WHERE publicToken="{}"'.format(publicToken))
    return True

def logIn(userEmail, publicToken, privateToken):
    result = findTokenByEmail(userEmail)
    oldToken = None
    if result["success"]:
        oldToken = result["data"]
        print("old token : ", oldToken)
        logOut(oldToken)

    executeDB('INSERT INTO loggedInUsers VALUES("{0}", "{1}", "{2}")'.format(userEmail, publicToken, privateToken))
    return {"success" : True, "message" : "Successfully logged in", "data" : oldToken}

def addUser(user):
    executeDB('INSERT INTO users VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}")'.format(user.email, user.passwordHash, user.firstName, user.lastName, user.gender, user.city, user.country))

def addMessage(message):
    executeDB('INSERT INTO messages (email, writer, content) VALUES ("{0}", "{1}", "{2}")'.format(message.email, message.writer, message.content))

def findAllMessages(email):
    userTuple = findAllDB('SELECT * from messages where email = "{}"'.format(email))
    if (userTuple == None):
        return {"success" : False}
    allMessages = []
    for message in userTuple:
        msg = {"email" : message[1], "writer" : message[2], "content" : message[3]}
        allMessages.append(msg)
    return {"success" : True, "data" : allMessages}

def findUser(email):
    userTuple = findOneDB('SELECT * from users where email = "{}"'.format(email))
    if (userTuple == None):
        return {"success" : False}
    user = User(userTuple[0], userTuple[1], userTuple[2], userTuple[3], userTuple[4], userTuple[5], userTuple[6])
    return {"success" : True, "data" : user}

def findPrivateToken(publicToken):
    userTuple = findOneDB('SELECT * from loggedInUsers where publicToken = "{}"'.format(publicToken))
    if (userTuple == None):
        return {"success" : False}
    return {"success" : True, "data" : userTuple[2]}

def changeThePassword(userEmail, newPassword):
    executeDB('UPDATE users SET passwordHash = "{0}" where email = "{1}"'.format(hash(newPassword), userEmail))

def verifyPassword(userEmail, password):
    valid = findUser(userEmail)["data"].passwordHash == hash(password)
    return valid

def resetLoggedInUsers():
    executeDB('DELETE FROM loggedInUsers')

def addForgetfulUser(email, code):
    executeDB('INSERT INTO forgetfulUsers (email, recoveryCode) VALUES ("{0}", {1})'.format(email, code))

def getForgetfulUser(email):
    data = findOneDB('SELECT * FROM forgetfulUsers WHERE email = "{}"'.format(email))
    if (data == None):
        return {"success" : False}
    return {"success" : True, "code" : data[1]}

def removeForgetfulUser(email):
    executeDB('DELETE FROM forgetfulUsers WHERE email = "{}"'.format(email))

def createMockData():
    connection = sqlite3.connect(DATABASE_URI)
    c = connection.cursor()
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM messages")
    connection.commit()
    connection.close()
    user = User("test@gmail.com", hash("abcde"),"John","Smith","Decidedly male","Kansas City","Murica")
    user2 = User("fail@gmail.com", hash("abcdef"),"John","Wick","Surely male","Missouri","Murica")

    message = Message(user.email, user.email, "Hello World!")
    message2 = Message(user.email, user2.email, "Hej World!")

    addUser(user)
    addUser(user2)
    addMessage(message)
    addMessage(message2)
