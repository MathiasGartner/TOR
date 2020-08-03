
DELETE FROM tor.jobqueue;
DELETE FROM tor.diceresult;
DELETE FROM tor.job;
DELETE FROM tor.client;

INSERT INTO tor.job (Code, Name, Description) VALUES ('R', 'Roll', 'Do a die roll');
INSERT INTO tor.job (Code, Name, Description) VALUES ('W', 'Wait', 'Wait for a given number of seconds, then ask for next job');
INSERT INTO tor.job (Code, Name, Description) VALUES ('H', 'Homing', 'Do a homing move');
INSERT INTO tor.job (Code, Name, Description) VALUES ('M', 'Move', 'Move to specified position');
INSERT INTO tor.job (Code, Name, Description) VALUES ('Q', 'Quit', 'Shut down client program');

INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.101', 'C1', 'cinnamon');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.102', 'C2', 'star anise');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.103', 'C3', 'cotton');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.104', 'C4', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.105', 'C5', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.106', 'C6', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.107', 'C7', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.108', 'C8', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.109', 'C9', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.110', 'C10', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.111', 'C11', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.112', 'C12', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.113', 'C13', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.114', 'C14', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.115', 'C15', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.116', 'C16', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.117', 'C17', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.118', 'C18', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.119', 'C19', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.120', 'C20', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.121', 'C21', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.122', 'C22', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.123', 'C23', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.124', 'C24', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.125', 'C25', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.126', 'C26', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.127', 'C27', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.128', 'C28', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.129', 'C29', 'unspecified');
INSERT INTO tor.client (IP, Name, Material) VALUES ('192.168.0.130', 'C30', 'unspecified');

INSERT INTO tor.jobqueue (ClientId, JobId, JobParameters, ExecuteAt) VALUES ((SELECT Id FROM tor.client WHERE Name = 'C3'), (SELECT Id FROM tor.job WHERE Code = 'R'), 1, NULL);

SELECT * FROM tor.jobqueue;
SELECT * FROM tor.diceresult;
SELECT * FROM tor.job;
SELECT * FROM tor.client;