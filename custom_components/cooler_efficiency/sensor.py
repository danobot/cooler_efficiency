"""
This file is part of Cooler Efficiency.

Cooler Efficiency is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cooler Efficiency is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cooler Efficiency.  If not, see <https://www.gnu.org/licenses/>.

"""

"""
Evaporative Cooling efficiency calculator for Home Assistant.
Maintainer:       Daniel Mason
Version:          v0.0.1
Documentation:    https://github.com/danobot/meteologic_metrics
Issues Tracker:   Report issues on Github. Ensure you have the latest version. Include:
                    * YAML configuration (for the misbehaving entity)
                    * log entries at time of error and at time of initialisation
"""

from homeassistant.helpers.entity import Entity
import logging
import math as m
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.components.notify import (
    ATTR_MESSAGE, DOMAIN as DOMAIN_NOTIFY)
from homeassistant.components.sensor import (DOMAIN as DOMAIN_SENSOR)
from datetime import datetime
from .entity_services import (
    async_setup_entity_services,
)

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
    component = EntityComponent(logger, DOMAIN_SENSOR, hass)

    sensor = ExampleSensor(hass, config)
    async_setup_entity_services(component)

    component.async_add_entities([sensor])
    # add_devices([sensor])


class ExampleSensor(Entity):
    """Representation of a Sensor."""
    from .entity_services import (
        async_entity_service_start_experiment as async_start_experiment,
    )
    
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
        self.logger = logger

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
        if self._data_available():
            turn_on_ac, turn_on_ac_text = self._should_turn_on_ac()
            attr = {
                    "indoor temp": round(self.t_outdoor, 2),
                    "outdoor temp": round(self.t_indoor, 2),
                    "actual temp delta": round(self.t_delta_actual, 2),
                    "optimal temp delta": round(self.t_delta_best, 2),
                    "wet bulb temp": round(self.t_wb, 2),
                    "ac recommendation":  turn_on_ac,
                    "ac recommendation description":  turn_on_ac_text
            }
        attr["wet bulb sensor"] = self.wetBulb
        attr["Outside sensor"] = self.outdoorTemp
        attr["Indoor sensor"] =self.indoorTemp

        return attr
    def _outdoor_temp(self):
        return self.hass.states.get(self.outdoorTemp).state
    def _indoor_temp(self):
        return self.hass.states.get(self.indoorTemp).state
    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            
            self.t_wb  = self.toKelvin(float(self.hass.states.get(self.wetBulb).state))
            logger.debug("Temp outdoor (raw sensor value): " + str(self._outdoor_temp))
            logger.debug("Temp indoor (raw sensor value):  " + str(self._indoor_temp))
            logger.debug("wet bulb (raw sensor value):   " + str(self.t_wb))

            self.t_outdoor = self.toKelvin(float(self.hass.states.get(self.outdoorTemp).state))
            self.t_indoor = self.toKelvin(float(self.hass.states.get(self.indoorTemp).state))

            logger.debug("Temp outdoor:      " + str(self.t_outdoor))
            logger.debug("Temp indoor :      " + str(self.t_indoor))
            logger.debug("wet bulb:       " + str(self.t_wb))


            logger.debug("The wet bulb temperature is "+ str(self.t_wb))
            logger.debug("Calculation ------  " )
            logger.debug("The dry bulb temperature (t_in): "+ str(self.t_outdoor))
            logger.debug("The dry bulb temperature (t_out): "+ str(self.t_indoor))
            logger.debug("The wet bulb temperature is (t_wb)"+ str( self.t_wb ))
            logger.debug("cooling_efficiency = (t_in - t_out)/(t_in - t_wb)")
            self.t_delta_actual = self.t_outdoor - self.t_indoor
            self.t_delta_best = self.t_outdoor - self.t_wb
            # Formula: https://en.wikipedia.org/wiki/Evaporative_cooler
            self._state = round( (self.t_delta_actual/ self.t_delta_best ) * 100, 1)
            logger.debug("The efficiency is           " + str(self._state))
            self.update_data()
            self.update_recommendation()


        except ValueError as e:
            logger.warning("Some input sensor values are still unavailable")

        except AttributeError:
            logger.error("Some entity does not exist or is spelled incorrectly. Did its component initialise correctly?")
        except Exception as e:
            logger.error(e)

    def _should_turn_on_ac(self):
        if self._state > 100:
            logger.debug("_should_turn_on_ac: No, it already cooler than the best AC can achieve. This state is also triggered if your temperature sensors are inaccurate (+/- 1-2 degrees)")
            return False, "No, it already cooler than the best AC can achieve. turning it on now would increase the temperature and humidity inside."
        
        if self.t_delta_actual < 2:
            logger.debug("_should_turn_on_ac: No, indoor temp is only %s degrees from optimal temperature." % (self.t_delta_actual))
            return False, "No, indoor temp is only %s degrees from optimal temperature. Turning it on now, would have a small to no effect on temperature and would unesearily increase indoor humidity." % (self.t_delta_actual)
        
        if self._state <= 0:
            logger.debug("_should_turn_on_ac: No, ventilating the house is better, it's cool outside.")
            return False, "No, ventilating the house is better.  It's cool outside. Turning AC on now would increase humidity and apparent temperature."
        return True, "Yes"

    def _data_available(self):
        return self.t_outdoor and self.t_indoor and self.t_wb and self.t_delta_best and self.t_delta_actual

    def update_data(self):
        csv_data = []
        csv_header = []
        for e in self.entities:
            logger.debug("Querying %s to log it" % (e))
            try:
                entity = self.hass.states.get(e)
            except AttributeError:
                raise Exception("%s does not exist." % (e))
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

    @property
    def should_poll(self) -> bool:
        return True