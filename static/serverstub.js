/**
 * Serverstub.js
 *
 * Simple dummy server for TDDD97
 *
 * If you're a student, you shouldn't need to look through this file,
 *  the description of how it works is in the lab instructions.
 **/
var serverstub = (function() {
  'use strict';

  var users;
  var loggedInUsers;

  var syncStorage = function(){
	if (localStorage.getItem("users") === null) {
	    users = {};
	} else {
	    users = JSON.parse(localStorage.getItem("users"));
	}

	if (localStorage.getItem("loggedinusers") === null) {
	    loggedInUsers = {};
	} else {
	    loggedInUsers = JSON.parse(localStorage.getItem("loggedinusers"));
      }

  }

  var persistUsers = function(){
    localStorage.setItem("users", JSON.stringify(users));
  };

  var persistLoggedInUsers = function(){
    localStorage.setItem("loggedinusers", JSON.stringify(loggedInUsers));
  };

  var tokenToEmail = function(token){
    return loggedInUsers[token];
  };

  var copyUser = function(user){
    return JSON.parse(JSON.stringify(user));
  };

  var serverstub = {
    signIn: function(email, password){
      syncStorage();
      if(users[email] != null && users[email].password == password){
        var letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
        var token = "";
        for (var i = 0 ; i < 36 ; ++i) {
          token += letters[Math.floor(Math.random() * letters.length)];
        }
        loggedInUsers[token] = email;
        persistLoggedInUsers();
        return {"success": true, "message": "Successfully signed in.", "data": token};
      } else {
        return {"success": false, "message": "Wrong username or password."};
      }
    },

    postMessage: function(token, content, toEmail){
      syncStorage();
      var fromEmail = tokenToEmail(token);
      if (fromEmail != null) {
        if (toEmail == null) {
          toEmail = fromEmail;
        }
        if(users[toEmail] != null){
          var recipient = users[toEmail];
          var message = {"writer": fromEmail, "content": content};
          recipient.messages.unshift(message);
          persistUsers();
          return {"success": true, "message": "Message posted"};
        } else {
          return {"success": false, "message": "No such user."};
        }
      } else {
        return {"success": false, "message": "You are not signed in."};
      }
    },

    getUserDataByToken: function(token){
      syncStorage();
      var email = tokenToEmail(token);
      return serverstub.getUserDataByEmail(token, email);
    },

    getUserDataByEmail: function(token, email){
	syncStorage();
      if (loggedInUsers[token] != null){
        if (users[email] != null) {
          var match = copyUser(users[email]);
          delete match.messages;
          delete match.password;
          return {"success": true, "message": "User data retrieved.", "data": match};
        } else {
          return {"success": false, "message": "No such user."};
        }
      } else {
        return {"success": false, "message": "You are not signed in."};
      }
    },

    getUserMessagesByToken: function(token){
      syncStorage();
      var email = tokenToEmail(token);
      return serverstub.getUserMessagesByEmail(token,email);
    },

    getUserMessagesByEmail: function(token, email){
	syncStorage();
      if (loggedInUsers[token] != null){
        if (users[email] != null) {
          var match = copyUser(users[email]).messages;
          return {"success": true, "message": "User messages retrieved.", "data": match};
        } else {
          return {"success": false, "message": "No such user."};
        }
      } else {
        return {"success": false, "message": "You are not signed in."};
      }
    },

    signOut: function(token){
      syncStorage();
      if (loggedInUsers[token] != null){
        delete loggedInUsers[token];
        persistLoggedInUsers();
        return {"success": true, "message": "Successfully signed out."};
      } else {
        return {"success": false, "message": "You are not signed in."};
      }
    },

    signUp: function(inputObject){ // {email, password, firstname, familyname, gender, city, country}
      syncStorage();
      if (users[inputObject.email] === undefined){
        if(
          (typeof(inputObject.email) === 'string') &&
          (typeof(inputObject.password) === 'string') &&
          (typeof(inputObject.firstname) === 'string') &&
          (typeof(inputObject.familyname) === 'string') &&
          (typeof(inputObject.gender) === 'string') &&
          (typeof(inputObject.city) === 'string') &&
          (typeof(inputObject.country) === 'string')
        ) {
          var user = {
            'email': inputObject.email,
            'password': inputObject.password,
            'firstname': inputObject.firstname,
            'familyname': inputObject.familyname,
            'gender': inputObject.gender,
            'city': inputObject.city,
            'country': inputObject.country,
            'messages': []
          };
            users[inputObject.email] = user;
            persistUsers();
            return {"success": true, "message": "Successfully created a new user."};
        } else {
          return {"success": false, "message": "Form data missing or incorrect type."};
        }

      } else {
        return {"success": false, "message": "User already exists."};
      }
    },

    changePassword: function(token, oldPassword, newPassword){
      syncStorage();
      if (loggedInUsers[token] != null){
        var email = tokenToEmail(token);
        if (users[email].password == oldPassword){
          users[email].password = newPassword;
          persistUsers();
          return {"success": true, "message": "Password changed."};
        } else {
          return {"success": false, "message": "Wrong password."};
        }
      } else {
        return {"success": false, "message": "You are not logged in."};
      }
    }
  };

  return serverstub;
})();
