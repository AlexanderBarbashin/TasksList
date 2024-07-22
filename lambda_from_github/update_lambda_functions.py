import boto3
from os import environ
from zipfile import ZipFile


def update_lambda_functions(lambda_client):
    lambda_api_service_function_name = environ['LAMBDA_API_SERVICE_FUNC_NAME']
    lambda_data_service_function_name = environ['LAMBDA_DATA_SERVICE_FUNC_NAME']
    print("Updating lambda functions: " + lambda_api_service_function_name + ", " + lambda_data_service_function_name)
    with ZipFile('lambda_api_service.zip', 'w') as my_zip:
        my_zip.write('api_service.py')
    with ZipFile('lambda_data_service.zip', 'w') as my_zip:
        my_zip.write('data_service.py')
    lambda_client.update_function_code(
        FunctionName=lambda_api_service_function_name,
        ZipFile='lambda_api_service.zip'
    )
    lambda_client.update_function_code(
        FunctionName=lambda_data_service_function_name,
        ZipFile='lambda_data_service.zip'
    )


if __name__ == "__main__":
    region = environ['AWS_REGION']
    client = boto3.client('lambda', region)
    update_lambda_functions(client)
