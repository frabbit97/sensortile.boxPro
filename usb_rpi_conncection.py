import usb.core
import time
import re
from array import array
from mqtt_client import MQTTClient
import json
from datetime import datetime
if __name__ == "__main__":
    try:
        broker_address = "test.mosquitto.org"
        port = 1883
        topicMagnetometer = "sensorbox1/Magnetometer"
        topicGyroscope = "sensorbox1/Gyroscope"
        topicAccelerometer = "sensorbox1/Accelerometer"
        mqtt_client = MQTTClient(broker_address, port)
        mqtt_client.connect()
        time.sleep(2)
        # Apre il file in modalità append
        file= open('nome_file.txt', 'a')
        # find our device
        dev = usb.core.find(idVendor=0x0483, idProduct=0x5740)
        # was it found?
        if dev is None:
            raise ValueError('Device not found')
        dev.set_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(1,0)]
        #print(intf)
        ep = intf[1]
        #print(ep)
        dev.set_interface_altsetting(intf)
        while(1):
            ret= dev.read(ep,64)
            #print(ret)
            bytes_array = bytes(ret)
            stringa = bytes_array.decode('utf-8')
            #print(stringa)
            # Rimuove i caratteri di spaziatura non standard
            stringa_pulita = re.sub(r'\s+', '', stringa)
            #print(stringa_pulita)
            # Dividi la stringa in base alla virgola seguita da spazi
            elementi = stringa_pulita.split(",")
            #print(elementi)
            # Converte gli elementi in interi e li mette in un vettore
            vettore = [int(elemento) for elemento in elementi]
            #print(vettore)
            if(len(vettore)>=10):
                temperature=vettore[0]
                accelerometer={'x':vettore[1],'y':vettore[2],'z':vettore[3]}
                json_accelerometer=json.dumps(accelerometer)
                gyroscope={'x':vettore[4]/100.0,'y':vettore[5]/100.0,'z':vettore[6]/100.0}
                json_gyroscope=json.dumps(gyroscope)
                magnetometer={'x':vettore[7],'y':vettore[8],'z':vettore[9]}
                json_magnetometer=json.dumps(magnetometer)
                print("Temperature of ",temperature,"°C")
                print("Accelerometer\n X:",accelerometer['x'],"mg\n","Y:",accelerometer['y'],"mg\n","Z:",accelerometer['z'],"mg")
                print("Gyroscope\n X:",gyroscope['x'],"dps\n","Y:",gyroscope['y'],"dps\n","Z:",gyroscope['z'],"dps")
                print("Magnetometer\n X:",magnetometer['x'],"mGa\n","Y:",magnetometer['y'],"mGa\n","Z:",magnetometer['z'],"mGa")
                # Ottieni la data corrente
                data_corrente = datetime.now()
                # Formatta la data nel formato desiderato (ad esempio, 'YYYY-MM-DD-HH-MM')
                data_formattata = data_corrente.strftime('%Y-%m-%d-%H-%M')
                #publish in the topic mqtt
                mqtt_client.publish_message(topicAccelerometer, json_accelerometer)
                mqtt_client.publish_message(topicGyroscope, json_gyroscope)
                mqtt_client.publish_message(topicMagnetometer, json_magnetometer)
                # Scrivi i dati nel file
                file.write(f"Data: {data_formattata}\nSensor: Accelerometer x: {accelerometer['x']}, y: {accelerometer['y']}, z: {accelerometer['z']}\nSensor: Gyroscope x: {gyroscope['x']}, y: {gyroscope['y']}, z: {gyroscope['z']}\nSensor: Magnetometer x: {magnetometer['x']}, y: {magnetometer['y']}, z: {magnetometer['z']}\n")
            else:
                raise ValueError('Error in retrieve data!')
            time.sleep(1)
    except Exception as e:
        print("Si è verificato un errore generico:", e)
    finally:
        mqtt_client.disconnect()
        file.close()   
