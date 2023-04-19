import uuid

import boto3
import json
import os

from urllib.parse import unquote_plus

s3_client = boto3.client('s3')
sqs = boto3.client('sqs')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
queue_url = 'https://sqs.us-east-1.amazonaws.com/855479483274/simplequeue'
table = dynamodb.Table('ImageTextTable')


def lambda_handler(event, context):
    # Check the event source
    event_source = event['Records'][0]['eventSource']
    print("received event: " + event_source)
    if event_source == 'aws:s3':
        # Handle S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        filename = event['Records'][0]['s3']['object']['key']
        message_body = json.dumps({"bucket": bucket, "filename": filename})
        try:
            response = sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)
            print(f'Message sent to SQS: {response["MessageId"]}')
            return {
                'statusCode': 200,
                'body': json.dumps('File name inserted into SQS queue.')
            }
        except Exception as e:
            print(f'Error sending message to SQS: {e}')
            return {
                'statusCode': 400,
                'body': json.dumps('File name insertion failed.')
            }
    elif event_source == 'aws:sqs':
        # Handle SQS event
        message = json.loads(event['Records'][0]['body'])
        print(message)
        bucket = message['bucket']
        filename = message['filename']
        print("bucket: " + bucket + "fileName: " + filename)
        try:
            rekognition_response = rekognition.detect_text(
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': filename
                    }
                }
            )
            print("rekognition response: " + str(rekognition_response))
            detected_text = [text_detection['DetectedText'] for text_detection in rekognition_response['TextDetections']]
            print("detected_labels: " + str(detected_text))
            table.put_item(
                Item={
                    'file_name': filename,
                    'detected_labels': json.dumps(detected_text),
                }
            )
            print(f'Successfully stored the detected content in DynamoDB for {filename}')
            return {
                'statusCode': 200,
                'body': json.dumps('Successfully stored the detected content in DynamoDB.')
            }
        except Exception as e:
            print(str(e))
            return {
                'statusCode': 400,
                'body': json.dumps('file type not supported!')
            }