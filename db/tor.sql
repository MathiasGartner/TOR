use tor;

# alle Würfelboxen nach Position sortiert anzeigen
select * from client where position is not null order by position;

# UserModeActiv bei allen Würfelboxen deaktivieren
UPDATE client SET UserModeActive = 0;

set @boxId = 16;

update client set currentState = "" WHERE ID = @boxId;
update client set currentState = "ROLL" WHERE ID = @boxId;
update client set currentState = "PICKUP_TAKEIMAGE" WHERE ID = @boxId;
update client set currentState = "PICKUP_PICKUP" WHERE ID = @boxId;

delete from useraction;
insert into useraction (ClientId, Action, Parameters) values (@boxId, "DOWN", 15);
insert into useraction (ClientId, Action, Parameters) values (@boxId, "UP", 15);
insert into useraction (ClientId, Action, Parameters) values (@boxId, "LEFT", 15);
insert into useraction (ClientId, Action, Parameters) values (@boxId, "RIGHT", 15);
insert into useraction (ClientId, Action, Parameters) values (@boxId, "FRONT", 15);
insert into useraction (ClientId, Action, Parameters) values (@boxId, "BACK", 15);
insert into useraction (ClientId, Action, Parameters) values (@boxId, "ROLL", 5);

insert into diceresult (ClientId, Result, X, Y, Time) values (@boxId, 5, 0, 0, NOW());

delete from jobqueue;
INSERT INTO jobqueue (ClientId, JobCode) VALUES (@boxId, 'W');
INSERT INTO jobqueue (ClientId, JobCode) VALUES (@boxId, 'R');
INSERT INTO jobqueue (ClientId, JobCode) VALUES (@boxId, 'U');

select * from jobqueue order by id desc;

