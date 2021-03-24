/****************************************************************************
                             VIEWS - START
****************************************************************************/

window.onload = function() {
  setView();
}

setView = function() {
  removeAlert();

  sendRequest("GET", "/getUserDataByToken", null, function(response) {
    if (response.success) {
      history.pushState(null, null, "Profile");
      switchView(1);
    } else {
      history.pushState(null, null, "Welcome");
      switchView(0);
    }
  });
}

switchView = function(view) {
  var bodyDiv = document.getElementById("bodyDiv");
  var welcomeViewDiv = document.getElementById("welcomeView");
  var profileViewDiv = document.getElementById("profileView");

  if(!view) {
    bodyDiv.innerHTML = welcomeViewDiv.innerHTML;
  } else {
    bodyDiv.innerHTML = profileViewDiv.innerHTML;
  }
}

/****************************************************************************
                             VIEWS - END
****************************************************************************/

/****************************************************************************
                             UTILITIES - START
****************************************************************************/

function shaHash(message) {

    return sha256(message);

}

sendRequest = function(method, path, payload, lambda) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        console.log(this.responseText)
        lambda(JSON.parse(this.responseText));
      }
  };

  var privateToken = localStorage.getItem("privateToken");

  xhttp.open(method, path, true);
  if (privateToken) {
    xhttp.setRequestHeader("token", localStorage.getItem("publicToken"));
    xhttp.setRequestHeader("tokenDataHash", shaHash(JSON.stringify(payload) + privateToken));
  }
  xhttp.setRequestHeader("Content-type", "application/JSON");
  if (method == "GET" || method == "DELETE") {
    xhttp.send();
  } else {
    xhttp.send(JSON.stringify(payload));
  }
}

openSocket = function(route) {
  socket = new WebSocket(route);
  socket.onopen = function(){
    console.log("Hello Server at Client!")

    var tokenData = {
      'type' : 'token',
      'data' : localStorage.getItem("publicToken")
    }
    console.log(JSON.stringify(tokenData))
    socket.send(JSON.stringify(tokenData));
  }

  socket.onmessage = function(event) {
    console.log(event.data)
    setView();
  }
}

const contentAlternatives = ["profileHome", "profileBrowse", "profileAccount"];

clickButton = function(name) {
  for (var i = 0; i < contentAlternatives.length; i++) {
    if (contentAlternatives[i] != name) {
      document.getElementById(contentAlternatives[i]).style.display = "none";
    }
  }
  document.getElementById(name).style.display = "block";
  history.pushState(null, null, name.substring(7,));
}

myAlert = function(alert) {
  document.getElementById("alertHeader").innerHTML = alert;
  document.getElementById("extraDiv").style.display = "block";
}

removeAlert = function() {
  document.getElementById("extraDiv").style.display = "none";
}

removeChildNodes = function(parent) {
  while (parent.firstChild) {
    parent.removeChild(parent.firstChild);
  }
}

/****************************************************************************
                             UTILITIES - END
****************************************************************************/

/****************************************************************************
                             SIGNING - START
****************************************************************************/

signInSubmit = function() {



  var email = document.getElementById("signInEmail").value;
  var pass = document.getElementById("signInPassword").value;

  var user = {
    'email': email,
    'password': pass
  };
  sendRequest("POST", "/signIn", user, function(response) {
    if (response.success) {
      localStorage.setItem("publicToken", response.data.public);
      localStorage.setItem("privateToken", response.data.private);
      openSocket("ws://localhost:5000/webSocket");
      setView();
    } else {
      myAlert(response.message);
      //myAlert(shaHash("Hej"));
    }
  });
}

signUpSubmit = function() {

  if(!isPasswordSame()) {
    myAlert("Passwords do not match");
  } else if(!isPasswordLengthy()) {
    myAlert("Password length must be at least 8 characters");
  } else {
    var email = document.getElementById("signUpEmail").value;
    var pass = document.getElementById("signUpPassword").value;

    var signUpObject = {
      email: email,
      password: pass,
      firstName: document.getElementById("signUpFirstName").value,
      lastName: document.getElementById("signUpLastName").value,
      gender: document.getElementById("signUpGender").value,
      city: document.getElementById("signUpCity").value,
      country: document.getElementById("signUpCountry").value
    };

    sendRequest("POST", "/signUp", signUpObject, function(response) {
      if (response.success) {
        localStorage.setItem("publicToken", response.data.public);
        localStorage.setItem("privateToken", response.data.private);
        openSocket("ws://localhost:5000/webSocket");
        setView();
      } else {
        myAlert(response.message);
      }
    });
  }
}

signOutSubmit = function() {
  sendRequest("DELETE", "/signOut", null, function(response) {
    if (response.success) {
      localStorage.removeItem("publicToken");
      localStorage.removeItem("privateToken");
      setView();
    } else {
      myAlert(response.message);
    }
  });
}

isPasswordSame = function() {
  var pass = document.getElementById("signUpPassword").value;
  var repeat = document.getElementById("signUpRepeatPassword").value;
  return pass == repeat;
}

isPasswordLengthy = function() {
  var pass = document.getElementById("signUpPassword").value;
  return ((parseInt(pass.length) >= 8));
}

