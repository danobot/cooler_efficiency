# Introduction
This sensor component calculates the efficiency (%) of your evaporative air conditioning system given sensory inputs such as temperature, humidity and atmospheric pressure.

# Configuration

```
- platform: cooler_efficiency
  name: "Aircon Efficiency"
  indoor_temp: sensor.bedroom_temp
  outdoor_temp: sensor.outside_temp
  indoor_hum: sensor.bedroom_hum
  outdoor_hum: sensor.outside_hum
  pressure: sensor.bom_perth_pressure_mb
```

[Buy me a coffee](https://www.gofundme.com/danobot&rcid=r01-155117647299-36f7aa9cb3544199&pc=ot_co_campmgmt_w)
