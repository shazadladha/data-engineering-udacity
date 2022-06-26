import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark

def process_song_data(spark, input_data, output_data):
    """
    Loads song_data from S3, extracts the songs and artist tables and loads the tables back to S3.
    """
    
    # get filepath to song data file
    song_data = input_data + 'song_data/*/*/*/*.json'
    
    # read song data file
    df = spark.read.json(song_data).cache()
    
    # extract columns to create songs table
    songs_table = df['song_id', 'title', 'artist_id', 'year', 'duration']
    songs_table = songs_table.dropDuplicates(['song_id'])
    
    print("Writing songs table to parquet files partitioned by year and artist...")
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy('year', 'artist_id').parquet(output_data + "songs/songs.parquet", 'overwrite')
    print("Done.")    
    
    # extract columns to create artists table
    artists_table = df['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    artists_table = artists_table.dropDuplicates(['artist_id'])
    
    print("Writing songs table to parquet files...")
    artists_table.write.parquet(output_data + "artists/artists.parquet", 'overwrite')
    print("Done.")


def process_log_data(spark, input_data, output_data):
    """
    Loads log_data from S3, extracts the users, time and songplays tables and loads the tables back to S3.           
    """

    # get filepath to log data file
    log_data = input_data + 'log_data/*/*/*.json'

    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong').cache()

    # extract columns for users table    
    users_table = df['userId', 'firstName', 'lastName', 'gender', 'level']
    users_table = users_table.dropDuplicates(['userId'])
    
    # write users table to parquet files
    print("Writing users table to parquet files...")
    users_table.write.parquet(output_data + "users/users.parquet", 'overwrite')
    print("Done.")
    
    # create timestamp column from original timestamp column
    get_timestamp = udf(
        lambda x: str(int(int(x) / 1000.0))
    )
    df = df.withColumn('timestamp', get_timestamp(df.ts))
    
    # create datetime column from original timestamp column
    get_datetime = udf(
        lambda x: str(datetime.fromtimestamp(int(x) / 1000.0))
    )
    df = df.withColumn("datetime", get_datetime(df.ts))
    
    # extract columns to create time table
    time_table = df.select(
        col('datetime').alias('start_time'),
        hour('datetime').alias('hour'),
        dayofmonth('datetime').alias('day'),
        weekofyear('datetime').alias('week'),
        month('datetime').alias('month'),
        year('datetime').alias('year')
        )
    time_table = time_table.dropDuplicates(['start_time'])
    
    # write time table to parquet files partitioned by year and month
    print("Writing time table to parquet files partitioned by year and month...")
    time_table.write.partitionBy('year', 'month').parquet(output_data + "time/time_table.parquet", 'overwrite')
    print("Done.")

    # read in song data to use for songplays table
    song_data = input_data + 'song_data/*/*/*/*.json'
    df_song = spark.read.json(song_data)

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = df.join(df_song, [df_song.title == df.song, df_song.artist_name == df.artist], 'inner')
    songplays_table = songplays_table.distinct()

    songplays_table = songplays_table.select(
        col('ts').alias('start_time'),
        col('userId').alias('user_id'),
        col('level').alias('level'),
        col('song_id').alias('song_id'),
        col('artist_id').alias('artist_id'),
        col('sessionId').alias('session_id'),
        col('location').alias('location'),
        col('userAgent').alias('user_agent'),
        year('datetime').alias('year'),
        month('datetime').alias('month')
    )
    
    songplays_table = songplays_table.withColumn('songplay_id', monotonically_increasing_id())

    # write songplays table to parquet files partitioned by year and month
    print("Writing songplays table to parquet files partitioned by year and month...")
    songplays_table.write.partitionBy('year', 'month') \
        .parquet(os.path.join(output_data, 'songplays/songplays.parquet'), 'overwrite')
    print("Done.")


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = ""
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
