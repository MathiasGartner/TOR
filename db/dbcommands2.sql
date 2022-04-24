use tor;

select * from client;

select * from useraction order by id desc;

insert into useraction (ClientId, Action, Parameters) select c.id, "DOWN", 15 FROM client c WHERE c.Id = 5 and c.AllowUserMode and c.UserModeActive;

UPDATE client SET UserModeActive = 0 WHERE id = 1;

update client set currentState = "" WHERE ID = 15;
update client set currentState = "ROLL" WHERE ID = 15;
update client set currentState = "PICKUP_TAKEIMAGE" WHERE ID = 15;
update client set currentState = "PICKUP_PICKUP" WHERE ID = 15;

UPDATE client SET UserModeActive = 0;

select * from useraction order by id desc LIMIT 10;

insert into diceresult (ClientId, Result, X, Y, Time) values (13, 5, 0, 0, NOW());

select * from diceresult where Time > DATE_SUB(NOW(), INTERVAL 5 DAY);

SELECT * FROM diceresult WHERE ClientId = 20 AND Time > DATE_SUB(NOW(), INTERVAL 20 SECOND) ORDER BY Id DESC LIMIT 1;

SELECT IFNULL( (SELECT Result FROM diceresult WHERE ClientId = 5 AND Time > DATE_SUB(NOW(), INTERVAL 10 SECOND) ORDER BY Id DESC LIMIT 1), -1) as Result;

INSERT INTO jobqueue (ClientId, JobCode) SELECT 5 As ClientId, IFNULL( (SELECT JobCode FROM jobqueue WHERE ClientId = 5 AND (JobCode = 'W' OR JobCode = 'R') ORDER BY Id DESC LIMIT 1), 'W') AS JobCode;

SELECT 5 As Id, IFNULL( (SELECT JobCode FROM jobqueue WHERE ClientId = 5 AND JobCode <> 'U' ORDER BY Id DESC LIMIT 1), 'W') AS JobCode;

SELECT JobCode FROM jobqueue WHERE ClientId = 5 AND JobCode <> 'U' ORDER BY Id DESC LIMIT 1;

select * from jobqueue;

delete from jobqueue;
INSERT INTO jobqueue (ClientId, JobCode) VALUES (5, 'W');
INSERT INTO jobqueue (ClientId, JobCode) VALUES (11, 'R');
INSERT INTO jobqueue (ClientId, JobCode) VALUES (5, 'U');

select * from clientsettings where clientid = 4;

select count(*), value from clientsettings where name = 'CAM_SHUTTER_SPEED' group by value;

select * from clientsettings where name = 'CAM_SHUTTER_SPEED';

select * from diceresult order by id desc limit 1000;

select * from diceresult where result = 0;

select count(*), result from diceresult where time >= '2020-09-07 00:00:00' group by result;

select avg(result) from diceresult where time >= '2020-09-07 00:00:00' and result > 0;

select count(*), result from diceresult group by result;

select avg(result) from (select result from diceresult order by id desc limit 1200) as r;


