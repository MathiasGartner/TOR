use tor;

ALTER TABLE client ADD IsActive tinyint NOT NULL DEFAULT 0;

DROP TABLE clientlog;

CREATE TABLE clientlog (
    Id INT NOT NULL AUTO_INCREMENT,
    ClientId INT NOT NULL,
    MessageType VARCHAR(30) NOT NULL,
    MessageCode VARCHAR(30) NOT NULL,
    Message TEXT NOT NULL,
    Time DATETIME NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (Id),
    KEY fk_clientlog_clientId_idx (ClientId),
    CONSTRAINT fk_clientlog_clientId_idx FOREIGN KEY (ClientId) REFERENCES client (Id)
);

CREATE TABLE jobprogram (
    ClientId INT NOT NULL,
    Name VARCHAR(300) NOT NULL,
    JobCode VARCHAR(45) NOT NULL,
    JobParameters VARCHAR(45),
    PRIMARY KEY (ClientId, Name),
    KEY fk_jobprograms_clientId_idx (ClientId),
    CONSTRAINT fk_jobprograms_clientId_idx FOREIGN KEY (ClientId) REFERENCES client (Id)
);

INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Run all', 'R', '' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Wait all', 'W', '' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Run & Wait - short pause', 'RW', '4 30 6' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Run & Wait - medium pause', 'RW', '4 60 6' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Run & Wait - long pause', 'RW', '4 120 6' FROM client WHERE Position <= 27;
