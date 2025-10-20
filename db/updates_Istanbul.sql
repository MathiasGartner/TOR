use tor;

UPDATE client SET Latin = "Cetraria islandica" WHERE Id = 17;

ALTER TABLE client ADD UseSchedule tinyint NOT NULL DEFAULT 0;

CREATE TABLE schedule (
    Id INT NOT NULL AUTO_INCREMENT,
    StartTime DATETIME NULL,
    EndTime DATETIME NULL,
    PRIMARY KEY (Id)
);

CREATE TABLE interactivevisits (
    Id INT NOT NULL AUTO_INCREMENT,
    Ip VARCHAR(45) NOT NULL,
    Browser VARCHAR(100) DEFAULT NULL,
    OS VARCHAR(100) DEFAULT NULL,
    Device VARCHAR(100) DEFAULT NULL,
    UserAgent TEXT DEFAULT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Id)
);

CREATE TABLE interactivelog (
    Id INT NOT NULL AUTO_INCREMENT,
    VisitorId INT NOT NULL,
    Path VARCHAR(255) NOT NULL,
    Method VARCHAR(10) NOT NULL DEFAULT 'GET',
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Referrer VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (Id),
    FOREIGN KEY (VisitorId) REFERENCES interactivevisits(Id)
        ON DELETE CASCADE
);

INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-21 11:05:00', '2025-10-21 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-22 11:05:00', '2025-10-22 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-23 11:05:00', '2025-10-23 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-24 11:05:00', '2025-10-24 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-25 11:05:00', '2025-10-25 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-26 11:05:00', '2025-10-26 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-27 11:05:00', '2025-10-27 20:50:00');
INSERT INTO schedule (StartTime, EndTime) VALUES ('2025-10-28 11:05:00', '2025-10-28 20:50:00');

INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Zorlu - pause', 'W', '' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Zorlu - default', 'RW', '6 60 3' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Zorlu - slow', 'RW', '4 120 3' FROM client WHERE Position <= 27;
INSERT INTO jobprogram (ClientId, Name, JobCode, JobParameters) SELECT Id, 'Zorlu - wait', 'W', '' FROM client WHERE Position <= 27;