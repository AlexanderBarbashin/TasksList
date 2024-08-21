import boto3
from os import environ
from zipfile import ZipFile


def update_lambda_function(lambda_client):
    lambda_function_name = environ['LAMBDA_FUNC_NAME']
    lambda_function_dir = environ['LAMBDA_FUNC_DIR']
    print("Updating lambda function: " + lambda_function_name)
    with ZipFile('index.zip', 'w') as my_zip:
        my_zip.write(f'{lambda_function_dir}/index.py', arcname='index.py')
    with open('index.zip', 'rb') as zip_file:
        zip_code = zip_file.read()
        lambda_client.update_function_code(
            FunctionName=lambda_function_name,
            ZipFile=zip_code
        )


if __name__ == "__main__":
    region = environ['AWS_REGION']
    client = boto3.client('lambda', region)
    update_lambda_function(client)
