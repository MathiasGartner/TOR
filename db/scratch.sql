select * from client order by Position;

select * from jobqueue order by id desc limit 100;

select * from diceresult order by id desc limit 10;

select * from diceresult where Time >= '2021-09-06';

select * from diceresult where Time >= '2021-09-06' and UserGenerated = 1 order by id desc;

select count(*) as count, avg(result) from diceresult where Time >= '2021-09-08';

select count(*) as count, result from diceresult where Time >= '2021-09-08' group by result;

select count(*) as count, c.Material, c.Position, avg(result), clientid from diceresult d left join client c on d.clientid = c.id
where Time >= '2021-09-08' group by clientid order by count;

select * from meshpoints where clientid = 20;

select * from jobqueue order by id desc ;

UPDATE client SET AllowUserMode = 1 WHERE Id = 20;
UPDATE client SET IsActive = 0 WHERE Id = 20;
select * from client where id = 20;
