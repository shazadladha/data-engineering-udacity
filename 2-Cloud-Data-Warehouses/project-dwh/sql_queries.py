import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE staging_events
(
    artist VARCHAR(256),
    auth VARCHAR(16),
    firstName VARCHAR(256),
    gender VARCHAR(256),
    itemInSession INTEGER,
    lastName VARCHAR(256),
    length NUMERIC(10,5),
    level VARCHAR(8),
    location VARCHAR(256),
    method VARCHAR(6),
    page VARCHAR(20),
    registration BIGINT,
    sessionId INTEGER,
    song VARCHAR(256),
    status INTEGER,
    ts TIMESTAMP,
    userAgent VARCHAR(256),
    userId INTEGER
    
    
);
""")

staging_songs_table_create = ("""
CREATE TABLE staging_songs
(
    num_songs INTEGER,
    artist_id VARCHAR(20),
    artist_latitude FLOAT,
    artist_longitude FLOAT,
    artist_location VARCHAR(256),
    artist_name VARCHAR(256),
    song_id VARCHAR(20),
    title VARCHAR(256),
    duration FLOAT,
    year INTEGER
);
""")

songplay_table_create = ("""
CREATE TABLE songplays 
(
    songplay_id INTEGER IDENTITY(0,1) PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL,
    level VARCHAR(8),
    song_id VARCHAR(20) NOT NULL,
    artist_id VARCHAR(20) NOT NULL,
    session_id INTEGER NOT NULL,
    location VARCHAR(256) NOT NULL,
    user_agent VARCHAR(256) NOT NULL
)
DISTSTYLE AUTO
SORTKEY (start_time);
""")

user_table_create = ("""
CREATE TABLE users
(
    user_id INTEGER NOT NULL PRIMARY KEY,
    first_name VARCHAR(256) NOT NULL,
    last_name VARCHAR(256) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    level VARCHAR(8) NOT NULL
)
DISTSTYLE AUTO
SORTKEY (user_id);
""")

song_table_create = ("""
CREATE TABLE songs
(
    song_id VARCHAR(20) NOT NULL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    artist_id VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    duration FLOAT
)
DISTSTYLE AUTO
SORTKEY (song_id);
""")

artist_table_create = ("""
CREATE TABLE artists
(
    artist_id VARCHAR(20) NOT NULL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    location VARCHAR(256),
    latitude FLOAT,
    longitude FLOAT
)
DISTSTYLE AUTO
SORTKEY (artist_id);
""")

time_table_create = ("""
CREATE TABLE time
(
    start_time TIMESTAMP NOT NULL PRIMARY KEY, 
    hour INTEGER NOT NULL, 
    day INTEGER NOT NULL, 
    week INTEGER NOT NULL, 
    month INTEGER NOT NULL, 
    year INTEGER NOT NULL, 
    weekday VARCHAR(9) ENCODE BYTEDICT NOT NULL
)
DISTSTYLE AUTO
DISTKEY ( start_time )
SORTKEY ( start_time );
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events
FROM {}
CREDENTIALS 'aws_iam_role={}' 
FORMAT AS JSON {} REGION 'us-west-2';
""").format(config['S3']['log_data'], config['IAM_ROLE']['arn'], config['S3']['log_jsonpath'])

staging_songs_copy = ("""
COPY staging_songs
FROM {}
CREDENTIALS 'aws_iam_role={}' 
FORMAT AS JSON 'auto' REGION 'us-west-2';
""").format(config['S3']['song_data'], config['IAM_ROLE']['arn'])

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT
    TIMESTAMP 'epoch' + (se.ts / 1000) * INTERVAL '1 second',
    se.userId as user_id,
    se.level,
    ss.song_id,
    ss.artist_id,
    se.sessionId as session_id,
    se.location,
    se.userAgent as user_agent
FROM staging_events se
INNER JOIN staging_songs ss ON ss.title = se.song 
AND se.artist = ss.artist_name
WHERE se.page = 'NextSong';
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT
    userId as user_id,
    firstName as first_name,
    lastName as last_name,
    gender,
    level
FROM staging_events
WHERE userId IS NOT NULL
AND page = 'NextSong';
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT 
    song_id,
    title,
    artist_id,
    year,
    duration
FROM staging_songs
WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT
    artist_id, 
    artist_name as name, 
    artist_location as location, 
    artist_latitude as latitude, 
    artist_longitude as longitude
FROM staging_songs
WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT
    TIMESTAMP 'epoch' + (ts/1000) * INTERVAL '1 second' as start_time,
    EXTRACT(HOUR FROM start_time) AS hour,
    EXTRACT(DAY FROM start_time) AS day,
    EXTRACT(WEEKS FROM start_time) AS week,
    EXTRACT(MONTH FROM start_time) AS month,
    EXTRACT(YEAR FROM start_time) AS year,
    CASE WHEN EXTRACT(ISODOW FROM start_time) IN (6, 7) THEN false ELSE true END AS weekday
FROM staging_events;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
