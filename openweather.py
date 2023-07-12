import datetime
import json

import requests
from decouple import config

# Cardinal directions and their corresponding degrees
CARDINAL_DIRECTIONS = [
    {'name': 'north', 'abbr': 'N', 'min': 348.75, 'max': 360},
    {'name': 'north', 'abbr': 'N', 'min': 0, 'max': 11.25},
    {'name': 'north-northeast', 'abbr': 'NNE', 'min': 11.25, 'max': 33.75},
    {'name': 'northeast', 'abbr': 'NE', 'min': 33.75, 'max': 56.25},
    {'name': 'east-northeast', 'abbr': 'ENE', 'min': 56.25, 'max': 78.75},
    {'name': 'east', 'abbr': 'E', 'min': 78.75, 'max': 101.25},
    {'name': 'east-southeast', 'abbr': 'ESE', 'min': 101.25, 'max': 123.75},
    {'name': 'southeast', 'abbr': 'SE', 'min': 123.75, 'max': 146.25},
    {'name': 'south-southeast', 'abbr': 'SSE', 'min': 146.25, 'max': 168.75},
    {'name': 'south', 'abbr': 'S', 'min': 168.75, 'max': 191.25},
    {'name': 'south-southwest', 'abbr': 'SSW', 'min': 191.25, 'max': 213.75},
    {'name': 'southwest', 'abbr': 'SW', 'min': 213.75, 'max': 236.25},
    {'name': 'west-southwest', 'abbr': 'WSW', 'min': 236.25, 'max': 258.75},
    {'name': 'west', 'abbr': 'W', 'min': 258.75, 'max': 281.25},
    {'name': 'west-northwest', 'abbr': 'WNW', 'min': 281.25, 'max': 303.75},
    {'name': 'northwest', 'abbr': 'NW', 'min': 303.75, 'max': 326.25},
    {'name': 'north-northwest', 'abbr': 'NNW', 'min': 326.25, 'max': 348.75}
]

# Distance strings and their corresponding feet
DISTANCE_STRINGS = [
    {'desc': 'practically nothing', 'min': 0, 'max': 125},
    {'desc': '250 ft', 'min': 125, 'max': 375},
    {'desc': '500 ft', 'min': 375, 'max': 875},
    {'desc': '750 ft', 'min': 875, 'max': 1000},
    {'desc': '1/4 mile', 'min': 1000, 'max': 1980},
    {'desc': '1/2 mile', 'min': 1980, 'max': 3300},
    {'desc': '3/4 mile', 'min': 3300, 'max': 4620},
    {'desc': '1 mile', 'min': 4620, 'max': 6600},
    {'desc': '1.5 miles', 'min': 6600, 'max': 9900},
    {'desc': (lambda x : str(round(x / 5280)) + ' miles'), 'min': 9900, 'max': 999999}
]

# Moon phases and their corresponding values
MOON_PHASES = [
    {'name': 'new moon', 'min': 0, 'max': 0.0625},
    {'name': 'waxing crescent', 'min': 0.0625, 'max': 0.1875},
    {'name': 'first quarter', 'min': 0.1875, 'max': 0.3125},
    {'name': 'waxing gibbous', 'min': 0.3125, 'max': 0.4375},
    {'name': 'full moon', 'min': 0.4375, 'max': 0.5625},
    {'name': 'waning gibbous', 'min': 0.5625, 'max': 0.6875},
    {'name': 'last quarter', 'min': 0.6875, 'max': 0.8125},
    {'name': 'waning crescent', 'min': 0.8125, 'max': 0.9375},
    {'name': 'new moon', 'min': 0.9375, 'max': 1.0}   
]

# Function to convert degrees to cardinal directions
def degrees_to_cardinal(degrees, long=False):
    for direction in CARDINAL_DIRECTIONS:
        if direction['min'] <= degrees < direction['max']:
            if long == True:
                return direction['name']
            return direction['abbr']
    return 'nowhere'

# Function to convert visibility in feet to a string
def visibility_to_string(feet):
    for distance in DISTANCE_STRINGS:
        if distance['min'] <= feet < distance['max']:
            if callable(distance['desc']):
                return distance['desc'](feet)
            else:
                return distance['desc']
    return 'unclear at this time'

# Function to convert moon phase value to a string
def moon_phase_string(moon_phase):
    for phase in MOON_PHASES:
        if phase['min'] <= moon_phase < phase['max']:
            return phase['name']
    return 'a mystery'
    
# Function to convert unix time to a nice string format
def nice_time(unix_time):
    return datetime.datetime.fromtimestamp(unix_time).strftime('%_I:%M %p')
    
def get_weather_data(lat, lon, units, api_key):
    request_url = 'https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&units={}&appid={}'.format(lat, lon, units, api_key)
    response = requests.get(request_url)
    return response.json()

