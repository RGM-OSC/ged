CREATE DATABASE IF NOT EXISTS ged;
CREATE DATABASE IF NOT EXISTS lilac;

GRANT ALL ON `ged`.* TO 'gedadmin'@'localhost' IDENTIFIED BY '0rd0-c0m1735-b47h0n143';
GRANT SELECT ON `lilac`.* TO 'gedadmin'@'localhost' IDENTIFIED BY '0rd0-c0m1735-b47h0n143';

-- better implementation, but `CREATE USER IF EXISTS` work only with mariadb 5.7.6
-- CREATE USER 'gedadmin'@'localhost';
-- SET PASSWORD FOR 'gedadmin'@'localhost' = PASSWORD('0rd0-c0m1735-b47h0n143');
-- GRANT ALL ON `ged`.* TO 'gedadmin'@'localhost';
-- GRANT SELECT ON `lilac`.* TO 'gedadmin'@'localhost';
