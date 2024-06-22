from kafka import KafkaConsumer, KafkaProducer
import json

bootstrap_servers = ['localhost:9092']

# Initialize Kafka Consumer for 'transactions' topic
consumer = KafkaConsumer('transactions', bootstrap_servers=bootstrap_servers, auto_offset_reset='earliest', enable_auto_commit=True)

# Initialize Kafka Producer
producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# Consume messages from the 'transactions' topic
for message in consumer:
    transaction_data = json.loads(message.value.decode('utf-8'))
    
    # Check if amount exceeds 4000 and age is over 40
    if float(transaction_data['amount']) > 4000 and int(transaction_data['customer_age']) > 40:
        print("Received transaction data matching criteria:", transaction_data)
        
        # Send customer_id and message to 'alerts' topic
        alert_data = {'customer_id': transaction_data['customer_id'], 'message': 'fraud'}
        producer.send('alerts', value=alert_data)
        print("Sent to 'alerts' topic:", alert_data)
    else:
        print("Received transaction data:", transaction_data)

consumer.close()
producer.close()

