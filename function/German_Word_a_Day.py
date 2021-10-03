import boto3
import random
import os
import datetime
import csv
from botocore.exceptions import ClientError

now = datetime.datetime.now()
year = lambda x: x.year
month = lambda x: x.month
day = lambda x: x.day
t = lambda x: x.time()

def lambda_handler(event, context):

    # Get the daily word and translation from function
    daily_row = daily_word_gen() 
    daily_word = daily_row[0]
    daily_translation = daily_row[1]
    
    # Add to the DynamoDB table to ensure it's not used again
    add_to_record = put_word(daily_word)
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = f"Das deutsche Tageswort für heute is {daily_word}."  
    BODY_HTML = create_html_body(daily_word, daily_translation)

    # Send the email out with SES
    send_it_out = send_email(BODY_TEXT,BODY_HTML)

def daily_word_gen():
    # Define the variables to be passed to the function
    german_dict = os.environ['german_dict']
    input_bucket = os.environ['input_bucket']
    s3_resource = boto3.resource('s3')
    s3_object = s3_resource.Object(input_bucket, german_dict)

    # Read the data from the txt file and parse into lines
    data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
    lines = csv.reader(data)
    rows = list(lines)

    # Set up while loop for ensuring same word not used again
    i = 0
    while i < 1:
        # Get the number of lines in the file and return a random line
        daily_number = random.randrange(0,len(data))
        daily_row = rows[daily_number]

        # Check if the word been featured beforehand
        daily_word = daily_row[0]
        check_word = word_check(daily_word)
        i = check_word

    return daily_row

def word_check(daily_word):
    # DynamoDB table to be used
    table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['table_name'])

    # Check if the word is already in the table
    try:
        response = table.get_item(Key={'Word': {'S': daily_word}})
    except ClientError as e:
        return 1
    else:
        return 0
    
def put_word(daily_word):

    # Add the word to the DynamoDB table
    table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['table_name'])
    response = table.put_item(
            Item={
            'Word':  daily_word,
            'Date':  "{}/{}/{}".format(day(now),month(now),year(now))
            }
        )
    return response

def create_html_body(daily_word, daily_translation):
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
      <h1>Das deutsche Tageswort ist {daily_word}, was {daily_translation} bedeutet</h1>
      <p>Diese E-Mail wurde von
        <a href='https://www.linkedin.com/in/jack-cahalane-31621899/'>Jack Cahalane</a> mit
           seinen beschissenen AWS-Kenntnissen verschickt</a>.</p>
    </body>
    </html>
                """   
    return BODY_HTML

def send_email(BODY_TEXT, BODY_HTML):

    # Set up the SES Configuration
    sender_email = os.environ['sender_email']
    SENDER = "German Word A Day <" + sender_email + ">"
    RECIPIENT = os.environ['recipient_email']
    AWS_REGION = os.environ['AWS_REGION']

    # The subject line for the email.
    SUBJECT = "Das deutsche Tageswort für {}/{}/{}".format(day(now),month(now),year(now))
    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
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
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])