BEGIN TRANSACTION;

CREATE TABLE children (
  id INTEGER PRIMARY KEY,
  class NUMERIC, name TEXT,
  gender NUMERIC,
  classid NUMERIC,
  FOREIGN KEY(class) REFERENCES classes(id)
);

CREATE TABLE classes (
  id INTEGER PRIMARY KEY,
  name TEXT,
  created NUMERIC
);

CREATE TABLE friendships (
  id INTEGER PRIMARY KEY,
  who NUMERIC,
  likes NUMERIC,
  FOREIGN KEY(who) REFERENCES children(id),
  FOREIGN KEY(likes) REFERENCES children(id)
);

CREATE TABLE questionnaires(
  id INTEGER PRIMARY KEY,
  child NUMERIC,
  friend1 NUMERIC,
  friend2 NUMERIC,
  friend3 NUMERIC,
  antipathy1 NUMERIC,
  antipathy2 NUMERIC,
  antipathy3 NUMERIC,
  selfeval NUMERIC,
  yesnoquest1 NUMERIC,
  yesnoquest2 NUMERIC,
  yesnoquest3 NUMERIC,
  yesnoquest4 NUMERIC,
  yesnoquest5 NUMERIC,
  scale1 NUMERIC,
  scale2 NUMERIC,
  scale3 NUMERIC,
  scale4 NUMERIC,
  scale5 NUMERIC,
  traits1 NUMERIC,
  traits2 NUMERIC,
  traits3 NUMERIC,
  traits4 NUMERIC,
  traits5 NUMERIC,
  traits6 NUMERIC,
  traits7 NUMERIC,
  traits8 NUMERIC,
  traits9 NUMERIC,
  traits10 NUMERIC,
  FOREIGN KEY(child) REFERENCES children(id),
  FOREIGN KEY(friend1) REFERENCES children(id),
  FOREIGN KEY(friend2) REFERENCES children(id),
  FOREIGN KEY(friend3) REFERENCES children(id),
  FOREIGN KEY(antipathy1) REFERENCES children(id),
  FOREIGN KEY(antipathy2) REFERENCES children(id),
  FOREIGN KEY(antipathy3) REFERENCES children(id),
  FOREIGN KEY(traits1) REFERENCES children(id),
  FOREIGN KEY(traits2) REFERENCES children(id),
  FOREIGN KEY(traits3) REFERENCES children(id),
  FOREIGN KEY(traits4) REFERENCES children(id),
  FOREIGN KEY(traits5) REFERENCES children(id),
  FOREIGN KEY(traits6) REFERENCES children(id),
  FOREIGN KEY(traits7) REFERENCES children(id),
  FOREIGN KEY(traits8) REFERENCES children(id),
  FOREIGN KEY(traits9) REFERENCES children(id),
  FOREIGN KEY(traits10) REFERENCES children(id)
);

CREATE UNIQUE INDEX i1 ON questionnaires(child);

CREATE TABLE diagrams (
  id INTEGER PRIMARY KEY,
  class NUMERIC NOT NULL,
  type TEXT NOT NULL,
  created NUMERIC NOT NULL,
  data TEXT,
  FOREIGN KEY(class) REFERENCES classes(id)
);


COMMIT;
