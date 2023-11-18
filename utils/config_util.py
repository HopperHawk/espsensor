#!/usr/bin/python3

'''
=============================
HopperHawk Management Utility
=============================

Dev utility to interact with/configure the
HopperHawk device (running firmware 0.1)

Date: 11/18/2023

~ Sideline Data ~
'''

# ========== LIBRARIES ========== #
import requests, getopt, sys
import getpass
# =============================== #





# ========== CONFIG FUNCTIONS ========== #
# Wi-Fi Configuration 
def conf_wifi():
    run_conf = True
    while run_conf:
        print("\nWi-Fi Configuration\n===================")
        conf = requests.get(url+"/configure/wifi").json()
        c_status = conf['status']
        c_ssid = conf['ssid']
        c_pass = conf['password']

        print("Status: " + str(c_status))
        print("SSID: " + str(c_ssid))
        if c_pass:
            print("Password: ********")
        else:
            print("Password: None")

        print('\nConfigurable Options\n--------------------\n0. Stop Configuration\n1. Change Status\n2. Update SSID\n3. Update Password')
        choice = input('Selection: ')

        if int(choice) == 0:
            run_conf = False
        else:
            if int(choice) == 1:
                status = input("Enable (1) or Disable (0)? ")
                payload = {'status':int(status), 'ssid':c_ssid, 'password':c_pass}
            elif int(choice) == 2:
                ssid = input("SSID: ")
                payload = {'status':c_status, 'ssid':ssid, 'password':c_pass}
            elif int(choice) == 3:
                passwd = getpass.getpass()
                payload = {'status':c_status, 'ssid':c_ssid, 'password':passwd}

            try:
                print("\nResponse: " + str((requests.post((url+"/configure/wifi"), json=payload).text)))
            except Exception as e:
                print("\nResponse: Failed to update Wi-Fi configuration!\n" + str(e))

# MQTT Configuration
def conf_mqtt():
    run_conf = True
    while run_conf:
        print("\nMQTT Configuration\n===================")
        conf = requests.get(url+"/configure/mqtt").json()
        c_status = conf['status']
        c_ip = conf['broker_ip']
        c_port = conf['broker_port']
        c_user = conf['user']
        c_pass = conf['password']

        print("Status: " + str(c_status))
        print("Broker IP: " + str(c_ip))
        print("Broker Port: " + str(c_port))
        print("Username: " + str(c_user))
        if c_pass:
            print("Password: ********")
        else:
            print("Password: None")

        print('\nConfigurable Options\n--------------------\n0. Stop Configuration\n1. Change Status\n2. Update Broker IP\n3. Update Broker Port\n4. Update Username\n5. Update Password')
        choice = input('Selection: ')
        if int(choice) == 0:
            run_conf = False
        else:
            if int(choice) == 1:
                status = input("Enable (1) or Disable (0)? ")
                payload = {"status":int(status),"user":c_user,"password":c_pass,"broker_ip":c_ip,"broker_port":int(c_port)}
            elif int(choice) == 2:
                broker_ip = input("Broker IP Address: ")
                payload = {"status":c_status,"user":c_user,"password":c_pass,"broker_ip":broker_ip,"broker_port":int(c_port)}
            elif int(choice) == 3:
                broker_port = input("Broker Port: ")
                payload = {"status":c_status,"user":c_user,"password":c_pass,"broker_ip":c_ip,"broker_port":int(broker_port)}
            elif int(choice) == 4:
                user = input("Username: ")
                payload = {"status":c_status,"user":user,"password":c_pass,"broker_ip":c_ip,"broker_port":int(c_port)}
            elif int(choice) == 5:
                passwd = getpass.getpass()
                payload = {"status":c_status,"user":c_user,"password":passwd,"broker_ip":c_ip,"broker_port":int(c_port)}

            try:
                print("\nResponse: " + str((requests.post((url+"/configure/mqtt"), json=payload)).text))
            except Exception as e:
                print("\nResponse: Failed to update MQTT configuration!\n" + str(e))

# Hopper Configuration
def conf_hopper():
    run_conf = True
    while run_conf:
        print("\nHopper Configuration\n===================")
        conf = requests.get(url+"/configure/hopper")

        c_frequency = conf.json()['poll_frequency']
        c_pellets = conf.json()['current_pellets']

        print("Polling Frequency: " + str(c_frequency))
        print("Current Pellets: " + str(c_pellets))

        print("\nConfigurable Options\n--------------------\n0. Stop Configuration\n1. Update Polling Frequency\n2. Change Pellets")
        choice = input('Selection: ')
        if int(choice) == 0:
            run_conf = False
        else:
            if int(choice) == 1:
                polling_frequency = input("New Polling Frequency (Seconds)? ")
                payload = {"poll_frequency":int(polling_frequency),"current_pellets":c_pellets}
            elif int(choice) == 2:
                curr_pellets = input("New Pellets: ")
                payload = {"poll_frequency":int(c_frequency),"current_pellets":curr_pellets}
            try:
                print("\nResponse: " + str((requests.post((url+"/configure/hopper"), json=payload)).text))
            except Exception as e:
                print("\nResponse: Failed to update hopper configuration!\n" + str(e))

# Calibration
def calibrate():
    run_cal = True
    while run_cal:
        print("\nSystem Calibration\n==================")
        empty_m = requests.get(url+"/calibrate/empty")
        full_m = requests.get(url+"/calibrate/full")
        print("Current Measurements:")
        print("Empty = " + str(empty_m.text))
        print("Full = " + str(full_m.text))
        print("\n0. Stop Calibration\n1. Take New Empty Measurement\n2. Take New Full Measurement")
        choice = input("Selection: ")

        if int(choice) == 0:
            run_cal = False
        else:
            if int(choice) == 1:
                requests.post(url+"/calibrate/empty")
            elif int(choice) == 2:
                requests.post(url+"/calibrate/full")
# ====================================== #


def present_main_menu():
    print("\n=============================\nHopperHawk Management Utility\n=============================\n")
    try: 
        status = requests.get(url+"/status").json()
        print("[ Status: Connected | Pellets: " + status['pellet_level'] + " | Battery: " + status['battery_level'] + " ]")

        print("\nConfiguration:\n-------------")
        print("1. Wi-Fi")
        print("2. MQTT")
        print("3. Hopper Config")
        print("\nSystem:\n-------")
        print("4. Reboot")
        print("5. Calibrate\n\n")

        choice = input('What would you like to do? ')

        try:
            choice = int(choice)
            if choice == 1:
                conf_wifi()
            elif choice == 2:
                conf_mqtt()
            elif choice == 3:
                conf_hopper()
            elif choice == 4:
                requests.post(url+"/system/reboot")       
            elif choice == 5:
                calibrate()

            
        except ValueError:
            print('Enter a number selection from the main menu!')
            present_main_menu()

    except Exception as e:
        print('\nFailed to connect to HopperHawk! Error:\n' + str(e))




# Main
if __name__ == "__main__":
    url = "http://"
    input_flag = 0
    argv = sys.argv[1:]
    run = True
    try:
        opts, args = getopt.getopt(argv, "s:")
    except:
        print("Error!")

    for opt,arg in opts:
        if opt in ['-s']:
            url += arg
            input_flag += 1

    if input_flag < 1:
        print('Invalid syntax! Example:\nconfig_util.py -s 127.0.0.1')
        sys.exit(0)
    
    else:
        while run:
            try:
                present_main_menu()
            except KeyboardInterrupt:
                print('\nExiting...\n')
                sys.exit(0)