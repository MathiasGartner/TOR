use tor;

ALTER TABLE client ADD IsAvailable tinyint NOT NULL DEFAULT 0;

ALTER TABLE clientlog ADD IsAcknowledged tinyint NOT NULL DEFAULT 0;