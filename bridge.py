import argparse
import time
import pika
import pymongo
import bluetooth
import socket
from gpiozero import RGBLED
from time import sleep

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, required=True, help="Repository RPi IP", metavar='REPO_RPI_IP')
    args = parser.parse_args()
    REPO_RPI_IP = args.s
    
    # Setup RGBLED
    led = RGBLED(red =16, green=20, blue=21)
    led.color = (1,1,1)
    sleep(1)

    server_sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM )
    port = 1
    server_sock.bind(("",port))
    server_sock.listen(1)
    print("Waiting to accept connection")
    client_sock,address = server_sock.accept()
    print("accepted connection from, %s",address)
    while True:

        # Receive message command from mobile phone
        #CMD = "p:Squires+Rooms I like the comfortable chairs on 3rd floor"
        CMD = client_sock.recv(1024)
        CMDstr = CMD.decode()
        print("Received command: " + CMDstr)
        ticks = time.time()
        MsgID = "1$" + str(ticks)

        # Determine action.  'p' for produce, 'c' for consume
        command = CMDstr.split(':')
        action = command[0]

        # Determine Place and Subject
        command_message = command[1].split(' ')
        Place_Subject = command_message[0].split('+')
        place = Place_Subject[0]
        subject = Place_Subject[1]

        # Determine message
        global document
        if command == 'p':
            message = ''
            for word in command_message[1:]:
                message += word + ' '
            # Build Message
            document = {"Action":action, "Place":place, "MsgID":MsgID, "Subject":subject, "Message":message}
            
            print(document)

            # Connect to MongoDB
            password = 'zUwz4Dvn61VIwoHT'
            cluster = pymongo.MongoClient(
                'mongodb+srv://seans_laptop:' + password + '@cluster0.kvaed.mongodb.net/Cluster0?retryWrites=true&w=majority')
            db = cluster["UserData"]
            collection = db["test"]
            # Send message to MongoDB
            led.color = (0,0,1)
            sleep(1)
            collection.insert_one(document)
        elif command == 'c':
            document = {"Action":action, "Place":place, "MsgID":MsgID, "Subject":subject}
            print(document)
            # Connect to MongoDB
            password = 'zUwz4Dvn61VIwoHT'
            cluster = pymongo.MongoClient(
                'mongodb+srv://seans_laptop:' + password + '@cluster0.kvaed.mongodb.net/Cluster0?retryWrites=true&w=majority')
            db = cluster["UserData"]
            collection = db["test"]

            # Send message to MongoDB
            led.color = (0,0,1)
            sleep(1)
            collection.insert_one(document)
        


        # Send to Repository RPi
        credentials = pika.PlainCredentials('user1', 'user1')

        connection = pika.BlockingConnection(pika.ConnectionParameters(REPO_RPI_IP, 5672, '/', credentials))
        channel = connection.channel()

        # Middleware example
        channel.queue_declare(queue=subject, durable=True)
        if action == 'p':
            led.color = (1,0,0)
            sleep(1)
            channel.basic_publish(exchange=place, routing_key=subject, body=message)
            connection.close()
        elif action == 'c':
            led.color = (0,1,0)
            sleep(1)
            def callback(ch, method, properties, body):
                print('[x] Received ' + body)
            channel.basic_consume(callback, queue=subject, no_ack=True)
            channel.start_consuming()
