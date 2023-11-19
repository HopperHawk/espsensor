# ========== IMPORTS ========== #
import network, machine, json, utime, time
import uasyncio as asyncio
from machine import Pin, ADC
from microdot_asyncio import Microdot
from umqtt.simple import MQTTClient
# ============================= #





# ========== NETWORK ========== #
def connect_network():
    if config['wifi']['status'] == 1:
        sta_if = network.WLAN(network.STA_IF)
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(False)
        if not sta_if.isconnected():
            sta_if.active(True)
            sta_if.config(dhcp_hostname="hopperhawk")
            sta_if.connect(config['wifi']['ssid'], config['wifi']['password'])
            while not sta_if.isconnected():
                pass
        return sta_if.ifconfig()

    else:
        ap_if = network.WLAN(network.AP_IF)
        sys_id = machine.unique_id()
        ap_ssid = "HopperHawk-" + str('{:02x}{:02x}{:02x}{:02x}'.format(machine.unique_id()[0], machine.unique_id()[1], machine.unique_id()[2], machine.unique_id()[3]))
        ap_if.active(True)
        ap_if.config(essid=ap_ssid)
        while ap_if.active() == False:
            pass
        return ap_if.ifconfig()
# ============================= #



    
        


# ========== API SERVER ========== #
# API
api = Microdot()

# System status
@api.route('/status')
async def api_status(request):
    try:
        return json.dumps({'alive':True,'pellet_level':(str(calc_remaining())+'%'),'battery_level':(str(check_battery())+"v")})
    except:
        return json.dumps({'alive':False})

# Calibration
@api.route('/calibrate/<level>', methods=['GET','POST'])
async def api_calibrate(request,level):
    global config
    if request.method == 'GET':
        return str(config['hopper'][(str(level)+'_measurement')])
    elif request.method == 'POST':
        config['hopper'][(str(level)+'_measurement')] = take_measurement()
        with open('config.json', 'w') as f:
            json.dump(config,f)
        
        return str(config['hopper'][(str(level)+'_measurement')])

# Return current level
@api.route('/level')
async def api_measure(request):
    return str(calc_remaining()),200

# System reboot
@api.route('/system/<action>', methods=['POST'])
async def api_syscontrol(request,action):
    if action == 'reboot':
        machine.reset()

# System configuration management
@api.route('/configure/<setting>', methods=['GET','POST'])
async def api_sysconfig(request,setting):
    global config
    if request.method == 'GET':
        if setting == 'wifi':
            return json.dumps(config['wifi']), 200
        if setting == 'mqtt':
            return json.dumps(config['mqtt']), 200
        if setting == 'hopper':
            return json.dumps(config['hopper']), 200

    if request.method == 'POST':

        if setting == 'wifi':
            # Load configs from POST
            config['wifi']['status'] = request.json['status']
            config['wifi']['ssid'] = request.json['ssid']
            config['wifi']['password'] = request.json['password']
            
            # Save
            with open('config.json', 'w') as f:
                json.dump(config,f)
            
            return 'saved_wifi_settings'

        if setting == 'mqtt':
            # Load configs from POST
            config['mqtt']['status'] = request.json['status']
            config['mqtt']['user'] = request.json['user']
            config['mqtt']['password'] = request.json['password']
            config['mqtt']['broker_ip'] = request.json['broker_ip']
            config['mqtt']['broker_port'] = request.json['broker_port']

            # Save
            with open('config.json', 'w') as f:
                json.dump(config,f)

            return 'saved_mqtt_settings'

        if setting == 'hopper':
            # Load configs from POST
            config['hopper']['poll_frequency'] = request.json['poll_frequency']
            config['hopper']['current_pellets'] = request.json['current_pellets']

            # Save
            with open('config.json', 'w') as f:
                json.dump(config,f)

            return 'saved_hopper_settings'
# ================================ #





