from homeassistant.helpers.entity import Entity
import logging
import math as m
from psypy import psySI as SI

logger = logging.getLogger(__name__)

CONF_OUTDOOR_TEMP = 'outdoor_temp'
CONF_OUTDOOR_HUM = 'outdoor_hum'
CONF_INDOOR_TEMP = 'indoor_temp'
CONF_INDOOR_HUM = 'indoor_hum'
CONF_PRESSURE = 'pressure'
CONF_NAME = 'name'
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([ExampleSensor(hass, config)])



class ExampleSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.hass = hass
        self.outdoorTemp = config.get(CONF_OUTDOOR_TEMP)
        self.outdoorHum = config.get(CONF_OUTDOOR_HUM)
        self.indoorTemp = config.get(CONF_INDOOR_TEMP)
        self.indoorHum = config.get(CONF_INDOOR_HUM)
        self.pressure = config.get(CONF_PRESSURE)
        self._name = config.get(CONF_NAME)
        self._state = None


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name 

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'
    def toKelvin(self, celsius):
        return celsius + 273.15
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            logger.debug("Temp outdoor (raw sensor value): " + str(self.hass.states.get(self.outdoorTemp).state))
            logger.debug("Temp indoor (raw sensor value):  " + str(self.hass.states.get(self.indoorTemp).state))
            logger.debug("hum outdoor (raw sensor value):  " + str(self.hass.states.get(self.outdoorHum).state))
            logger.debug("hum indoor (raw sensor value):   " + str(self.hass.states.get(self.indoorHum).state))
            logger.debug("pressure (raw sensor value):     " + str(self.hass.states.get(self.pressure).state))
            temp_out = self.toKelvin(float(self.hass.states.get(self.outdoorTemp).state))
            temp_in = self.toKelvin(float(self.hass.states.get(self.indoorTemp).state))
            hum_out = self.toKelvin(float(self.hass.states.get(self.outdoorHum).state))
            hum_in = self.toKelvin(float(self.hass.states.get(self.indoorHum).state))
            pressure = float(self.hass.states.get(self.pressure).state)*100

            logger.debug("Temp outdoor:      " + str(temp_out))
            logger.debug("Temp indoor :      " + str(temp_in))
            logger.debug("Hum outdoor:       " + str(hum_out))
            logger.debug("Pressure (pascal): " + str(pressure))


            S=SI.state("DBT",temp_out,"RH",hum_out/100,pressure)
    # self._attributes = {
    #     "specific enthalpy": S[1],
    #     "specific volume": S[3],
    #     "humidity ratio": S[4])
    # }
            logger.debug("The dry bulb temperature is "+ str(S[0]))
            logger.debug("The specific enthalpy is "+ str(S[1]))
            logger.debug("The relative humidity is "+ str(S[2]))
            logger.debug("The specific volume is "+ str(S[3]))
            logger.debug("The humidity ratio is "+ str(S[4]))
            logger.debug("The wet bulb temperature is "+ str(S[5]))
            t_in = temp_out
            
            t_wb = S[5] 
            t_out = temp_in
            logger.debug("Calculation ------  " )
            logger.debug("The dry bulb temperature (t_in): "+ str(temp_out))
            logger.debug("The dry bulb temperature (t_out): "+ str(temp_in))
            logger.debug("The wet bulb temperature is (t_wb)"+ str(t_wb))
            logger.debug(" (t_in - t_out)/(t_in - t_wb)")
# ()
            # Formula: https://en.wikipedia.org/wiki/Evaporative_cooler
            cooling_efficiency = (t_in - t_out)/(t_in - t_wb)
            logger.debug("The efficiency is           " + str(cooling_efficiency*100))
            self._state = abs(cooling_efficiency*100)
        except ValueError as e:
            logger.warning("Some input sensor values are still unavailable")

        except AttributeError:
            logger.error("Some entity does not exist or is spelled incorrectly. Did its component initialise correctly?")
    