def write_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def get_current_weather(response):
    dt             = response['current']['dt']
    wind_speed     = round(response['current']['wind_speed'])
    wind_direction = degrees_to_cardinal(response['current']['wind_deg'], long=False)
    weather_desc   = response['current']['weather'][0]['description']
    visibility     = visibility_to_string(response['current']['visibility'])
    cloud_cover    = response['current']['clouds']
    uv_index       = response['current']['uvi']
    temp           = round(response['current']['temp'])
    feels_like     = round(response['current']['feels_like'])
    humidity       = response['current']['humidity']
    dew_point      = round(response['current']['dew_point'])
    sunrise        = nice_time(response['current']['sunrise'])
    sunset         = nice_time(response['current']['sunset'])

    return {
        'dt': dt,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'weather_desc': weather_desc,
        'visibility': visibility,
        'cloud_cover': cloud_cover,
        'uv_index': uv_index,
        'temp': temp,
        'feels_like': feels_like,
        'humidity': humidity,
        'dew_point': dew_point,
        'sunrise': sunrise,
        'sunset': sunset
    }

def print_current_weather(current_weather):
    print("\n\n" + datetime.datetime.fromtimestamp(current_weather['dt']).strftime('%A %B %-d at %-I:%M %p') + '\n')
    print("Currently:   " + current_weather['weather_desc'] + " with " + str(current_weather['cloud_cover']) + "% cloud cover and " + current_weather['visibility'] + " visibility")
    print("Temperature: " + str(current_weather['temp']), "°F")
    print("Feels like:  " + str(current_weather['feels_like']), "°F")
    print("Humidity:    " + str(current_weather['humidity']) + "%")
    print("Dew point:   " + str(current_weather['dew_point']) + "°F")
    print("Wind:        " + current_weather['wind_direction'] + " @ " + str(current_weather['wind_speed']) + " MPH")
    print("UV index:    " + str(current_weather['uv_index']))
    print("Sunrise:     " + str(current_weather['sunrise']).strip())
    print("Sunset:      " + str(current_weather['sunset']).strip())

def get_hourly_forecast(response):
    hourly_forecast = []
    for hour in response['hourly']:
        weekday   = datetime.datetime.fromtimestamp(hour['dt']).strftime('%a')
        hr      = datetime.datetime.fromtimestamp(hour['dt']).strftime('%_I %p').lower()
        temp      = str(round(hour['temp'])) + "°F"
        humidity  = str(round(hour['humidity'])) + "% "
        dew_point = str(round(hour['dew_point'])) + "°F"
        wind      = str(round(hour['wind_speed'])) + " MPH" + "\t" + degrees_to_cardinal(hour['wind_deg'], long=False)
        pop       = str(round(hour['pop'])) + "%"
        weather   = hour['weather'][0]['description']
        hourly_forecast.append({
            'weekday': weekday,
            'hr': hr,
            'temp': temp,
            'humidity': humidity,
            'dew_point': dew_point,
            'wind': wind,
            'pop': pop,
            'weather': weather
        })
    return hourly_forecast

def print_hourly_forecast(hourly_forecast):
    print("\nFORECAST")
    print("\n            TEMP\tRH    DEW\tWIND\tDIR\tPOP\tWEATHER")
    for hour in hourly_forecast:
        print(hour['weekday'] + '  ' + hour['hr'] + '  ' + hour['temp'] + '\t' + hour['humidity'] + '  ' + hour['dew_point'] + '\t' + hour['wind'] + '\t' + hour['pop'] + '\t' + hour['weather'])

def get_daily_forecast(response):
    daily_forecast = []
    i = 0
    for day in response['daily']:
        if i == 0:
            weekday = "TODAY"
        else:
            weekday = datetime.datetime.fromtimestamp(day['dt']).strftime('%A').upper()
        i += 1

        summary   = day['summary']
        high      = str(round(day['temp']['max']))
        low       = str(round(day['temp']['min']))
        rh        = str(round(day['humidity']))
        dew_point = str(round(day['dew_point']))
        pop       = str(round(day['pop']))

        sunrise    = nice_time(day['sunrise'])
        sunset     = nice_time(day['sunset'])
        moonrise   = nice_time(day['moonrise'])
        moonset    = nice_time(day['moonset'])
        moon_phase = moon_phase_string(day['moon_phase'])

        daily_forecast.append({
            'weekday': weekday,
            'summary': summary,
            'high': high,
            'low': low,
            'rh': rh,
            'dew_point': dew_point,
            'pop': pop,
            'sunrise': sunrise,
            'sunset': sunset,
            'moonrise': moonrise,
            'moonset': moonset,
            'moon_phase': moon_phase
        })
    return daily_forecast

def print_daily_forecast(daily_forecast):
    for day in daily_forecast:
        print("\n" + day['weekday'])
        print(day['summary'])
        print("High " + day['high'] + "°F Low " + day['low'] + "°F RH " + day['rh'] + "% Dew Point " + day['dew_point'] + "°F POP " + day['pop'], "%")
        print("Sun: " + day['sunrise'] + " " + day['sunset'] + " Moon: " + day['moonrise'] + " " + day['moonset'] + " " + day['moon_phase'])

def main():
    API_KEY = config('OPENWEATHER_API_KEY')
    LATITUDE = config('LATITUDE', cast=float)
    LONGITUDE = config('LONGITUDE', cast=float)
    UNITS = 'imperial'
    
    response = get_weather_data(LATITUDE, LONGITUDE, UNITS, API_KEY)
    #write_to_file(response, 'weather.json')

    current_weather = get_current_weather(response)
    print_current_weather(current_weather)

    hourly_forecast = get_hourly_forecast(response)
    print_hourly_forecast(hourly_forecast)

    daily_forecast = get_daily_forecast(response)
    print_daily_forecast(daily_forecast)

if __name__ == '__main__':
    main()

