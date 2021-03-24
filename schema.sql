create table users (email varchar(63) NOT NULL PRIMARY KEY,
                    passwordHash varchar(63) NOT NULL,
                    firstName varchar(63) NOT NULL,
                    lastName varchar(63) NOT NULL,
                    gender varchar(63) ,
                    city varchar(63) NOT NULL,
                    country varchar(63) NOT NULL);

create table messages (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                       email varchar(63) NOT NULL ,
                       writer varchar(63) NOT NULL,
                       content varchar(1023) NOT NULL,
                       FOREIGN KEY(email) REFERENCES users(email));

create table loggedInUsers (email varchar(63) NOT NULL PRIMARY KEY,
                              publicToken varchar(63) NOT NULL,
                              privateToken varchar(63) NOT NULL,
                              FOREIGN KEY(email) REFERENCES users(email));

create table forgetfulUsers (email varchar(63) NOT NULL PRIMARY KEY,
                             recoveryCode INTEGER NOT NULL,
                             FOREIGN KEY(email) REFERENCES users(email));
