import os
import json
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid

dynamodb = boto3.resource('dynamodb')
dynamodb_table_name = os.environ.get('DynamoDBTableName')
table = dynamodb.Table(dynamodb_table_name)


def get_task_by_id(task_id):
    print(12)
    response = table.get_item(
        Key={
            'id': task_id
        }
    )
    try:
        task = response['Item']
        return task
    except KeyError:
        print('Response from query task by id: ', response)


def search_tasks(body):
    search_by = body.get('search_by')
    key_word = body.get('key_word')
    response = table.scan(
        FilterExpression=Attr(search_by).contains(key_word)
    )
    tasks = response['Items']
    if tasks:
        return {'Tasks': tasks}
    else:
        return {'Empty': f'There isn\'t any tasks now with {search_by} contains {key_word}'}


def get_all_tasks(body):
    tasks_list = []
    response = {'LastEvaluatedKey': False}
    while 'LastEvaluatedKey' in response:
        if response['LastEvaluatedKey']:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
        else:
            response = table.scan()
        tasks = response['Items']
        tasks_list.extend(tasks)
    return {'Tasks': tasks_list}


def create_task(body):
    task_id = str(uuid.uuid4())
    title = body.get('title')
    description = body.get('description')
    created_at = str(time.time())
    table.put_item(
        Item={
            'id': task_id,
            'title': title,
            'description': description,
            'task_status': 'pending',
            'created_at': created_at
        }
    )


def get_task(body):
    task_id = body.get('task_id')
    task = get_task_by_id(task_id)
    if task:
        return {'Task': task}


def add_tag(body):
    task_id = body.get('task_id')
    tag = body.get('tag')
    task = get_task_by_id(task_id)
    if task:
        tags = task.get('tags')
        if tags:
            if tags.count(tag) > 0:
                print(f'Tag {tag} already added to task with id: {task_id}!')
            else:
                tags.append(tag)
        else:
            tags = [tag]
        table.update_item(
            Key={
                'id': task_id
            },
            UpdateExpression='SET tags = :val1',
            ExpressionAttributeValues={
                ':val1': tags
            }
        )


def update_task(body):
    task_id = body.get('task_id')
    new_task_status = body.get('new_task_status')
    task = get_task_by_id(task_id)
    if task:
        updated_at = str(time.time())
        table.update_item(
            Key={
                'id': task_id
            },
            UpdateExpression='SET task_status = :val1, updated_at = :val2',
            ExpressionAttributeValues={
                ':val1': new_task_status,
                ':val2': updated_at
            }
        )


def delete_task(body):
    task_id = body.get('task_id')
    table.delete_item(
        Key={
            'id': task_id
        }
    )


DATA_FUNCTIONS = {
    'search_tasks': search_tasks,
    'get_all_tasks': get_all_tasks,
    'create_task': create_task,
    'get_task': get_task,
    'add_tag': add_tag,
    'update_task': update_task,
    'delete_task': delete_task
}


def lambda_handler(event, context):
    records = event.get('Records')
    if records:
        event = json.loads(records[0].get('body'))
    print('Event: ', event)
    data_function_name = event.get('data_function')
    body = event.get('body')
    data_function = DATA_FUNCTIONS[data_function_name]
    result = data_function(body)
    return result
