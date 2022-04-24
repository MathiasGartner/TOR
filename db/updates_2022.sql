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
