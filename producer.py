import time
from kafka import KafkaProducer, KafkaConsumer
import csv
import json
from time import sleep

bootstrap_servers = ['localhost:9092']

# Initialize Kafka Producer with JSON serializer
producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def is_row_present_in_alerts(row, bootstrap_servers):
    # Create a Kafka consumer and consume all messages to get a set of customer_ids
    consumer = KafkaConsumer('alerts', 
                             bootstrap_servers=bootstrap_servers, 
                             auto_offset_reset='earliest', 
                             enable_auto_commit=True,
                             consumer_timeout_ms=1000)    
    customer_ids = set()
    start_time = time.time()
    
    # Consume messages and add customer_ids to the set
    while True:
        for message in consumer:
            alert = json.loads(message.value.decode('utf-8'))
            customer_ids.add(alert['customer_id'])
        
            # Check the elapsed time
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                break
        else:
            # Check the elapsed time after each poll
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                break
        # Break the outer loop if the time is up
        if elapsed_time >= 1:
            break
    
    consumer.close()
    
    # Check if the customer_id in the row is present in the set of customer_ids
    if row['customer_id'] in customer_ids:
        print(f"This {row['customer_id']} has committed fraud")
        return True
    else:
        print(f"No fraud detected for customer_id {row['customer_id']}")
        return False

def read_csv_and_send_to_kafka(csv_file_path, bootstrap_servers):
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Check if the row is already present in alerts
            if is_row_present_in_alerts(row, bootstrap_servers):
                print(f"Ignored: Row with customer_id {row['customer_id']} already present in 'alerts' topic")
                continue  # Skip sending to 'transactions' if row is already present in 'alerts'
            data_to_send = {
                'customer_id': row['customer_id'],
                'customer_age': row['customer_age'],
                'amount': row['amount']
            }
            producer.send('transactions', value=data_to_send)
            print(f"Sent to 'transactions' topic: {data_to_send}")
            
            sleep(4)

csv_file_path = '/home/maemoon/Documents/BDA_Final/Q2/synthetic_financial_data.csv'
read_csv_and_send_to_kafka(csv_file_path, bootstrap_servers)
producer.close()
