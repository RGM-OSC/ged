CREATE DATABASE IF NOT EXISTS ged;
CREATE DATABASE IF NOT EXISTS lilac;

FLUSH PRIVILEGES;
CREATE USER 'gedadmin'@'localhost';
SET PASSWORD FOR 'gedadmin'@'localhost' = PASSWORD('0rd0-c0m1735-b47h0n143');
GRANT ALL ON `ged`.* TO 'gedadmin'@'localhost';
GRANT SELECT ON `lilac`.* TO 'gedadmin'@'localhost';
