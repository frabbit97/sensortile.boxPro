import sys
import usb.core
import time
from time import ctime
import ntplib
import os
import re
from array import array
from mqtt_client import MQTTClient
import json
from datetime import datetime, timedelta
import asyncio
from bleak import BleakScanner


#clock sync procedure
def synch_time():
        c= ntplib.NTPClient()  #client for clock updates
        response=c.request('time.nist.gov',version=3)
        print(response.tx_time)
        os.system('sudo date -s "'+ ctime(response.tx_time)+'"')
        
def on_disconnect(client, userdata, rc):
        global connection
        if rc!=0:
                connection=False
        
#temporary solution to get an ID for the SensorTile
async def discover_devices():

    devices = await BleakScanner.discover()

    for device in devices:
            if device.name=="STB_PRO":
                     return device.address

#uid=asyncio.run(discover_devices())

iter=-1                  #number of script iterations
uid="E3:4E:8E:6A:C1:21"
sampling_period=4
connection=False

#time.sleep(10)
#print(uid)


broker_address = "test.mosquitto.org"
port = 1883
clean_session=False
#topicMagnetometer = "sensorbox1/Magnetometer"
#topicGyroscope = "sensorbox1/Gyroscope"
topicAccelerometer = "sensorbox1/Accelerometer"
topicTemperature = "sensorbox1/Temperature"


mqtt_client = MQTTClient(broker_address, port,clean_session)

