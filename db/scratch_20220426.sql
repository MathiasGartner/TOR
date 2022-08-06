use tor;

select * from client;

select Id, Position, IP, Material, Latin from client;

select * from diceresult order by id desc;

select * from job;

select * from jobqueue;

WITH ranked_jobs AS (
  SELECT j.ClientId, j.JobCode, ROW_NUMBER() OVER (PARTITION BY ClientId ORDER BY id DESC) AS rj
  FROM jobqueue AS j
)
SELECT * FROM ranked_jobs j LEFT JOIN client c ON c.ID = j.ClientId WHERE rj = 1 AND c.Position IS NOT NULL;

select * from diceresult;

WITH ranked_results AS (
  SELECT d.ClientId, d.Result, ROW_NUMBER() OVER (PARTITION BY ClientId ORDER BY id DESC) AS rr
  FROM diceresult AS d
)
SELECT c.Id, AVG(r.Result) AS ResultAverage, STDDEV(r.Result) AS ResultStddev FROM ranked_results r LEFT JOIN client c ON c.ID = r.ClientId WHERE rr < 100 AND c.Position IS NOT NULL GROUP BY r.ClientId;

ALTER TABLE client ADD IsActive tinyint NOT NULL DEFAULT 0;

INSERT INTO clientlog (ClientId, MessageType, MessageCode, Message) VALUES (27, 'ERRROR', 'NOT_LOC', 'Could not locate die.');

select * from clientlog order by id desc;

select * from diceresult where clientid = 25 and time >= '2022-04-28 16:41:00' order by id desc;

select * from diceresult where clientid = 8 and time >= '2022-04-28 16:41:00' order by id desc;

select * from diceresult where time >= '2021-10-10 00:00:00';

update diceresult set source = 'Test2022' where time >= '2021-10-10 00:00:00';

select count(*), result from diceresult where clientid = 25 and time >= '2022-04-24 09:00:00' group by result;

select count(*), result from diceresult where Source = 'CyberArts2021' group by result;

select count(*), result from diceresult where Source = 'ArsElectronica2020' group by result;

select distinct Source from diceresult;

select avg(Z), avg(Y) from meshpoints where Type = 'M';

INSERT INTO jobqueue (ClientId, JobCode) VALUES (8, 'R');

INSERT INTO jobqueue (ClientId, JobCode, JobParameters) VALUES (11, 'RW', '10 5 5');

select * from jobqueue order by id desc limit 1;

select * from client where id = 11;

WITH ranked_jobs AS (
  SELECT j.ClientId, j.JobCode, j.JobParameters, j.ExecuteAt, ROW_NUMBER() OVER (PARTITION BY ClientId ORDER BY id DESC) AS rj
  FROM jobqueue AS j
)
SELECT c.Id, j.JobCode, j.JobParameters, j.ExecuteAt FROM ranked_jobs j LEFT JOIN client c ON c.ID = j.ClientId WHERE rj = 1 AND c.Position IS NOT NULL;


select * from jobprogram;

select distinct name from jobprogram;

SELECT DISTINCT Name FROM jobprogram;

SELECT Name, ClientId, JobCode, JobParameters FROM jobprogram;

SELECT ClientId AS Id, JobCode, JobParameters FROM jobprogram WHERE Name = 'Run all';






select * from clientlog where clientid = 16 order by id desc;
select * from client;
update client set IP = "192.168.1.103", MAC = "b8:27:eb:9c:33:9d" where ID = 15;
insert into jobqueue(ClientId, JobCode) values (15,"W");
select * from jobqueue;

select * from client order by position;

update client set position = NULL where id = 3;

update client set position = 8 where id = 14;

use tor;

update client set AllowUserMode = 0;
update client set UserModeActive = 0;
update client set CurrentState = "";
update client set IsActive = 1;
update client set IsActive = 0 WHERE Position IS NULL;

select * from jobprogram;


delete from jobprogram;

select * from clientsettings where ClientId = 4;

select * from clientsettings where Name = "CAM_ISO";

select * from client where position = 27;

select count(*) from diceresult;

select Id, Position, MAC, IP as IPAdress, Latin as Name from client where position is not null order by position;


select distinct source from diceresult;

select source, count(*) from diceresult group by source;
select result, count(*) from diceresult where source = 'Kapelica2022' group by result;

select count(*), value from clientsettings where Name = "CAM_SHUTTER_SPEED" group by value;


select * from clientsettings where Name = "CAM_SHUTTER_SPEED" order by value;

select * from client

select c.position, c.material, count(*) as count from diceresult d left join client c on c.id = d.ClientId
where Time >= '2022-06-07 15:10:00' and c.position in (25, 19, 9, 20, 4, 13, 27, 1) group by d.ClientId order by count;

select * from diceresult where clientId = 15 order by id desc;

select * from clientsettings where clientid = 6;

select count(*), avg(result) from diceresult where Source = "Test2022";

select count(*), avg(result) from diceresult where Source = "Kapelica2022";

select avg(id) from diceresult where source = "test2022";

select count(*) from diceresult where id > 196000;

update diceresult set source = "Kapelica2022" where id > 196000;

select count(*), avg(result) from diceresult where Source;

select * from diceresult where UserGenerated = 1 order by id desc;

select * from jobqueue order by id desc;

select * from useraction order by id desc;

delete from useraction;

select * from client;

SELECT Id, Position, Latin FROM client WHERE IsActive = 1 AND CurrentState != "WAITING";

update client set CurrentState = "WAITING" WHERE IsActive = 1;

update client set IsActive = 0;

update client set IsActive = 1 where Position is not null;

select count(*), avg(result), stddev(result) from diceresult where time > "2022-06-15";

update client set AllowUserMode = 1 where Position in (23, 6, 12, 17, 24, 3, 11, 22, 4, 5, 16, 9, 13, 18, 21, 25);

select count(*), avg(result) from diceresult where time > "2022-06-13" group by result;

select * from diceresult where time > "2022-06-15" and usergenerated = 1;

select c.material, count(*) as dcount, avg(result) from diceresult d left join client c on c.Id = d.clientId
                                                   where time > "2022-06-10" group by clientId order by dcount;

select clientId, c.material, count(*) as dcount, avg(result) from diceresult d left join client c on c.Id = d.clientId
                                                   where time > "2022-06-10" group by clientId order by clientId;

select * from jobqueue order by id desc limit 1000;

select date(d.Time) as t, c.material, count(*) as dcount, avg(result) from diceresult d left join client c on c.Id = d.clientId
                                                   where time > "2022-06-10" group by clientId, date(d.Time) order by t, dcount;

select * from jobqueue order by id desc;

select * from useraction order by id desc;

select * from clientlog order by id desc;