"""
Record temperature and humidity data using DHT22 connected to a Raspberry Pi.
"""

import Adafruit_DHT
import argparse
import datetime
import os
import psycopg2
import time

from dotenv import load_dotenv

sensor_type = Adafruit_DHT.DHT22
sensor_gpio = 4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Path to .env file.")
    parser.add_argument(
        "--path_env",
        "-p",
        help="Absolute path to .env file",
        type=str,
        required=False,
        default="/home/pi/dhtlog/.env",
        )
    args = parser.parse_args()
    
    load_dotenv(args.path_env) # Load environmental variables

    conn = psycopg2.connect(
        host=os.getenv["HOST"],
        port=os.getenv["PORT"],
        database=os.getenv["DATABASE"],
        user=os.getenv["USER"],
        password=os.getenv["PASSWORD"],
        )
    cur = conn.cursor()

    query = f"INSERT INTO {os.getenv["TABLE"]} (datetime, temperature, humidity) VALUES (%s, %s, %s)"

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, sensor_gpio)
        dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(query, (dt_string, temperature, humidity))
        conn.commit()
    
    cur.close()
    conn.close()