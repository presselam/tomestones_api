import simplejson as json
import boto3
import requests

def lambda_handler(event, context):
  status = 400 
  mesg = 'Bad Request'

  params = event['pathParameters']

  userid = None
  if 'userid' in params:
    userid = int(params['userid'])
        
  jobid = None
  if 'jobid' in params:
    jobid = params['jobid'].upper()

  retval = None;
  if jobid is not None:
    retval = getUserFromDynamo(userid,jobid)
  else:
    retval = getUserFromXIVAPI(userid)

  return {
    'statusCode': 200,
    'body': json.dumps(retval)
  }


def getUserFromXIVAPI(userid: int):
  resp = requests.get('https://xivapi.com/character/' + str(userid) + '?extended=1')
  data = resp.json()
  data = data['Character']
  acj = data['ActiveClassJob']
  cid = acj['Job']['Abbreviation']

  retval = {}
  retval['jobid'] = cid
  retval['id'] = int(data['ID'])
  retval['name'] = data['Name']
  retval['image'] = data['Portrait']
  retval['parsed'] = data['ParseDate']
  retval['jobid'] = acj['Job']['Abbreviation']
  retval['job'] = acj['Job']['Name']
  retval['icon'] = acj['Job']['Icon']
  retval['level'] = int(acj['Level'])
  retval['xp'] = int(acj['ExpLevel'])
  retval['xpmax'] = int(acj['ExpLevelMax'])

  gear={}
  for slot in data['GearSet']['Gear'].keys():
      item = data['GearSet']['Gear'][slot]['Item']
      gear[slot]={}
      gear[slot]['id'] = int(item['ID'])
      gear[slot]['name'] = item['Name']
      gear[slot]['level'] = int(item['LevelEquip'])
      gear[slot]['ilvl'] = int(item['LevelItem'])

  retval['gear'] = gear

  dynamo = boto3.resource('dynamodb')
  table = dynamo.Table('tsCharacter')
  table.put_item(Item=retval)

  return retval


    
def getUserFromDynamo(userid: int, jobid: str):    
  dynamo = boto3.resource('dynamodb')
  tbl = dynamo.Table('tsCharacter')
  res = tbl.get_item(Key={'jobid': jobid})

  retval = None
  if 'Item' in res.keys():
    item = res['Item']
    retval = item

  return retval


  
