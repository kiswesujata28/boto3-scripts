import json
import boto3
import logging
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
    
def lambda_handler(event, context):
    eventName = str(event['detail']['eventName'])
    userName = str(event['detail']['requestParameters']['userName'])
    consoleUser = str(event['detail']['userIdentity']['userName'])
    print(event)
    print(eventName)
    print(consoleUser)
    print(userName)
    
    iam_client = boto3.client('iam')
    response = iam_client.list_user_tags(UserName=userName)
    do_tags_exists = tags_exist(response['Tags'], userName, consoleUser)
    logger.info("Tags Exists %s.", do_tags_exists)
    if do_tags_exists:
        print("All tags exists")
    else:
        print("Some tags does not exists")
        

def tags_exist(tags, userName, consoleUser):
    user_type = False
    responsible_user = False
    contact_email = False
    bool = False
    tag_violation = []
    for tag in tags:
        user_tag = str(tag['Key']).lower()
        logger.info("Tags Name %s.", user_tag)
        if str(tag['Key']).lower() == "user_type":
            user_type = True
        if str(tag['Key']).lower() == "responsible_user":
            responsible_user = True
        if user_tag == "contact_email":
            contact_email = True

    if user_type and responsible_user and contact_email:
        bool = True
    else:
        bool = False
        
    if user_type == False:
        tag_violation.append("user_type")
    if responsible_user == False:
        tag_violation.append("responsible_user")
    if contact_email == False:
        tag_violation.append("contact_email")
    print(tag_violation)
    message1 = str(" **** IAM User COMPLIANCE ALERT (wba-sandbox) ***** ")
    message2 = str(" || IAM User: [ " + str(userName) + " ] is missing these tags" + " [ "+ ', '.join(tag_violation)+ " ]")
    message3 = str(" || Created by: " + str(consoleUser))
    message = message1+message2+message3
    print(message)
    slack_notification(message)
                   
    return bool


def slack_notification(message):
    http = urllib3.PoolManager()
    
    data = {"text": message}
    
    r = http.request("POST",
                     "https://hooks.slack.com/services/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",
                     body = json.dumps(data),
                     headers = {"Content-Type": "application/json"} 
                    )
    return