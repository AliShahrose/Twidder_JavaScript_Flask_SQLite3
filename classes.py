import hashlib

def hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

class User:
    def __init__(self, email, passwordHash, firstName, lastName, gender, city, country):
        self.email = email
        self.passwordHash = passwordHash
        self.firstName = firstName
        self.lastName = lastName
        self.gender = gender
        self.city = city
        self.country = country

class Message:
    def __init__(self, user, writer, content):
        self.email = user
        self.writer = writer
        self.content = content
