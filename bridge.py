import argparse
import time
import pika
import pymongo
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

    # Receive message command from mobile phone
    CMD = "p:Squires+Rooms I like the comfortable chairs on 3rd floor"
    ticks = time.time()
    MsgID = "1$" + str(ticks)

    # Determine action.  'p' for produce, 'c' for consume
    command = CMD.split(':')
    action = command[0]

    # Determine Place and Subject
    command_message = command[1].split(' ')
    Place_Subject = command_message[0].split('+')
    place = Place_Subject[0]
    subject = Place_Subject[1]

    # Determine message
    message = ''
    for word in command_message[1:]:
        message += word + ' '

    # Build Message
    document = {"Action": action, "Place": place, "MsgID": MsgID, "Subject": subject, "Message": message}
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

    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.51', 5672, '/', credentials))
    channel = connection.channel()

    """""
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
    """""
    # Assignment example
    if action == 'p':
        led.color = (1,0,0)
        sleep(1)
        channel.exchange_declare(exchange=place, exchange_type='direct')
        channel.basic_publish(exchange=place, routing_key=subject, body=message)
    if action == 'c':
        led.color = (0,1,0)
        sleep(1)
        channel.queue_bind(exchange=place, queue=subject, routing_key=subject)

        def callback(ch, method, properties, body):
            print("%r:%r" % (method.routing_key, body))

        channel.basic_consume(callback, queue=subject, no_ack=True)
        channel.start_consuming()
