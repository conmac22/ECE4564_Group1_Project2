import argparse
import time
import pika
import pymongo

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, required=True, help="Repository RPi IP", metavar='REPO_RPI_IP')
    args = parser.parse_args()
    REPO_RPI_IP = args.s

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
    document = {"Action":action, "Place":place, "MsgID":MsgID, "Subject":subject, "Message":message}
    print(document)

    # Connect to MongoDB
    # password = 'zUwz4Dvn61VIwoHT'
    #cluster = pymongo.MongoClient('mongodb+srv://seans_laptop:' + password + '@cluster0.kvaed.mongodb.net/Cluster0?retryWrites=true&w=majority')
    #db = cluster["UserData"]
    #collection = db["test"]

    # Send message to MongoDB
    #collection.insert_one(document)

    # Send to Repository RPi
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.51'))
    channel = connection.channel()
    channel.queue_declare(queue='Classrooms')
    channel.basic_publish(exchange='Goodwin', routing_key='Classrooms', body=message)
    connection.close()



