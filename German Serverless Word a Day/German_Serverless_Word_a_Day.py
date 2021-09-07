import boto3
import os
import json
import random
import csv
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    #Define the variables to be passed to the function
    german_dict = 'german_vocab.csv'
    input_bucket = 'serverless-german-word-a-day'
    s3_resource = boto3.resource('s3')
    s3_object = s3_resource.Object(input_bucket, german_dict)

    #Read the data from the txt file and parse into lines
    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
    
    #Get the number of lines in the file and return a random line
    daily_number = random.randrange(0,len(data))
    daily_word = data[daily_number]

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "German Word A Day <cahalnej@tcd.ie>"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = "jackcahalane@gmail.com"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "eu-west-1"

    # The subject line for the email.
    SUBJECT = "Amazon SES Test (SDK for Python)"
    
    # The email body for recipients with non-HTML email clients.
    
    BODY_TEXT = f"The German Word of the Day is {daily_word}."       
    
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
      <h1>{daily_word}</h1>
      <p>This email was sent by
        <a href='https://www.linkedin.com/in/jack-cahalane-31621899/'>Jack Cahalane</a> using his
          atrocious AWS skills</a>.</p>
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
    return daily_word