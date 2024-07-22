import json
import time
import boto3

client = boto3.client('lambda')


def lambda_handler(event, context):
    if event['http_method'] == 'POST':
        created_at = str(time.time())
        event["body"]['created_at'] = created_at

    elif event['http_method'] == 'PUT':
        updated_at = str(time.time())
        event["body"]['updated_at'] = updated_at

    response = client.invoke(
        FunctionName='arn:aws:lambda:eu-central-1:730335656503:function:DataService',
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )

    result = json.load(response['Payload'])
    return result
