# Introduction
This sensor component calculates the efficiency (%) of your evaporative air conditioning system given sensory inputs such as temperature, humidity and atmospheric pressure.


![Entity Attributes](entity.png)

# Basic Configuration

```
- platform: cooler_efficiency
  name: "Aircon Efficiency Bedroom"
  outdoor_temp: sensor.outside_temp
  indoor_temp: sensor.bedroom_temp
  wet_bulb_temp: sensor.meteorologic_metrics
```

Note that this component requires the wet bulb temperature (WBT, a metric measured by a temperature sensor wrapped in a wet cloth). The purpose of this is to measure the cooling effect of evaporation. Since this is impractical to measure without special equipment, I have created another component called `meterologic_metrics` which calculates the WBT given the temperature, humidity and pressure at your location.

The simplest way to process is to install both components and use one as the input to the other.

[Meterologic Metrics Component on Github](https://github.com/danobot/meteorologic_metrics)


[Buy me a coffee](https://www.gofundme.com/danobot&rcid=r01-155117647299-36f7aa9cb3544199&pc=ot_co_campmgmt_w)

## Home Assistant Package
```
notify:
  - name: aircon_data
    platform: file
    filename: data/aircon_efficiency_data.csv
    timestamp: false
sensor:
  - platform: cooler_efficiency
    name: "Aircon Efficiency"
    outdoor_temp: sensor.outside_temp
    indoor_temp: sensor.bedroom_temp
    wet_bulb_temp: sensor.meteorologic_metrics
    csv_notifier: notify.aircon_data
    entities:
      - sensor.meteorologic_metrics
      - sensor.aircon_efficiency

  - platform: template
    sensors:
      aircon_optimal_temp_delta:
        value_template: "{{ state_attr('sensor.aircon_efficiency', 'optimal temp delta') | float }}"   
        unit_of_measurement: "°C"
      aircon_actual_temp_delta:
        value_template: "{{ state_attr('sensor.aircon_efficiency', 'actual temp delta') | float }}"    
        unit_of_measurement: "°C"
      aircon_min_possible_temp:
        value_template: "{{ state_attr('sensor.aircon_efficiency', 'wet bulb temp') | float }}"    
        unit_of_measurement: "°C"

  - platform: meteorologic_metrics
    name: "Meteorologic Metrics"
    temp: sensor.outside_temp
    hum: sensor.outside_hum
    pressure: sensor.pixel_2_xl_pressure_sensor
```    


