import json
import urllib3
import boto3
from urllib.parse import urlparse
client = boto3.client('ssm')
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):

    # Set parameters
    parameter = client.get_parameter(Name='/player/C1/c1ApiKey', WithDecryption=True)
    playerApiKey = parameter ['Parameter']['Value']
    parameter = client.get_parameter(Name='/player/C1/c1Region', WithDecryption=True)
    playerC1Region = parameter ['Parameter']['Value']
    running_with = []
    running_without = []
    C1_protected_names = []

    # Find EC2 computer name of Sentry resource with Malware 
    for instance in ec2.instances.all():

        if instance.state['Name'] != 'running':
            continue
        has_tag = False
        for tag in instance.tags:
            if tag['Key'] == 'MachineRole' and tag['Value'] == 'File':
                has_tag = True
                break

            if has_tag:
                running_with.append(instance.id)
            else:
                running_without.append(instance.id)

        print("With: %s" % running_with)
        print("Without: %s" % running_without)

        # EC2 with MachineRole tag is now stored in running_with - convert to string:
        for c in running_with:
            ec2_name += c
        print(ec2_name)

        url = 'https://workload.'+playerC1Region+'.cloudone.trendmicro.com/api/computers/search'
                
        headers = {
            "Content-Type": "application/json",
            "Authorization": "ApiKey "+playerApiKey,
            "api-version": "v1"
        }
                
        payload = json.dumps({
            "maxItems": 1,
            "searchCriteria": [
                {
                "fieldName": "hostName",
                "stringTest": "equal",
                "stringValue": "server-00"
                }
            ],
            "sortByObjectID": True
        })
                
        response = http.request(
            "POST",
            url,
            headers = headers, 
            body = payload
        )
                
        if response.status == 200:
            data = json.loads(response.data.decode('utf-8'))
            if data["computers"]:
                return data["computers"][0]["groupID"]
            return None




        # Check C1WS for protected machine with name matching ec2_name
        urlCluster = 'https://container.'+playerC1Region+'.cloudone.trendmicro.com/api/clusters/playerC1csClusterID'
        payloadCluster = json.dumps({
        })
        headers = {
            'api-version': 'v1',
            'Authorization': 'ApiKey '+playerApiKey+'',
            'Content-Type': 'application/json'
        }
        http = urllib3.PoolManager()
        encoded_payload = payloadCluster.encode("utf-8")
        message = "Not yet completed"
        try:
            clusterEvalResponse = http.request("GET", url=urlCluster, headers=headers) #, body=encoded_payload)
                
            #print(clusterEvalResponse.data.decode("utf-8"))
            clusterEval = json.loads(clusterEvalResponse.data.decode("utf-8"))
            clusterName = clusterEval["name"]
            #print(clusterName)
                                      
            playerComplete = "no"
            if clusterName == "ProductionCluster":
                playerComplete = "yes"
                message = "Task completed"
                print(message)
                return (True)
        except:
            print('We were not able to complete the call and check the clusters name')
            print(message)


        # Check if the specific EC2 with tag is present and protected in C1WS
        arr = [1, 2, 3, 4]
        v = 3
        x = 2
        if(x(arr, v)):
            ec2name = clusterName
            print("EC2 is protected by C1WS")
            return (True)
        else:
	        print("Element is Not Present in the list")