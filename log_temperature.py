import time
import sqlite3
import nest

CONFIG_FILE = 'nest_api_config.json'
DB_FILE = 'homelog.db'

def create_table(conn):
    """Create a table to store device stats"""
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS device_stats
                 (timestamp INTEGER, temperature REAL, relative_humidity REAL, dew_point REAL, device_id TEXT, connectivity TEXT, hvac TEXT, mode TEXT, eco_mode TEXT, eco_heat REAL, eco_cool REAL, set_point REAL)''')
    conn.commit()

def insert_stats(conn, device_stats):
    """Insert device stats into the database"""
    c = conn.cursor()
    c.execute("INSERT INTO device_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", device_stats)
    conn.commit()

def get_and_parse_stats(api, conn):
    """Retrieve and parse device stats"""
    devices = api.get_devices()
    for device in devices:
        device_stats = nest.get_device_stats(device, api)
        timestamp = int(time.time())
        print('\n', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)))
        nest.print_device_stats(device_stats)
        temperature_c = device_stats['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
        temperature = nest.c_to_f(device_stats['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius'])
        relative_humidity = device_stats['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent']
        if relative_humidity >= 50:
            dew_point = nest.c_to_f(temperature_c - ((100 - relative_humidity) / 5))
        else:
            dew_point = None
        device_id = device['name'].split('/')[-1]
        connectivity = device_stats['traits']['sdm.devices.traits.Connectivity']['status']
        hvac = device_stats['traits']['sdm.devices.traits.ThermostatHvac']['status']
        mode = device_stats['traits']['sdm.devices.traits.ThermostatMode']['mode']
        eco_mode = device_stats['traits']['sdm.devices.traits.ThermostatEco']['mode']
        eco_heat = nest.c_to_f(device_stats['traits']['sdm.devices.traits.ThermostatEco']['heatCelsius'])
        eco_cool = nest.c_to_f(device_stats['traits']['sdm.devices.traits.ThermostatEco']['coolCelsius'])
        try:
            set_point = nest.c_to_f(device_stats['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']['heatCelsius'])
        except KeyError:
            set_point = None
        insert_stats(conn, (timestamp, temperature, relative_humidity, dew_point, device_id, connectivity, hvac, mode, eco_mode, eco_heat, eco_cool, set_point))

if __name__ == '__main__':
    # Set up a connection to the SQLite database
    conn = sqlite3.connect(DB_FILE)

    # Create a table in the database to store the device stats
    create_table(conn)

    # Set up authentication with the Nest API
    api = nest.Nest_Api(CONFIG_FILE)

    # Define a loop that calls the function every 5 minutes and inserts the results into the database
    while True:
        get_and_parse_stats(api, conn)
        time.sleep(300)  # Wait 5 minutes before calling the function again