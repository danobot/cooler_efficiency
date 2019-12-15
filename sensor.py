from homeassistant.helpers.entity import Entity
import logging
import math as m

logger = logging.getLogger(__name__)

CONF_OUTDOOR_TEMP = 'outdoor_temp'
CONF_WET_BULB = 'wet_bulb_temp'
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
        self.t_in = None
        self.t_out = None
        self.t_wb = None

        self.hass = hass
        self.outdoorTemp = config.get(CONF_OUTDOOR_TEMP)
        self.wetBulb = config.get(CONF_WET_BULB)
        self.indoorTemp = config.get(CONF_INDOOR_TEMP)
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
        return round(celsius, 2)# + 273.15

        
    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""

        attr = {}
        if self.t_in and self.t_out and self.t_wb:
                
            attr = {
                    "dry bulb temp in": self.t_in-273.15,
                    "dry bulb temp out": self.t_out-273.15,
                    "wet bulb temp": self.t_wb-273.15
            }
        if self._name:
            attr['name'] = self._name
            attr["wet bulb sensor"] = self.wetBulb
            attr["temp in sensor"] = self.outdoorTemp
            attr["temp out sensor"] =self.indoorTemp

        return attr

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            logger.debug("Temp outdoor (raw sensor value): " + str(self.hass.states.get(self.outdoorTemp).state))
            logger.debug("Temp indoor (raw sensor value):  " + str(self.hass.states.get(self.indoorTemp).state))
            logger.debug("wet bulb (raw sensor value):   " + str(self.hass.states.get(self.wetBulb).state))
            self.t_in = self.toKelvin(float(self.hass.states.get(self.outdoorTemp).state))
            self.t_out = self.toKelvin(float(self.hass.states.get(self.indoorTemp).state))
            self.t_wb  = self.toKelvin(float(self.hass.states.get(self.wetBulb).state))

            logger.debug("Temp outdoor:      " + str(self.t_in))
            logger.debug("Temp indoor :      " + str(self.t_out))
            logger.debug("wet bulb:       " + str(self.t_wb))


            logger.debug("The wet bulb temperature is "+ str(self.t_wb -273.15))
            logger.debug("Calculation ------  " )
            logger.debug("The dry bulb temperature (t_in): "+ str(self.t_in))
            logger.debug("The dry bulb temperature (t_out): "+ str(self.t_out))
            logger.debug("The wet bulb temperature is (t_wb)"+ str( self.t_wb ))
            logger.debug("cooling_efficiency = (t_in - t_out)/(t_in - t_wb)")
            # Formula: https://en.wikipedia.org/wiki/Evaporative_cooler
            self._state = round( ((self.t_in - self.t_out)/(self.t_in - self.t_wb) ) * 100, 2)
            logger.debug("The efficiency is           " + str(self._state))
        except ValueError as e:
            logger.warning("Some input sensor values are still unavailable")

        except AttributeError:
            logger.error("Some entity does not exist or is spelled incorrectly. Did its component initialise correctly?")
    

