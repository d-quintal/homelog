"""
https://www.wouternieuwerth.nl/controlling-a-google-nest-thermostat-with-python/
https://console.nest.google.com/device-access/project-list

"""

import datetime
import json
import os
import requests

CONFIG_FILE = 'nest_api_config.json'

def c_to_f(temperature):
    """Convert Celsius to Fahrenheit"""
    return round((temperature * 9/5) + 32)

class Nest_Api():
    def __init__(self, config_file) -> None:
        self.config_file = config_file
        if os.path.exists(config_file):
            self.load_config()
        else:
            self.new_config()
        
    def load_config(self):
        """Load config from JSON file."""
        with open(self.config_file) as json_file:
            self.config = json.load(json_file)
        self.project_id = self.config['project_id']
        self.client_id = self.config['client_id']
        self.client_secret = self.config['client_secret']
        self.redirect_uri = self.config['redirect_uri']
        self.authorization_code = self.config['authorization_code']
        self.refresh_token = self.config['refresh_token']
        self.access_token = self.config['access_token']
        self.access_token_expiration = datetime.datetime.fromisoformat(self.config['access_token_expiration'])
        # If access token has expired, refresh it
        if datetime.datetime.now() > self.access_token_expiration:
            self.refresh_access_token()
            
    def save_config(self):
        """Save config to JSON file."""
        self.config = {
            "project_id": self.project_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "authorization_code": self.authorization_code,
            "refresh_token": self.refresh_token,
            "access_token": self.access_token,
            "access_token_expiration": datetime.datetime.isoformat(self.access_token_expiration)
        }
        with open(self.config_file, 'w') as outfile:
            json.dump(self.config, outfile)
            
    def new_config(self):
        """Generate a URL for the user to login and authorize access to their Nest account."""
        
        instructions = """
        If you have not already, follow these instructions to create a Google Cloud project, an OAuth 2.0 client ID,
            and a device access project:
        
            https://developers.google.com/nest/device-access/get-started
            
        Once you have completed the above steps, enter the following information:
        """
        print(instructions)
        print("From the Google Cloud project:")
        self.client_id = input("    OAuth 2.0 Client ID: ")
        self.client_secret = input("    OAuth 2.0 Client Secret: ")
        self.redirect_uri = input("    OAuth 2.0 Redirect URI [https://www.google.com]: ")
        if self.redirect_uri == "":
            self.redirect_uri = "https://www.google.com"
        print("From the Device Access project:")
        self.project_id = input("    Project ID: ")
        
        # Prompt user to login and authorize access to their Nest account
        login_url = 'https://nestservices.google.com/partnerconnections/'+self.project_id+'/auth?redirect_uri='+self.redirect_uri+'&access_type=offline&prompt=consent&client_id='+self.client_id+'&response_type=code&scope=https://www.googleapis.com/auth/sdm.service'
        try:
            print("Press any key to open the URL in your browser. Once you have completed the login process, the Google\
                homepage will appear with a long URL. Copy the URL and paste it below.")
            os.system('start ' + login_url)
        except:
            print("Please navigate here in your browser to log in:")
            print(login_url)
            print("Once you have completed the login process, the Google homepage will appear with a long URL. Copy the URL and paste it below.")
        url_raw = input("Authorization URL: ")
        
        self.authorization_code = url_raw.split('code=')[1].split("&")[0]
        self.save_config()

    def auth_headers(self):
        """Return headers for API calls."""
        return {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
        }
    
    def get_tokens(self):
        """Poll API for access and refresh tokens."""
        params = (
            ('client_id', self.client_id),
            ('client_secret', self.client_secret),
            ('code', self.authorization_code),
            ('grant_type', 'authorization_code'),
            ('redirect_uri', self.redirect_uri),
        )

        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)

        response_json = response.json()
        self.access_token = response_json['token_type'] + ' ' + str(response_json['access_token'])
        self.refresh_token = response_json['refresh_token']
        self.access_token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=response_json['expires_in'])
        self.save_config()

    def refresh_access_token(self):
        """Use a valid refresh token to poll API for a new access token."""
        params = (
            ('client_id', self.client_id),
            ('client_secret', self.client_secret),
            ('refresh_token', self.refresh_token),
            ('grant_type', 'refresh_token'),
        )

        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)

        response_json = response.json()
        self.access_token = response_json['token_type'] + ' ' + response_json['access_token']
        self.access_token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=response_json['expires_in'])
        self.save_config()
            
    def get_structures(self):
        """Poll API for structure data (home, etc.)"""
        url_structures = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + self.project_id + '/structures'
        response = requests.get(url_structures, headers=self.auth_headers())
        return response.json()
    
    def get_devices(self):
        url_get_devices = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + self.project_id + '/devices'
        response = requests.get(url_get_devices, headers=self.auth_headers())
        devices = []
        try:
            for device in response.json()['devices']:
                devices.append(device)
        except KeyError:
            #print("Error: No devices found.")
            self.refresh_access_token()
            self.get_devices()
        return devices

def get_device_stats(device, api):
    """Poll API for device stats (temperature, humidity, etc.)"""
    url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device['name']
    response = requests.get(url_get_device, headers=api.auth_headers())    
    device_stats = response.json()
    return device_stats

def print_device_stats(device_stats):
    temperature = device_stats['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
    relative_humidity = device_stats['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent']
    print('\nTemperature:\t', c_to_f(temperature), "°F")
    print('\nHumidity:\t', relative_humidity, "%")
    if relative_humidity >= 50:
        dew_point = temperature - ((100 - relative_humidity) / 5)
        print('Dew Point:\t', c_to_f(dew_point), "°F")
    else:
        dew_point = None
    print('\nConnectivity:\t', device_stats['traits']['sdm.devices.traits.Connectivity']['status'])
    print('HVAC:\t\t', device_stats['traits']['sdm.devices.traits.ThermostatHvac']['status'])
    print('Mode:\t\t', device_stats['traits']['sdm.devices.traits.ThermostatMode']['mode'])
    print('\nEco Mode:\t', device_stats['traits']['sdm.devices.traits.ThermostatEco']['mode'])
    print('Eco Min:\t', c_to_f(device_stats['traits']['sdm.devices.traits.ThermostatEco']['heatCelsius']), "°F")
    print('Eco Max:\t', c_to_f(device_stats['traits']['sdm.devices.traits.ThermostatEco']['coolCelsius']), "°F")
    try:
        print('Set Point:', c_to_f(device_stats['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint']['heatCelsius']), "°F")
    except KeyError:
        pass
    print('\n')
    

if __name__ == '__main__':
    api = Nest_Api(CONFIG_FILE)
    devices = api.get_devices()
    device_stats = []
    for device in devices:
        print('\nTimestamp:\t', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        device_stats.append(get_device_stats(device, api))
        print_device_stats(device_stats[-1])
    