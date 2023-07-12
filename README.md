# homelog

Logs data related to the house.

## Currently:
1. nest.py gets interior temp and humidity (and settings) from Nest thermostat
2. log_temperature.py repeatedly calls nest and logs to sqlite db
3. openweather.py calls OpenWeather API to get outside weather (not yet wired in)

## TODO:
1. Wire up openweather and logger. Probably rename logger too.
2. Write something to poll Amazon Echo devices for temperature, or build/poll some Raspberry Pi Pico W's to do it since polling Alexa is a pain in the ass...
3. Poll A/C window units and fans via smart plugs; implement autocool mode to manage fans and A/C based on user-selected temp/humidity preferences and window status.
4. Consider putting sensors on all of the windows to more fully automate autocool.
