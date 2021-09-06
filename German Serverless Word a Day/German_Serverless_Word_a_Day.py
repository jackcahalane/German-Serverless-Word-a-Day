import boto3
import os
import json
from datetime import datetime

def lambda_handler(event, context):
    german_dict = 'cdoksmocgc-467176243-77598a.txt'
    input_bucket = 'serverless-german-word-a-day'
    s3_resource = boto3.resource('s3')
    s3_object = s3_resource.Object(input_bucket, german_dict)

    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
    
    f = open(data, "r")
    content = f.read()
    #Get contents of file `f`
    num_lines = sum(1 for line in open(data))

    content_list = content.splitlines()
    f.close()

    print(num_lines)