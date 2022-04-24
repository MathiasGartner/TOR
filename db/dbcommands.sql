use tor;

SET @@global.time_zone = '+00:00';

SET @@session.time_zone = '+00:00';

select * from client;

select Id, MaC, IP, Material, Latin, Position from client where Position is not null order by Position;

select * from client where position is not null order by position;

select * from client order by ip;

SELECT Id, Action, Parameters FROM useraction WHERE ClientId = 20 ORDER BY Id DESC LIMIT 1;

UPDATE client SET UserModeActive = 0;

delete from jobqueue;
insert into jobqueue (ClientId, JobCode) values (15, "U");
insert into jobqueue (ClientId, JobCode) values (15, "W");
insert into jobqueue (ClientId, JobCode) values (15, "UU");

delete from useraction;
insert into useraction (ClientId, Action, Parameters) values (20, "DOWN", 15);
insert into useraction (ClientId, Action, Parameters) values (20, "UP", 15);
insert into useraction (ClientId, Action, Parameters) values (20, "LEFT", 15);
insert into useraction (ClientId, Action, Parameters) values (20, "RIGHT", 15);
insert into useraction (ClientId, Action, Parameters) values (20, "FRONT", 15);
insert into useraction (ClientId, Action, Parameters) values (20, "BACK", 15);
insert into useraction (ClientId, Action, Parameters) values (20, "ROLL", 5);


insert into useraction (ClientId, Action, Parameters) select c.id, "DOWN", 15 FROM client c WHERE c.Id = 20 and c.AllowUserMode and c.UserModeActive;

select * from clientsettings where name = 'CAM_ISO';
select * from clientsettings where name = 'CAM_shutter_speed';
select * from clientsettings where name = 'CAM_ISO';

select * from clientsettings where clientid = 27;
select * from clientsettings where clientid = 11;
select * from clientsettings where clientid = 1;
/*
update clientsettings set value = 400 where name = 'CAM_ISO';
update clientsettings set value = 30000 where name = 'CAM_SHUTTER_SPEED';
update clientsettings set value = 20 where name = 'CAM_CONTRAST';

update clientsettings set value = 400 where name = 'CAM_ISO' and clientid in (select id from client where position in (1, 4, 7, 10, 13, 16, 19, 22, 25));
update clientsettings set value = 30000 where name = 'CAM_SHUTTER_SPEED' and clientid in (select id from client where position in (1, 4, 7, 10, 13, 16, 19, 22, 25));
update clientsettings set value = 20 where name = 'CAM_CONTRAST' and clientid in (select id from client where position in (1, 4, 7, 10, 13, 16, 19, 22, 25));

update clientsettings set value = 200 where name = 'CAM_ISO' and clientid in (select id from client where position in (2, 5, 8, 11, 14, 17, 20, 23, 26));
update clientsettings set value = 50000 where name = 'CAM_SHUTTER_SPEED' and clientid in (select id from client where position in (2, 5, 8, 11, 14, 17, 20, 23, 26));
update clientsettings set value = 20 where name = 'CAM_CONTRAST' and clientid in (select id from client where position in (2, 5, 8, 11, 14, 17, 20, 23, 26));

update clientsettings set value = 200 where name = 'CAM_ISO' and clientid in (select id from client where position in (3, 6, 9, 12, 15, 18, 21, 24, 27));
update clientsettings set value = 50000 where name = 'CAM_SHUTTER_SPEED' and clientid in (select id from client where position in (3, 6, 9, 12, 15, 18, 21, 24, 27));
update clientsettings set value = 20 where name = 'CAM_CONTRAST' and clientid in (select id from client where position in (3, 6, 9, 12, 15, 18, 21, 24, 27));
*/

select * from client where position is not null order by id;

select group_concat(c.Id separator ', ') from client c group by NULL;

select Material from client;

select * from diceresult order by id desc limit 600;

select avg(result) from diceresult where time > '2020-08-22 10:00:02';

select id, ip, concat(' - ', Material, ' - ', Latin) from client;

select group_concat(c.Material separator '","') from client c group by NULL;

select group_concat(c.Material sepeartor ', ') from client c group by 1;

select IP, Material, Latin from client;

SELECT ClientId, JobCode, JobParameters, Starttime FROM jobqueue;

update client set ip = replace(ip, ".0.", ".1.");

select replace(mac, ':', '-'), ip, concat(material, ' (', latin, ')') from client;

select mac from client;

select * from diceresult where clientid = 19 and id > 104151 order by id desc;

select * from meshpoints where y > 249;

select * from meshpoints order by z;

select * from meshpoints where clientid = 5;

select * from clientsettings where name like 'cam_%';

update clientsettings set value = 20 where name = 'CAM_CONTRAST';

select * from job;

select * from diceresult limit 5000;

delete from diceresult where id < 20000;

select * from diceresult order by id desc;

select avg(result) from diceresult where id < 16000;

select count(*) from diceresult;

select * from jobqueue;

SELECT IP FROM client WHERE Position = 1;

SELECT ClientId, JobCode, JobParameters, ExecuteAt FROM jobqueue WHERE ClientId = 19 ORDER BY Id DESC;

delete from jobqueue;

update jobqueue set jobparameters = NULL;

update jobqueue set JobCode = 'W' WHERE clientId = 7 or clientid = 12;

update jobqueue set JobCode = 'R' WHERE clientId = 7 or clientid = 12;

update jobqueue set JobCode = 'Q' WHERE clientId = 7 or clientid = 12;

select * from clientsettings; 

select * from clientsettings where clientId = 19;

delete from clientsettings where clientid = 19 and name like "CAM%";

select * from clientsettings where clientid = 7;

insert into clientsettings (clientid, name, value) select 12, Name, value from clientsettings where clientid = 7;

select * from meshpoints where clientid = 18;

select * from meshpoints where clientid = 19;

delete from meshpoints where clientid = 19 and type = "R";

INSERT INTO diceresult (ClientId, Result, Time) VALUES (7, 1, NOW());

SELECT Type, No, X, Y, Z FROM meshpoints WHERE ClientId = 1 ORDER BY Type, No;


ALTER TABLE client AUTO_INCREMENT = 1;
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:75:ec:1c', '192.168.0.101');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:e0:35:44', '192.168.0.102');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:f7:8a:a1', '192.168.0.103');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:3d:d7:1a', '192.168.0.104');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:e5:6a:07', '192.168.0.105');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:21:21:c7', '192.168.0.106');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:d8:24:99', '192.168.0.107');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:74:bc:ca', '192.168.0.108');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:e9:2c:5a', '192.168.0.109');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:c1:e8:05', '192.168.0.110');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:59:23:e1', '192.168.0.111');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:1c:e6:31', '192.168.0.112');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:8b:fb:c9', '192.168.0.113');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:c9:e4:c7', '192.168.0.114');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:16:99:2a', '192.168.0.115');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:05:aa:31', '192.168.0.116');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:ba:0a:ec', '192.168.0.117');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:15:b8:0c', '192.168.0.118');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:a2:06:a1', '192.168.0.119');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:bb:b1:ce', '192.168.0.120');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:ce:49:15', '192.168.0.121');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:64:41:71', '192.168.0.122');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:aa:86:ff', '192.168.0.123');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:42:ef:11', '192.168.0.124');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:69:c9:d6', '192.168.0.125');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:41:7f:a9', '192.168.0.126');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:de:e0:cd', '192.168.0.127');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:fc:69:cb', '192.168.0.128');
INSERT INTO client (MAC, IP) VALUES ('b8:27:eb:d7:e9:4c', '192.168.0.129');