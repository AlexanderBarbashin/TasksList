import json
import boto3
from boto3.dynamodb.conditions import Key
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')


def get_task_by_id(id):
    response = table.get_item(
        Key={
            'id': id
        }
    )
    task = response['Item']
    return task


def get_task(**kwargs):
    task_id = kwargs.get('task_id')
    if task_id:
        try:
            task = get_task_by_id(task_id)
            return task
        except KeyError:
            return {'Error': f'Task with id {task_id} not found!'}
    else:
        response = table.scan()
        tasks = response['Items']
        if tasks:
            return {'Tasks': tasks}
        else:
            return {'Empty': 'There isn\'t any tasks now'}


def add_task(**kwargs):
    task_id = str(uuid.uuid4())
    new_task = kwargs.get('body')
    table.put_item(
        Item={
            'id': task_id,
            'title': new_task['title'],
            'description': new_task['description'],
            'task_status': new_task['task_status'],
            'created_at': new_task['created_at']
        }
    )
    return {'New task id': task_id}


def update_task(**kwargs):
    task_id = kwargs.get('task_id')
    try:
        task = get_task_by_id(task_id)
    except KeyError:
        return {'Error': f'Task with id {task_id} not found!'}
    updated_task = kwargs.get('body')
    table.update_item(
        Key={
            'id': task_id
        },
        UpdateExpression='SET task_status = :val1, updated_at = :val2',
        ExpressionAttributeValues={
            ':val1': updated_task['task_status'],
            ':val2': updated_task['updated_at']
        }
    )
    return {'Successfully': f'Task with id {task_id} was updated'}


def delete_task(**kwargs):
    task_id = kwargs.get('task_id')
    try:
        task = get_task_by_id(task_id)
    except KeyError:
        return {'Error': f'Task with id {task_id} not found!'}
    table.delete_item(
        Key={
            'id': task_id
        }
    )
    return {'Successfully': f'Task with id {task_id} was deleted'}


ACTIONS = {
    'GET': get_task,
    'POST': add_task,
    'PUT': update_task,
    'DELETE': delete_task
}


def lambda_handler(event, context):
    action = event.get('http_method')
    task_id = event.get('id')
    body = event.get('body')
    db_function = ACTIONS[action]
    result = db_function(task_id=task_id, body=body)
    return result
