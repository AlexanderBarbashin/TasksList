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
    with open('lambda_api_service.zip', 'rb') as zip_file:
        api_zip_code = zip_file.read()
        lambda_client.update_function_code(
            FunctionName=lambda_api_service_function_name,
            ZipFile=api_zip_code
        )
    with open('lambda_data_service.zip', 'rb') as zip_file:
        data_zip_code = zip_file.read()
        lambda_client.update_function_code(
            FunctionName=lambda_data_service_function_name,
            ZipFile=data_zip_code
        )


if __name__ == "__main__":
    region = environ['AWS_REGION']
    client = boto3.client('lambda', region)
    update_lambda_functions(client)
