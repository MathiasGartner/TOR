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