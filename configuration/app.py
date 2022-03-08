import json
import boto3

def lambda_handler(event, context):

    jobid = None
    if event['pathParameters'] is not None:
        jobid = event['pathParameters']['jobid'].upper()

    dynamo = boto3.resource('dynamodb')
    tbl = dynamo.Table('tsConfig')
    results = tbl.scan()

    status = 403
    retval = { }
    for row in results['Items']:
      cid = row['classId']
      if jobid is None or jobid == cid:
        status = 200  
        retval[cid] = {};
        retval[cid]['keyStats'] = row['keyStats']
        retval[cid]['shops'] = [int(id) for id in row['shops']]

    return {
      'statusCode': status,
      'body': json.dumps(retval)
    }

