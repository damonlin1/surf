import boto3
import os

s3BucketName = 'textract-console-us-east-1-5d794769-13a2-4b5e-9e3c-e9456eeee922'
documentName = 'merged1.pdf'

client = boto3.client('textract', region_name='us-east-1')

# Call Amazon Textract
response = client.detect_document_text(
    Document={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': documentName
        }
    })

print(response)
