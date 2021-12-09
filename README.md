# dhtlog
Simple script to record temperature and humidity data using Raspberry Pi and DHT22 sensor and upload data to a PostgreSQL server.

No config files provided at the moment, because it is currently set up for a 1-off pet project to monitor a greenhouse. Sensitive credentials for Postgres should be saved in a .env file (see further below for format and variables).

# What you need
* Raspberry Pi (tested with model 3 B+)
* Adafruit [DHT22](https://www.adafruit.com/product/385) or [AM2302](https://www.adafruit.com/product/393) temperature-humidity sensor (alternatively, DHT11 unit can be used if SENSOR_TYPE is changed in log.py) (tested with generic AM2302 unit from Amazon. Link not provided because I would not recommend.)
* Postgres server with an accessible table with the following fields (and data types), in order:
  * datetime (timestamp)
  * temperature (real)
  * humidity (real)

# Setup
## Connecting DHT22 to Raspberry Pi
* See [link](https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/) for hardware setup.
* Follow instructions and ensure **DHT22 data pin is connected to Raspberry Pi's GPIO4 pin**

## Code and environment
* Log into Raspberry pi and clone this repository into home directory
* Create a `.env` file in the cloned repository with the following fields and format:   
    ```
    # Configuration for dhtlog
    SQL_HOST=1.1.1.1 # Host IP address
    SQL_PORT=5432 # Default Postgres port is 5432
    SQL_USER=user
    SQL_PASSWORD=password
    SQL_DATABASE=database
    SQL_TABLE=table
    INTERVAL=60 # time interval between measurements in seconds
    ```
    Default path for this file is `/home/pi/dhtlog/.env`
* Set script to run on boot by doing the following:
  * Open crontab by running command `crontab -e` in terminal
  * At the bottom of the file, add line
    ```
    @reboot sleep 60 && python3 /home/pi/dhtlog/dhtlog/log.py
    ```
    If `dhtlog` repository and/or `.env` are not in default locations, edit the above line as follows:
    ```
    @reboot sleep 60 && python3 /path/to/dhtlog/log.py /path/to/.env
    ```
  * Save changes and exit
* Reboot Raspberry Pi. Data should be logged continuously to database upon reboot. 

# Postgres setup hints
I set up a postgres server on my home network using a spare computer. Here are helpful links and steps in case this is new to you.

## Links
* https://www.postgresqltutorial.com/
* https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart
* http://www.project-open.com/en/howto-postgresql-port-secure-remote-access

## Steps
* Install postgres
  ```
  sudo apt install postgresql postgresql-contrib
  ```
* Set up postgres environment
  ```
  sudo -u postgres createuser --interactive # Create new superuser tentlogger (or whatever you want to name it)
  sudo adduser tentlogger  # Must have matching linux user
  sudo -u postgres createdb tentlogger # Create database with same name as username
  sudo -u tentlogger psql  # Access database
  ```
* Create table for logging
  ```
  CREATE TABLE dht22 (
    datetime   timestamp,
    temperature real,
    humidity real
    );
  ```
* Open Postgres port for remote access
  * Locate path to conf file: 
    ```
    sudo -u postgres psql -c 'SHOW config_file'
    ```
  * Copy file path from output and open in text editor. Change `listening address` to `0.0.0.0`
  * Open `pg_hba.conf` (located in the same directory as `postgresql.conf`) in text editor and add the following line to the bottom of the file:
    ```
    host  all  all  0.0.0.0/0  md5
    ``` 
* Restart Postgres service
  ```
  systemctl restart postgresql.service
  ```
* Open firewall ports
    ```
    # Install firewalld package
    sudo apt install firewalld 

    # Open port
    sudo firewall-cmd --zone=public --add-port=5432/tcp --permanent

    # Reload
    sudo firewall-cmd --reload  
    ```
* [Optional] Status check
  * Check port
  ```
  # Install net tools
  sudo apt install net-tools

  # Confirm changes to address and port
  netstat -nlp | grep 5432
  (Not all processes could be identified, non-owned process info
   will not be shown, you would have to be root to see it all.)
  tcp        0      0 0.0.0.0:5432            0.0.0.0:*               LISTEN      -
  unix  2      [ ACC ]     STREAM     LISTENING     25322    -                    /var/run/postgresql/.s.PGSQL.5432
  ```
  * Check if port is open from **ANOTHER COMPUTER**
    ```
    telnet [ip.address.to.server] 5432
    ```
* Turn off sleep
  ```
  sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
  ```