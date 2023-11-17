# HopperHawk Documentation

## Notes

The code in this repository is written specifically for a Rev 1.2 HopperHawk device (by Sideline Data). This is early stage/beta code and that means a few shortcuts have been taken and it may not be as optimized as it could be! You'll notice the API is currently un-authenticated and in the clear over HTTP, for right now this is intended to run as a device on your local network. There is a mobile app in development and it is definitely in the pipeline to implement more secure data-in-transit practices :)

A little overview of how this works...
The device will power on and either connect to your wi-fi (if configured) or it will stand up it's own wifi network ("HopperHawk-UniqueID"). Once connected to your home wifi, you should be able to communicate via "http://hopperhawk.local", if that doesn't work you will need to check your router/DHCP server to see what IP address it has.
If you connect to the device's network, you can interact with it using the API documentation below. The host will be: 192.168.4.1

If you want to use MQTT, all you need to do is enable it in the config.json file and provide your broker information. The HopperHawk device will publish to the following topics:
- hopperhawk/pellets/level
- hopperhawk/pellets/type
- hopperhawk/sensor/battery


The device includes a holder for an 18650 battery, if installed HopperHawk will try an estimate the battery life remaining and report that back. 

------------------------------------------------------------------------------------------


## API


<details>
 <summary><code>GET</code> <code><b>/status</b></code> <code>(gets the current status of the system including pellet level and battery percentage)</code></summary>
</details>

<details>
 <summary><code>GET</code> <code><b>/level</b></code> <code>(gets the current pellet level (will take a new measurement))</code></summary>
</details>

<details>
 <summary><code>GET</code> <code><b>/configure/<setting></b></code> <code>(gets the current configuration for the provided setting (wifi, mqtt, hopper))</code></summary>
</details>

<details>
 <summary><code>GET</code> <code><b>/calibrate/<level></b></code> <code>(gets the measurement for either 'full' or 'empty')</code></summary>
</details>

<details>
  <summary><code>POST</code> <code><b>/calibrate/<level></b></code> <code>(takes a new measurement and saves it as either the 'full' or 'empty' level)</code></summary>
</details>

<details>
  <summary><code>POST</code> <code><b>/system/reboot</b></code> <code>(reboots the device)</code></summary>
</details>

<details>
    <summary><code>POST</code> <code><b>/configure/wifi</b></code> <code>(submits new wifi settings to be saved on the device)</code></summary>

##### Parameters

> | name   |  type      | data type      | description                                          |
> | --------|------------|----------------|------------------------------------------------------|
> |  `status` | required | int | Enable (1) or Disable (0) connecting to your own wifi          |
> |  `ssid` | required | string | The SSID of your wifi         |
> | `password` | required | string | The password of your wifi         |

</details>



<details>
    <summary><code>POST</code> <code><b>/configure/mqtt</b></code> <code>(submits new mqtt settings to be saved on the device)</code></summary>

##### Parameters

> | name   |  type      | data type      | description                                          |
> | --------|------------|----------------|------------------------------------------------------|
> | `status` | required | int | Enable (1) or Disable (0) publishing to MQTT server          |
> |  `user` | required | string | The username for the MQTT broker        |
> |  `password` | required | string | The password of the MQTT broker         |
> |  `broker_ip` | required | string | The IP Address of the MQTT broker       |
> |  `broker_port` | required | int | The port of the MQTT broker        |

</details>


<details>
    <summary><code>POST</code> <code><b>/configure/mqtt</b></code> <code>(submits new mqtt settings to be saved on the device)</code></summary>

##### Parameters

> | name   |  type      | data type      | description                                          |
> | --------|------------|----------------|------------------------------------------------------|
> |`frequency` | required | int | Frequency in seconds that the sensor will take a new measurement         |


</details>





------------------------------------------------------------------------------------------


