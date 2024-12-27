use tor;

ALTER TABLE client ADD IsAvailable tinyint NOT NULL DEFAULT 0;