while True:
        try:      
                # Opening the output file in "append" mode
                file=open('SensorTile-data.txt', 'a') 
                # searching for SensorTile.Box Pro
                #print('Cycle start')
                dev = usb.core.find(idVendor=0x0483, idProduct=0x5740)
                #print(dev)
                # was it found?
                if dev is None:
                    print('Device not found')
                    dev_set=False
                    time.sleep(4)
                    continue
                else:
                        dev_set=True
                        time_correction=False
                        time_offset=0
                        try:
                                dev.set_configuration()
                                cfg = dev.get_active_configuration()
                                print('active configuration got')
                                #print("\n\n\n",cfg)
                                intf = cfg[(1,0)]
                                #print(intf)
                                ep = intf[1]
                                #print("\n\n",ep)
                                dev.set_interface_altsetting(intf)
                        except usb.core.USBError as e:
                                if e.errno ==16:
                                        print('already configured USB device')
                                continue
                        
                        while dev_set:
                            iter+=1
                            print('\n\nIteration #',iter)
                            #This section is for periodic synch of the clock with NTP server
                            if iter%(900/sampling_period)==0:  #this should activate clock synching every 15 minutes
                                iter=0
                                try:
                                        synch_time()
                                        print('RPi Clock synched\n')
                                except Exception as e:
                                        print('Warning: impossible to synch the RPi clock with NPT server\n',e)
                            
                            ret= dev.read(ep,64)
                            #print("ret=",ret,"\n")
                            bytes_array = bytes(ret)
                            #print("bytes_array=",bytes_array,"\n")
                            string = bytes_array.decode('utf-8')
                            # Removes non-standard spacing chars 
                            clean_string= re.sub(r'\s+', '', string)
                            #print("clean string=",clean_string)
                            # Divides the string based on the commas separating the items
                            items = clean_string.split(",")
                            # Converts each item into strings and puts them into a vector
                            vector = [item for item in items]
                            #print(vector)
                            if(len(vector)>=9):
                                temperature={'uid':uid,'temperature':int(vector[0])}
                                temperature1=int(vector[0]) #integer value of the temperature
                                json_temperature=json.dumps(temperature)
                                #Original ST RTC timestamp (it can be very different for real one)
                                st_timestamp=datetime.strptime(vector[8]+' '+vector[7],'%d/%m/%Y %H:%M:%S.%f')
                                # Current RPi timestamp
                                rpi_timestamp = datetime.now()
                                #Calculating difference between the two timestamps in seconds
                                datetime_split=(rpi_timestamp-st_timestamp).total_seconds()
                                #print(datetime_split)
                                if (abs(datetime_split)>3 and time_correction==False): #if the clock of the SensorTile has an offset greater than 3 seconds with NTP Server
                                        print('Correcting the offset error in the SensorTile.Box Real Time Clock\n')
                                        time_offset=datetime_split
                                        time_correction=True
                                st_timestamp=st_timestamp+timedelta(seconds=time_offset)
                                st_timestamp=st_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                                #print(st_timestamp)
                                # Formatting the timestamp in the desired format ('YYYY-MM-DDTHH:MM:SS.fff')
                                format_rpi_timestamp = rpi_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                                lp_accelerometer={'st_timestamp':st_timestamp,'rpi_timestamp':format_rpi_timestamp,'uid':uid,'x':vector[1],'y':vector[2],'z':vector[3]}
                                lp_accelerometer={'st_timestamp':st_timestamp,'rpi_timestamp':format_rpi_timestamp,'uid':uid,'x':vector[1],'y':vector[2],'z':vector[3]}
                                json_lp_accelerometer=json.dumps(lp_accelerometer)
                                #print("json_lp_accelerometer=",json_lp_accelerometer)
                                accelerometer={'x':vector[4],'y':vector[5],'z':vector[6]}
                                json_accelerometer=json.dumps(accelerometer)
                                #print(json_accelerometer)
                                print("\nTemperature:",temperature1,"°C")
                                print("Accelerometer   X:",accelerometer['x'],"mg ","Y:",accelerometer['y'],"mg ","Z:",accelerometer['z'],"mg")
                                #print("Gyroscope\n X:",gyroscope['x'],"dps\n","Y:",gyroscope['y'],"dps\n","Z:",gyroscope['z'],"dps")
                                #print("Magnetometer\n X:",magnetometer['x'],"mGa\n","Y:",magnetometer['y'],"mGa\n","Z:",magnetometer['z'],"mGa")
                                
                                #Publish in the topic mqtt
                                print("a. Network connection =",connection)
                                mqtt_client.on_disconnect = on_disconnect
                                if not connection:
                                        print("Network not connected")
                                if not connection:
                                        try:
                                                print("Tryng to connect...")
                                                mqtt_client.connect()
                                                time.sleep(2)
                                                connection=True
                                        except socket.error as e:
                                                print("MQTT connection not available: ", e)
                                                connection=False
                                                time.sleep(4)
                                                continue
                                print("b. Network connection =",connection)
                                if connection:
                                        try:
                                                print("trying to transmit data...")
                                                res=mqtt_client.publish_message(topicAccelerometer, json_lp_accelerometer,2)
                                                res=mqtt_client.publish_message(topicTemperature, json_temperature,2)
                                                #mqtt_client.publish_message(topicGyroscope, json_gyroscope)
                                                #mqtt_client.publish_message(topicMagnetometer, json_magnetometer)
                                        except Exception as e:
                                                print("MQTT connection is not available: ", e)
                                                connection=False
                                                time.sleep(4)
                                                continue
                                else:
                                        print('Impossible to send data via MQTT, connection probably lost')
                                # Writing data to file
                                try:
                                        file.write(f"{uid},{format_rpi_timestamp},{temperature1},{lp_accelerometer['x']},{lp_accelerometer['y']},{lp_accelerometer['z']}\n")
                                        file.flush()
                                except Exception as e:
                                        print('Impossible to save data to file\n',e)
                            else:
                                raise ValueError('Error in retrieve data!')
                            time.sleep(sampling_period)
        except PermissionError:
                print("You don't have the necessary permissions to write on the file. Continuing without file logging")
                continue
        except FileNotFoundError:
                print("Selected file has not been found.")
                continue
        except IOError as e:
                print("I/O error: ", e)
                time.sleep(4)
                continue
        except OSError as e:
                print("OS error: ", e)
                time.sleep(4)
                continue             
        except Exception as e:
                print("Si è verificato un errore generico:", e)
                usb.util.dispose_resources(dev)
                dev_set=False
                time.sleep(4)
                continue
        except KeyboardInterrupt:
    		# Managing keyboard interrupt to stop the script (e.g.: CTRL+C)
                print("\nTerminating the script...")
                mqtt_client.disconnect()
                file.close()
                sys.exit()
        #finally:
        #   mqtt_client.disconnect()
        #   file.close()  
