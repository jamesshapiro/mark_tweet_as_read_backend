import os
import json
import boto3
import time

dynamodb = boto3.client("dynamodb")
table_name = os.environ["TABLE_NAME"]

def lambda_handler(event, context):
    value = event["queryStringParameters"]["value"]

    query_params = {
        'TableName': table_name,
        'KeyConditionExpression': '#pk = :pk',
        'ExpressionAttributeNames': {'#pk': 'PK1'},
        'ExpressionAttributeValues': {':pk': {'S': value}},
        'Limit': 1
    }

    response = dynamodb.query(**query_params)
    item = None
    if response.get('Items'):
        item = response['Items'][0]
    
    current_timestamp = int(time.time())
    print(current_timestamp)

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,OPTIONS"
    }

    if item:
        record_timestamp = int(item["SK1"]["S"])
        print(record_timestamp)
        print(current_timestamp - record_timestamp)
        if current_timestamp - record_timestamp >= 30:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"result": "true"})
            }
    else:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                "PK1": {"S": value},
                "SK1": {"S": str(current_timestamp)}
            }
        )

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({"result": "false"})
    }