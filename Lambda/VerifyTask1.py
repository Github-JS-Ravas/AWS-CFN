import boto3
import urllib3
from urllib.parse import urlparse

def lambda_handler(event, context):
    try:
        COMMA = ','
        GOOD_STATE = ('CREATE_COMPLETE').split(COMMA)

        cfn_rs = boto3.resource('cloudformation')

        #Get all stacks in CREATE_COMPLETE

        good_stacks = [stack for stack in cfn_rs.stacks.all() if stack.stack_status in GOOD_STATE]
        good_stack_names = [stack.name for stack in cfn_rs.stacks.all() if stack.stack_status in GOOD_STATE]
        print(good_stack_names)
    
        for s in good_stack_names:
            if 'sentry' in s.lower():
                print('Sentry stack deployed successfully')
                return (True)
            else:
                print('Sentry stack NOT deployed successfully')
                return (False)
    
    except Exception as e:
                    print(e)