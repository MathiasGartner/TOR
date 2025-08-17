use tor;

ALTER TABLE client ADD UseSchedule tinyint NOT NULL DEFAULT 0;

CREATE TABLE schedule (
    Id INT NOT NULL AUTO_INCREMENT,
    StartTime DATETIME NULL,
    EndTime DATETIME NULL,
    PRIMARY KEY (Id)
);

INSERT INTO schedule