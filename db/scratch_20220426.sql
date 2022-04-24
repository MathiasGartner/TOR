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