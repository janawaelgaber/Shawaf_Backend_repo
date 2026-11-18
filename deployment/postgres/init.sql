-- Local bootstrap only. shawaf_local is the image superuser and is not an application user.
-- shawaf_app writes schema app. shawaf_ai writes schema analytics. Neither writes the other schema.

CREATE USER shawaf_app WITH PASSWORD 'shawaf_app';
CREATE USER shawaf_ai WITH PASSWORD 'shawaf_ai';

CREATE SCHEMA app AUTHORIZATION shawaf_app;
CREATE SCHEMA analytics AUTHORIZATION shawaf_ai;

REVOKE ALL ON SCHEMA app FROM PUBLIC;
REVOKE ALL ON SCHEMA analytics FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA app TO shawaf_app;
GRANT USAGE, CREATE ON SCHEMA analytics TO shawaf_ai;

ALTER ROLE shawaf_app SET search_path = app;
ALTER ROLE shawaf_ai SET search_path = analytics;
