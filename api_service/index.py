import os
import json
import boto3

print('Hello from pipeline!')

lambda_client = boto3.client('lambda')
sqs_client = boto3.client('sqs')

sqs_queue_url = os.environ.get('SQSQueueUrl')
data_service_function_name = os.environ.get('DataServiceFunctionName')


def send_message_to_sqs(data, success_text):
    response_from_sqs = sqs_client.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=json.dumps(data)
    )
    status_code = response_from_sqs['ResponseMetadata']['HTTPStatusCode']
    if status_code == 200:
        return {'Successfully': success_text}
    else:
        print(response_from_sqs)
        return {'Error': 'Something going wrong!'}


def get_tasks_list(**kwargs):
    body = kwargs.get('body')
    search_by = body.get('search_by')
    key_word = body.get('key_word')
    if search_by != '' and key_word != '':
        data_request = {
            'data_function': 'search_tasks',
            'body': {
                'search_by': search_by,
                'key_word': key_word
            }
        }
        response = lambda_client.invoke(
            FunctionName=data_service_function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(data_request)
        )
        result = json.load(response['Payload'])
        return result
    else:
        data_request = {
            'data_function': 'get_all_tasks'
        }
        response = lambda_client.invoke(
            FunctionName=data_service_function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(data_request)
        )
        result = json.load(response['Payload'])
        tasks = result.get('Tasks')
        if tasks:
            sorted_by = body.get('sorted_by')
            if sorted_by != 'None':
                reversed = body.get('reversed')
                if reversed == 'on':
                    is_reversed = True
                else:
                    is_reversed = False
                tasks.sort(key=lambda task: task[sorted_by], reverse=is_reversed)
            return {'Tasks': tasks}
        else:
            return {'Empty': 'There isn\'t any tasks now'}


def create_new_task(**kwargs):
    body = kwargs.get('body')
    data_request = {
        'data_function': 'create_task',
        'body': body
    }
    successfull_text = 'Message to create new task added to SQS queue'
    response_to_web_ui = send_message_to_sqs(data_request, successfull_text)
    return response_to_web_ui


def get_task(**kwargs):
    task_id = kwargs.get('task_id')
    data_request = {
        'data_function': 'get_task',
        'body': {
            'task_id': task_id
        }
    }
    response = lambda_client.invoke(
        FunctionName=data_service_function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(data_request)
    )
    result = json.load(response['Payload'])
    if result:
        task = result.get('Task')
        return {'Task': task}
    else:
        return {'Error': f'Task with id: {task_id} not found!'}


def add_tag(**kwargs):
    task_id = kwargs.get('task_id')
    body = kwargs.get('body')
    tag = body.get('tag')
    data_request = {
        'data_function': 'add_tag',
        'body': {
            'task_id': task_id,
            'tag': tag
        }
    }
    successfull_text = 'Message to add new tag to task added to SQS queue'
    response_to_web_ui = send_message_to_sqs(data_request, successfull_text)
    return response_to_web_ui


def update_task(**kwargs):
    task_id = kwargs.get('task_id')
    body = kwargs.get('body')
    new_task_status = body.get('task_status')
    data_request = {
        'data_function': 'update_task',
        'body': {
            'task_id': task_id,
            'new_task_status': new_task_status
        }
    }
    successfull_text = 'Message to update task status added to SQS queue'
    response_to_web_ui = send_message_to_sqs(data_request, successfull_text)
    return response_to_web_ui


def delete_task(**kwargs):
    task_id = kwargs.get('task_id')
    data_request = {
        'data_function': 'delete_task',
        'body': {
            'task_id': task_id
        }
    }
    successfull_text = 'Message to delete task added to SQS queue'
    response_to_web_ui = send_message_to_sqs(data_request, successfull_text)
    return response_to_web_ui


API_FUNCTIONS = {
    'GET': get_tasks_list,
    'POST': create_new_task,
    'GET/id': get_task,
    'POST/id': add_tag,
    'PUT/id': update_task,
    'DELETE/id': delete_task
}


def lambda_handler(event, context):
    print('Event: ', event)
    http_method = event.get('http_method')
    task_id = event.get('id')
    body = event.get('body')
    if isinstance(body, str):
        body = json.loads(body)
    if task_id:
        http_method = http_method + '/id'
    api_function = API_FUNCTIONS[http_method]
    result = api_function(task_id=task_id, body=body)
    return result