# ========== MQTT ========== #
# Push data to MQTT broker
def mqtt_publish(l,t,b):
    # Configure MQTT client
    client = MQTTClient('hopperhawk',config['mqtt']['broker_ip'], config['mqtt']['broker_port'], config['mqtt']['user'], config['mqtt']['password'], keepalive=60)
    
    # Try to connect and publish
    try:
        # Attempt the connection
        client.connect()

        # Publish the data
        client.publish('hopperhawk/pellets/level', msg=l)
        client.publish('hopperhawk/pellets/type', msg=t)
        client.publish('hopperhawk/sensor/battery', msg=b)

        # Wait, and disconnect
        time.sleep(.5)
        client.disconnect()

    # If it doesn't work...oh well :)
    except:
        pass
# ========================== #




# ========== SENSOR ========== #
# Configure Hardware
scan_trigger = Pin(23, Pin.OUT)
scan_echo = Pin(22, Pin.IN)
battery = ADC(Pin(34, Pin.IN))
battery.atten(ADC.ATTN_11DB)
battery.width(ADC.WIDTH_12BIT)

# Take a measurement and return in cm
def take_measurement():
    # Trigger
    scan_trigger.value(0)
    utime.sleep_us(2)
    scan_trigger.value(1)
    utime.sleep_us(5)
    scan_trigger.value(0)

    # Wait for reading from receiver
    while scan_echo.value() == 0:
        signal_off = utime.ticks_us()
    while scan_echo.value() == 1:
        signal_on = utime.ticks_us()

    # Calculate distance in cm
    timepassed = (signal_on - signal_off)
    level = ((timepassed * 0.0343) / 2)
    return level

# Calculate remaining pellets
def calc_remaining():
    # Take a measurement and calculate remaining
    level = take_measurement()
    try:
        p_level = ((level-config['hopper']['empty_measurement'])*100)/(config['hopper']['full_measurement']-config['hopper']['empty_measurement'])
    except ZeroDivisionError:
        p_level = 0

    # Clean the result
    if p_level < 0:
        p_level = 0
    if p_level > 100:
        p_level = 100

    return(round(p_level))


# Check the battery level
def check_battery():
    # Battery references
    max_battery_voltage = 3.6
    min_battery_voltage = 3.0
    
    # Get current voltage and estimate life remaining
    voltage = (battery.read() * (3.6/4096))*2
    voltage = voltage - (voltage*.05)
    battery_life = ((voltage - min_battery_voltage) / (max_battery_voltage - min_battery_voltage)) * 100;
    
    return round(voltage,2)
    
    # Primary function to poll sensor and report data via MQTT
def sensor_routine():
    # Main loop to continuously poll/report
    while True:
        if not calibration_mode:
            # Get the current hopper level (in cm), save globally for access via webserver
            global current_level
            current_level = calc_remaining()
    
            # If MQTT is enabled, publish the data
            if config['mqtt']['status'] == 1:
                mqtt_publish(str(current_level),config['hopper']['current_pellets'], str(check_battery()))

            # Sleep for user-defined amount of time before polling again
            await asyncio.sleep(config['hopper']['poll_frequency'])
# ============================ #




# ========== MAIN ========== #
def start_server():
    try:
        api.run(port=80)
    except:
        api.shutdown()

async def main():
    # Run the sensor routine
    asyncio.create_task(sensor_routine())
    
    # Run the API server
    start_server()

if __name__ == '__main__':
    # Load the config file
    try:
        config = json.load(open("config.json","r"))
    except:
        config = {
            'wifi': {'status':0,'ssid':"",'password':""},
            'mqtt': {'status':0,'password':"",'client_id':"hopperhawk",'broker_ip':"",'broker_port':1883,'user':""},
            'hopper': {'full_measurement':10,'empty_measurement':75,'current_pellets':"",'poll_frequency':300}
        }
        
        with open('config.json', 'w') as f:
            json.dump(config,f)
            
        

    # Working variables
    current_level = 0
    calibration_mode = False
    
    # Configure the network
    status = connect_network()


    # Start
    asyncio.run(main())
# ========================== #








