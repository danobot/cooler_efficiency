"""
Evaporative Cooling efficiency calculator for Home Assistant.
Maintainer:       Daniel Mason
Version:          v0.0.1
Documentation:    https://github.com/danobot/cooler_efficiency
Issues Tracker:   Report issues on Github. Ensure you have the latest version. Include:
                    * YAML configuration (for the misbehaving entity)
                    * log entries at time of error and at time of initialisation
"""

from homeassistant.helpers.entity import Entity
import logging
import math as m
from homeassistant.components.notify import (
    ATTR_MESSAGE, DOMAIN as DOMAIN_NOTIFY)
from datetime import datetime
logger = logging.getLogger(__name__)

CONF_NOTIFIER = 'csv_notifier'
CONF_ENTITIES = 'entities'
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
        self.t_outdoor = None
        self.t_indoor = None
        self.t_wb = None
        self.t_delta_best = None
        self.t_delta_actual = None
        self.hass = hass
        self.outdoorTemp = config.get(CONF_OUTDOOR_TEMP)
        self.notifier = config.get(CONF_NOTIFIER)
        self.entities = config.get(CONF_ENTITIES)
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
        if self._name:
            attr['name'] = self._name
        if self.t_outdoor and self.t_indoor and self.t_wb and self.t_delta_best and self.t_delta_actual:
                
            attr = {
                    "dry bulb temp in": round(self.t_outdoor, 2),
                    "dry bulb temp out": round(self.t_indoor, 2),
                    "actual temp delta": round(self.t_delta_actual, 2),
                    "optimal temp detla": round(self.t_delta_best, 2),
                    "wet bulb temp": round(self.t_wb, 2)
            }
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
            self.t_outdoor = self.toKelvin(float(self.hass.states.get(self.outdoorTemp).state))
            self.t_indoor = self.toKelvin(float(self.hass.states.get(self.indoorTemp).state))
            self.t_wb  = self.toKelvin(float(self.hass.states.get(self.wetBulb).state))

            logger.debug("Temp outdoor:      " + str(self.t_outdoor))
            logger.debug("Temp indoor :      " + str(self.t_indoor))
            logger.debug("wet bulb:       " + str(self.t_wb))


            logger.debug("The wet bulb temperature is "+ str(self.t_wb -273.15))
            logger.debug("Calculation ------  " )
            logger.debug("The dry bulb temperature (t_in): "+ str(self.t_outdoor))
            logger.debug("The dry bulb temperature (t_out): "+ str(self.t_indoor))
            logger.debug("The wet bulb temperature is (t_wb)"+ str( self.t_wb ))
            logger.debug("cooling_efficiency = (t_in - t_out)/(t_in - t_wb)")
            self.t_delta_actual = self.t_outdoor - self.t_indoor
            self.t_delta_best = self.t_outdoor - self.t_wb
            # Formula: https://en.wikipedia.org/wiki/Evaporative_cooler
            self._state = round( (self.t_delta_actual/ self.t_delta_best ) * 100, 1)
            # ((t_i - t_o)/(t_i - t_w) ) * 100
            logger.debug("The efficiency is           " + str(self._state))
            
            csv_data = []
            csv_header = []
            for e in self.entities:
                logger.debug("Querying %s to log it" % (e))
                entity = self.hass.states.get(e)
                state = entity.state
                attributes = entity.attributes
                csv_header.append("%s State" % (e))
                csv_data.append(state)
                
                logger.debug("Attributes %s" % (str(attributes)))
                for key, value in attributes.iteritems():
                    if not isinstance(value, str):
                        csv_header.append(key)
                        csv_data.append(value)

            csv_data.append('"%s"' % (', '.join(csv_header)))

            message = ", ".join([str(e) for e in csv_data])

            domain, service = self.notifier.split('.')
            csv_line =  "%s, %s" %(datetime.now() ,message)
            logger.debug("csv_line: " + csv_line)
            self.hass.async_create_task(
                self.hass.services.async_call(
                    DOMAIN_NOTIFY, service, {ATTR_MESSAGE: csv_line}
                )
            )
        except ValueError as e:
            logger.warning("Some input sensor values are still unavailable")

        except AttributeError:
            logger.error("Some entity does not exist or is spelled incorrectly. Did its component initialise correctly?")
        except Exception as e:
            logger.error(e)

