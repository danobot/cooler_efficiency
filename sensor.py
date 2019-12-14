from homeassistant.helpers.entity import Entity
import logging


logger = logging.getLogger(__name__)

CONF_OUTDOOR_SENSOR = 'outdoor_temp'
CONF_OUTDOOR_HUM = 'outdoor_hum'
CONF_INDOOR_SENSOR = 'indoor_temp'
CONF_INDOOR_HUM = 'indoor_hum'
CONF_PRESSURE = 'pressure'
CONF_NAME = 'name'
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([ExampleSensor()])


class ExampleSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        print(config)
        self.outdoorTemp = config.get(CONF_OUTDOOR_TEMP)
        self.indoorTemp = config.get(CONF_INDOOR_TEMP)
        self.outdoorHum = config.get(CONF_OUTDOOR_HUM)
        self.indoorHum = config.get(CONF_INDOOR_HUM)
        self.pressure = config.get(CONF_PRESSURE)
        self.pressure = config.get(CONF_NAME)
        self._state = None


    @property
    def name(self):
        """Return the name of the sensor."""
        return self.name or 'Cooling efficiency'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # logger.info(dir(self))
        # logger.info(dir(self.hass))
        temp_out = toKelvin(float(self.hass.states.get(self.outdoorTemp).state))
        logger.info("Temp outdoor: " + str(temp_out))
        temp_in = toKelvin(float(self.hass.states.get(self.indoorTemp).state))
        logger.info("Temp indoor : " + str(temp_in))
        hum_out = toKelvin(float(self.hass.states.get(self.outdoorHum).state))
        logger.info("hum outdoor: " + str(hum_out))
        hum_in = toKelvin(float(self.hass.states.get(self.indoorHum).state))
        logger.info("hum indoor : " + str(hum_in))
        pressure = float(self.hass.states.get(self.pressure).state*100)
        logger.info("pressure (pascal): " + str(pressure))


        # S=SI.state("DBT",300,"RH",0.32,101325)

        Tin = temp_out
        Tewb = getWetBulb(temp_out, hum_out, 1007.9)
        # Tewb = getWetBulb(temp_out, hum_out, self.pressure)
        Tout = temp_in

        c = (Tin - Tout)/(Tin-Tewb)
        logger.debug("The dry bulb temperature is ", temp_out)
        logger.debug("The wet bulb temperature is ", Tewb)
        logger.debug("The relative humidity is ", hum_out)
        logger.debug("The efficiency is ", c)
        logger.debug(c)
        return c

def getWetBulb(self, dry, hum, pressure):
    # dpDepression = dry - dew
    # return dry - dpDepression/3
    return __WBT_DBT_W_P(dry,hum, pressure)

def toKelvin(self, celsius):
    return celsius + 273.15

def __DBT_H_WBT_P(H, WBT, P):
    [DBTa, DBTb]=[Min_DBT, Max_DBT]
    DBT=(DBTa+DBTb)/2
    while DBTb-DBTa>TOL:
        ya=__W_DBT_WBT_P(DBTa, WBT, P)-__W_DBT_H(DBTa, H)
        y=__W_DBT_WBT_P(DBT, WBT, P)-__W_DBT_H(DBT, H)
        if __is_positive(y)==__is_positive(ya):
            DBTa=DBT
        else:
            DBTb=DBT
        DBT=(DBTa+DBTb)/2
    return DBT