changePassword = function() {

  var prevPassword = document.getElementById("prevPassword").value;
  var newPassword = document.getElementById("newPassword").value;
  var newPasswordRepeat = document.getElementById("newPasswordRepeat").value;
  if (newPassword != newPasswordRepeat) {
    myAlert("New passwords must match.");
  } else if (parseInt(newPassword.length) < 8) {
    myAlert("Password length must be at least 8 characters");
  } else {
    var package = {
      oldPassword : prevPassword,
      password : newPassword
    };
    sendRequest("POST", "/changePassword", package, function(response) {
     myAlert(JSON.stringify(response));
    });
  }
}

/****************************************************************************
                             SIGNING - END
****************************************************************************/

/****************************************************************************
                             USER - START
****************************************************************************/

printUser = function(user, specifier) {

  document.getElementById("email" + specifier).innerHTML = user["email"];
  document.getElementById("firstName" + specifier).innerHTML = user["firstName"];
  document.getElementById("lastName" + specifier).innerHTML = user["lastName"];
  document.getElementById("gender" + specifier).innerHTML = user["gender"];
  document.getElementById("city" + specifier).innerHTML = user["city"];
  document.getElementById("country" + specifier).innerHTML = user["country"];
  refreshWall(user["email"], specifier);

}

printMe = function() {
  sendRequest("GET", "/getUserDataByToken", null, function(response) {
    printUser(response.data, "Home");
  });
}

searchUser = function() {
  var emailJson = {
    email : document.getElementById("searchUserEmail").value
  };
  sendRequest("POST", "/getUserDataByEmail", emailJson, function(response) {
    history.pushState(null, null, response.data["firstName"] + response.data["lastName"]);
    printUser(response.data, "Browse");
  });
}

createMessages = function(parent, token, email) {
  var emailJson = {
    email : email
  };

  sendRequest("POST", "/getUserMessagesByEmail", emailJson, function(response) {
    var messages = response.data;
    for (var i = 0; i < messages.length; ++i) {
      var firstRow = document.createElement("div");
      var secondRow = document.createElement("div");
      var messageDiv = document.createElement("div");
      messageDiv.classList.add("Message");

      messageDiv.appendChild(firstRow);
      messageDiv.appendChild(secondRow);

      firstRow.appendChild(document.createTextNode("Sent by: " + messages[i].writer));
      secondRow.appendChild(document.createTextNode("Message: " + messages[i].content));

      parent.appendChild(messageDiv);
    }
  });
}

postMessage = function(specifier) {
  var post = {
    email : document.getElementById("email" + specifier).innerHTML,
    content : document.getElementById("messageBox" + specifier).value
  };
  sendRequest("POST", "/postMessage", post, function(response) {});
}

refreshWall = function(email, specifier) {
  var token = localStorage.getItem("publicToken");
  var wall = document.getElementById("wall" + specifier);
  removeChildNodes(wall);
  createMessages(wall, token, email);
}

refreshButton = function(specifier) {
  var email = document.getElementById("email" + specifier).innerHTML;
  refreshWall(email, specifier);
}

/****************************************************************************
                             USER - END
****************************************************************************/

/****************************************************************************
                             HTML BUTTONS - START
****************************************************************************/

clickHome = function() {
  printMe();
  clickButton(contentAlternatives[0]);
}

clickBrowse = function() {
  clickButton(contentAlternatives[1]);
}

clickAccount = function() {
  clickButton(contentAlternatives[2]);
}

postMessageHome = function() {
  postMessage("Home");
}

postMessageBrowse = function() {
  postMessage("Browse");
}

refreshButtonHome = function() {
  refreshButton("Home");
}

refreshButtonBrowse = function() {
  refreshButton("Browse");
}

goHome = function() {
  setView(0)
}

forgetButton = function() {
  var forgetPasswordDiv = document.getElementById("forgetPasswordView");

  bodyDiv.innerHTML = forgetPasswordDiv.innerHTML;
  history.pushState(null, null, "RecoverPassword");
}

sendEmail = function() {
  var email = document.getElementById("recoverEmail").value;
  var data = {
    'email': email
  };
  localStorage.setItem("myEmail", email);
  sendRequest("POST", "/requestCode", data, function(response) {
    if(response.success) {
      document.getElementById("sendCodeForm").style.display = "block";
      document.getElementById("codeText").style.display = "block";
      document.getElementById("sendEmailForm").style.display = "none";
    } else {
      myAlert (response.message);
    }
  });
}

sendCode = function() {
  var code = document.getElementById("recoverCode").value;

  var data = {
    'code': code,
    'email': localStorage.getItem("myEmail")
  }
  sendRequest("POST", "/validateCode", data, function(response){
    if (response.success) {
      localStorage.setItem("myCode", code);
      document.getElementById("resetPasswordForm").style.display = "block";
      document.getElementById("sendCodeForm").style.display = "none";
      document.getElementById("codeText").style.display = "none";
    } else {
      myAlert(response.message);
    }
  });

}

resetPasswordButton = function() {

  var newPassword = document.getElementById("resetNewPassword").value;
  var newPasswordRepeat = document.getElementById("resetRepeatPassword").value;
  if (newPassword != newPasswordRepeat) {
    myAlert("New passwords must match.");
  } else if (parseInt(newPassword.length) < 8) {
    myAlert("Password length must be at least 8 characters");
  } else {
    var data = {
      'email': localStorage.getItem("myEmail"),
      'password': newPassword,
      'code': localStorage.getItem("myCode")
    };

    sendRequest("POST", "/resetPassword", data, function(response) {
      if(response.success) {
        document.getElementById("resetText").style.display = "block";
      } else {
        myAlert(response.message)
      }
    });
  }
}

/****************************************************************************
                             HTML BUTTONS - END
****************************************************************************/
