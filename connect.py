import psycopg2
from psycopg2 import pool
import os

DATABASE_URL = os.environ['DATABASE_URL']

try:
    # conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    conn = psycopg2.pool.SimpleConnectionPool(DATABASE_URL, sslmode='require')


    norms_connection  = conn.getconn()
    reclows_connection = conn.getconn()
    rechighs_connection = conn.getconn()
    temps_connection = conn.getconn()

    # norms_connection  = postgreSQL_pool.getconn()
    # reclows_connection = postgreSQL_pool.getconn()
    # rechighs_connection = postgreSQL_pool.getconn()
    # temps_connection = postgreSQL_pool.getconn()

    if(norms_connection):
        print("successfully recived connection from connection pool ")
        norms_cursor = norms_connection.cursor()
        norms_cursor.execute("select * from dly_max_norm")
        norm_records = norms_cursor.fetchall()
        norms_cursor.close()

        rl_cursor = reclows_connection.cursor()
        rl_cursor.execute('SELECT min(ALL "TMIN") AS rec_low, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC')
        rec_lows = rl_cursor.fetchall()
        rl_cursor.close()  

        rh_cursor = rechighs_connection.cursor()
        rh_cursor.execute('SELECT max(ALL "TMAX") AS rec_high, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC')
        # rh_cursor.execute('SELECT max(ALL "TMAX") AS rec_high FROM temps GROUP BY day ORDER BY day ASC')
        rec_highs = rh_cursor.fetchall()
        rh_cursor.close()

        temps_cursor = temps_connection.cursor() 
        temps_cursor.execute('SELECT * FROM temps ORDER BY "DATE" ASC')
        all_temps = temps_cursor.fetchall()
        temps_cursor.close()

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while connecting to PostgreSQL", error)

finally:
    #closing database connection.
    # use closeall method to close all the active connection if you want to turn of the application
    if (conn):
        con.closeall
    print("PostgreSQL connection pool is closed")