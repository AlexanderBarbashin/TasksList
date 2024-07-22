import boto3
from os import environ
from zipfile import ZipFile


def update_lambda_functions(lambda_client):
    lambda_function_names = environ['LAMBDA_FUNC_NAME']
    print("Updating lambda functions: " + lambda_function_names[0] + ", " + lambda_function_names[1])
    with ZipFile('lambda_api_service.zip', 'w') as my_zip:
        my_zip.write('api_service.py')
    with ZipFile('lambda_data_service.zip', 'w') as my_zip:
        my_zip.write('data_service.py')
    lambda_client.update_function_code(
        FunctionName=lambda_function_names[0],
        ZipFile='lambda_api_service.zip'
    )
    lambda_client.update_function_code(
        FunctionName=lambda_function_names[1],
        ZipFile='lambda_data_service.zip'
    )


if __name__ == "__main__":
    region = environ['AWS_REGION']
    client = boto3.client('lambda', region)
    update_lambda_functions(client)
