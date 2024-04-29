import serial
import re
from mqtt_client import MQTTClient
import json
import time
from datetime import datetime

if __name__ == "__main__":
    broker_address = "test.mosquitto.org"
    port = 1883
    topicMagnetometer = "sensorbox1/Magnetometer"
    topicGyroscope = "sensorbox1/Gyroscope"
    topicAccelerometer = "sensorbox1/Accelerometer"
    #topictest= "sensorbox1/test"
    mqtt_client = MQTTClient(broker_address, port)
    mqtt_client.connect()
    time.sleep(2)
    s = serial.Serial('COM9')
    triplettaAccelerometer = []
    triplettaGyroscope_str = []
    triplettaMagnetometer = []
    # Apre il file in modalità append
    file= open('nome_file.txt', 'a')
    try:
    # Continua a leggere dalla porta seriale finché è aperta
        while s.is_open:
            res = s.readline()
            # Ottieni la data corrente
            data_corrente = datetime.now()
            # Formatta la data nel formato desiderato (ad esempio, 'YYYY-MM-DD')
            data_formattata = data_corrente.strftime('%Y-%m-%d')
            # Messaggio da inviare
            #message = "Questo è un messaggio di prova da inviare tramite MQTT"
            # Presa dei valori
            valori = re.findall(r'-?\d+', res.decode('utf-8'))
            # Assegna le triplette di numeri a tre variabili separate se i valori sono diversi dai precedenti
            if(len(triplettaAccelerometer) == 0 or valori[:3] != triplettaAccelerometer):
                triplettaAccelerometer = valori[:3]
                # Crea un dizionario con gli attributi desiderati per le triplette
                json_triplettaAccelerometer = {
                "x": triplettaAccelerometer[0],
                "y": triplettaAccelerometer[1],
                "z": triplettaAccelerometer[2]
                }
                # Converti il dizionario in una stringa JSON
                json_string_triplettaAccelerometer = json.dumps(json_triplettaAccelerometer)
                # Pubblica il messaggio sul topic specificato
                mqtt_client.publish_message(topicAccelerometer, json_string_triplettaAccelerometer)
                # Scrivi i dati nel file
                file.write(f"Data: {data_formattata}, Sensore: Accelerometer, x: {triplettaAccelerometer[0]}, y: {triplettaAccelerometer[1]}, z: {triplettaAccelerometer[2]}\n")
            if(len(triplettaGyroscope_str) == 0 or valori[3:6] != triplettaGyroscope_str):
                triplettaGyroscope_str = valori[3:6]
                #divido per 1000 i valori del giroscopio
                triplettaGyroscope = [float(valore) / 1000.0 for valore in triplettaGyroscope_str]
                # Crea un dizionario con gli attributi desiderati per le triplette
                json_triplettaGyroscope = {
                    "x": str(triplettaGyroscope[0]),
                    "y": str(triplettaGyroscope[1]),
                    "z": str(triplettaGyroscope[2])
                }
                # Converti il dizionario in una stringa JSON
                json_string_triplettaGyroscope = json.dumps(json_triplettaGyroscope)
                # Pubblica il messaggio sul topic specificato
                mqtt_client.publish_message(topicGyroscope, json_string_triplettaGyroscope)
                # Scrivi i dati nel file
                file.write(f"Data: {data_formattata}, Sensore: Gyroscope, x: {triplettaGyroscope[0]}, y: {triplettaGyroscope[1]}, z: {triplettaGyroscope[2]}\n")
            if(len(triplettaMagnetometer) == 0 or valori[6:9] != triplettaMagnetometer):
                triplettaMagnetometer = valori[6:9]
                # Crea un dizionario con gli attributi desiderati per le triplette
                json_triplettaMagnetometer = {
                "x": triplettaMagnetometer[0],
                "y": triplettaMagnetometer[1],
                "z": triplettaMagnetometer[2]
                }
                # Converti il dizionario in una stringa JSON
                json_string_triplettaMagnetometer = json.dumps(json_triplettaMagnetometer)
                # Pubblica il messaggio sul topic specificato
                mqtt_client.publish_message(topicMagnetometer, json_string_triplettaMagnetometer)
                # Scrivi i dati nel file
                file.write(f"Data: {data_formattata}, Sensore: Magnetometer, x: {triplettaMagnetometer[0]}, y: {triplettaMagnetometer[1]}, z: {triplettaMagnetometer[2]}\n")

            #aspetta un secondo
            time.sleep(0.5)
    except serial.SerialException:
        print("La porta seriale non è più disponibile. Uscita dal ciclo.")
    except KeyboardInterrupt:
    # Gestisce l'interruzione del programma (es. con CTRL+C)
        print("Richiesta di termine script accettata.")
    except PermissionError:
        print("Non hai i permessi per scrivere sul file.")
    except FileNotFoundError:
        print("Il file non è stato trovato.")
    except IOError as e:
        print("Errore di input/output:", e)
    except OSError as e:
        print("Errore del sistema operativo:", e)
    except Exception as e:
        print("Si è verificato un errore generico:", e)
    finally:
        s.close()
        mqtt_client.disconnect()
        file.close()   