BEGIN TRANSACTION;

CREATE TABLE children (
  id INTEGER PRIMARY KEY,
  class NUMERIC, name TEXT,
  gender NUMERIC,
  classid NUMERIC,
  FOREIGN KEY(class) REFERENCES classes(id)
);

INSERT INTO children VALUES(49,7,'B1',0,1);
INSERT INTO children VALUES(50,7,'B2',0,2);
INSERT INTO children VALUES(51,7,'B3',0,3);
INSERT INTO children VALUES(52,7,'B4',0,4);
INSERT INTO children VALUES(53,7,'B5',0,5);
INSERT INTO children VALUES(54,7,'B6',0,6);
INSERT INTO children VALUES(55,7,'B7',0,7);
INSERT INTO children VALUES(56,7,'B8',0,8);
INSERT INTO children VALUES(57,7,'B9',0,9);
INSERT INTO children VALUES(58,7,'B10',0,10);
INSERT INTO children VALUES(59,7,'B11',0,11);
INSERT INTO children VALUES(60,7,'G1',1,12);
INSERT INTO children VALUES(61,7,'G2',1,13);
INSERT INTO children VALUES(62,7,'G3',1,14);
INSERT INTO children VALUES(63,7,'G4',1,15);
INSERT INTO children VALUES(64,7,'G5',1,16);
INSERT INTO children VALUES(65,7,'G6',1,17);
INSERT INTO children VALUES(66,7,'G7',1,18);
INSERT INTO children VALUES(67,7,'G8',1,19);
INSERT INTO children VALUES(68,7,'G9',1,20);
INSERT INTO children VALUES(69,7,'G10',1,21);
INSERT INTO children VALUES(70,7,'G11',1,22);
INSERT INTO children VALUES(71,7,'B12-missing',0,23);

CREATE TABLE classes (missing NUMERIC, closed NUMERIC, id INTEGER PRIMARY KEY, name TEXT, created NUMERIC);
INSERT INTO classes VALUES(1,1,7,'testclass',1383495324.61021);

CREATE TABLE diagrams (
  id INTEGER PRIMARY KEY,
  class NUMERIC NOT NULL,
  type TEXT NOT NULL,
  created NUMERIC NOT NULL,
  data TEXT,
  FOREIGN KEY(class) REFERENCES classes(id)
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
INSERT INTO questionnaires VALUES(34,50,53,NULL,NULL,NULL,NULL,NULL,2,0,0,1,1,1,2,4,4,3,2,NULL,53,54,NULL,53,NULL,NULL,NULL,NULL,NULL);
INSERT INTO questionnaires VALUES(35,51,53,56,59,49,52,NULL,3,1,1,0,1,0,7,4,6,6,5,53,53,53,55,59,49,49,49,49,69);
INSERT INTO questionnaires VALUES(36,49,59,55,54,56,52,58,2,1,1,1,1,1,2,1,2,3,3,59,59,54,56,51,56,58,58,57,52);
INSERT INTO questionnaires VALUES(37,52,71,NULL,NULL,51,54,49,4,0,1,0,0,0,4,5,6,7,6,68,61,NULL,59,NULL,51,51,54,NULL,NULL);
INSERT INTO questionnaires VALUES(38,53,51,56,50,49,52,58,4,1,1,0,1,0,6,4,4,6,5,51,50,55,59,59,49,49,49,49,69);
INSERT INTO questionnaires VALUES(39,54,56,57,59,NULL,NULL,NULL,2,1,1,1,1,1,1,1,1,1,1,59,51,57,57,51,62,NULL,NULL,NULL,52);
INSERT INTO questionnaires VALUES(40,55,64,59,62,58,69,49,1,0,0,1,0,1,1,1,1,1,1,59,59,59,59,59,66,58,58,58,69);
INSERT INTO questionnaires VALUES(41,56,57,54,59,49,52,69,1,0,0,1,1,1,1,1,1,1,1,59,51,54,49,59,49,49,49,63,69);
INSERT INTO questionnaires VALUES(42,57,56,54,59,49,62,NULL,2,0,0,1,1,1,1,1,1,2,2,59,51,54,49,59,49,49,49,49,69);
INSERT INTO questionnaires VALUES(43,58,51,53,71,56,49,NULL,4,1,0,1,1,0,4,4,6,2,3,51,51,54,49,51,56,49,49,49,52);
INSERT INTO questionnaires VALUES(44,59,60,55,70,49,58,NULL,2,0,1,1,1,1,2,3,6,4,1,60,60,55,49,55,58,49,58,58,51);
INSERT INTO questionnaires VALUES(45,60,66,70,65,62,69,NULL,2,1,1,1,1,0,3,2,3,3,3,65,59,54,NULL,NULL,49,NULL,NULL,NULL,52);
INSERT INTO questionnaires VALUES(46,61,68,60,59,52,50,69,2,1,0,1,1,0,2,1,3,2,2,51,68,53,49,59,49,55,52,64,69);
INSERT INTO questionnaires VALUES(47,62,64,69,49,57,54,NULL,4,1,1,1,1,0,5,5,4,4,6,55,69,55,70,49,66,54,57,NULL,69);
INSERT INTO questionnaires VALUES(48,63,64,62,49,57,NULL,NULL,2,1,0,1,1,1,1,1,1,2,1,49,49,54,66,50,57,NULL,NULL,54,52);
INSERT INTO questionnaires VALUES(49,64,63,62,65,70,58,71,2,1,1,1,1,1,2,1,2,2,3,65,53,63,59,67,56,49,54,62,52);
INSERT INTO questionnaires VALUES(50,65,64,63,67,52,71,58,2,1,1,1,1,0,2,2,4,4,7,59,60,59,49,59,64,56,57,54,52);
INSERT INTO questionnaires VALUES(51,66,70,60,57,69,55,49,2,1,1,1,1,1,1,2,1,1,2,68,70,54,49,59,49,58,49,58,69);
INSERT INTO questionnaires VALUES(52,67,65,62,63,49,56,54,4,1,1,1,1,1,4,2,6,5,6,59,53,55,64,65,49,NULL,49,NULL,69);
INSERT INTO questionnaires VALUES(53,68,66,61,65,53,NULL,NULL,2,1,1,1,1,0,1,2,4,3,3,57,70,66,55,59,69,49,56,NULL,52);
INSERT INTO questionnaires VALUES(54,69,62,63,65,49,NULL,58,3,1,1,1,0,1,4,3,2,3,4,67,51,54,59,65,58,49,62,71,52);
INSERT INTO questionnaires VALUES(55,70,60,66,59,55,52,50,2,1,1,0,1,1,4,3,3,4,4,65,61,54,49,NULL,49,58,49,58,69);
INSERT INTO questionnaires VALUES(56,71,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);

CREATE TABLE tempfiles (filename TEXT, id INTEGER PRIMARY KEY, hash TEXT, data BLOB);
CREATE UNIQUE INDEX i1 ON questionnaires(child);

COMMIT;