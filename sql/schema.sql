PRAGMA foreign_keys = ON;

CREATE TABLE users(
	username VARCHAR(20) NOT NULL PRIMARY KEY,
	fullname VARCHAR(40) NOT NULL,
	email VARCHAR(40) NOT NULL,
	filename VARCHAR(64) NOT NULL,
	password VARCHAR(256) NOT NULL,
	created DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE posts(
	postid INTEGER NOT NULL PRIMARY KEY,
	filename VARCHAR(64) NOT NULL,
	owner VARCHAR(20) NOT NULL REFERENCES USERS(username) ON UPDATE CASCADE ON DELETE CASCADE,
	created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE following(
	username1 VARCHAR(20) NOT NULL REFERENCES USERS(username) ON UPDATE CASCADE ON DELETE CASCADE,
	username2 VARCHAR(20) NOT NULL REFERENCES USERS(username) ON UPDATE CASCADE ON DELETE CASCADE,
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(username1, username2)
);

CREATE TABLE comments(
	commentid INTEGER NOT NULL PRIMARY KEY,
	owner VARCHAR(20) NOT NULL REFERENCES USERS(username) ON UPDATE CASCADE ON DELETE CASCADE,
	postid INTEGER NOT NULL REFERENCES POSTS(postid) ON UPDATE CASCADE ON DELETE CASCADE,
	text VARCHAR(1024) NOT NULL,
	created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE likes(
	owner VARCHAR(20) NOT NULL REFERENCES USERS(username) ON UPDATE CASCADE ON DELETE CASCADE,
	postid INTEGER NOT NULL REFERENCES POSTS(postid) ON UPDATE CASCADE ON DELETE CASCADE,
	created DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(owner, postid)
);