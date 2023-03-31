import json
import urllib3
import boto3
from urllib.parse import urlparse
client = boto3.client('ssm')
ec2client = boto3.resource('ec2')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):

    # Set parameters
    try:
        parameter = client.get_parameter(Name='/player/C1/c1ApiKey', WithDecryption=True)
        playerApiKey = parameter ['Parameter']['Value']
        parameter = client.get_parameter(Name='/player/C1/c1Region', WithDecryption=True)
        playerC1Region = parameter ['Parameter']['Value']
        http = urllib3.PoolManager()
        
    except Exception as e:
                    print(e)
                    raise Exception('error occurred')
                    
    # Find EC2 computer name of Sentry resource with Malware 
    try:
        instances = ec2client.instances.filter(Filters=[{'Name':'tag:MachineRole', 'Values': ['File']}])
        ids = []
        #print(instances)

        for instance in instances:
            ec2_name=instance.id
            print(ec2_name)
            #print(instance.id, instance.instance_type)
            ids.append(instance.id)
            resp=ec2.describe_network_interfaces();
            #print ("printing pub dns name")
            #print(resp['NetworkInterfaces'][0]['Association']['PublicDnsName'])
            ec2_name_dns = resp['NetworkInterfaces'][0]['Association']['PublicDnsName']
            print(ec2_name_dns)
                    
        url = 'https://workload.'+playerC1Region+'.cloudone.trendmicro.com/api/computers/search'
        print(url)
                
        header = {
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
                "stringValue": ec2_name
                }
            ],
            "sortByObjectID": True
        })
        
        response = http.request(
            'POST',
            url,
            headers=header,
        )
         
        id_computer=[]      
        if response.status == 200:
            # success!
            data = json.loads(response.data.decode('utf-8'))
            print("Successfully accessed API")
            #print(data)
        else:
            print(response.data)
            print(json.loads(response.data.decode('utf-8'))) # body
            raise Exception('error occurred')

        for i in data["computers"]:
            if i["hostName"]==ec2_name_dns:
                id_computer=i["ID"]
        id_computer=str(id_computer)    
        print(id_computer)
        
        url2 = 'https://workload.'+playerC1Region+'.cloudone.trendmicro.com/api/computers/'+id_computer
        
        print(url2) 
        
        try:
            response2 = http.request(
                'GET',
                url2,
                headers=header,
            )
        except Exception as e:
            print(e)
            raise Exception('error occurred')
        if response2.status == 200:
            data = json.loads(response2.data.decode('utf-8'))
            #print(data)
        else:
            print(response2.data)
            print(json.loads(response2.data.decode('utf-8'))) # body
            raise Exception('error occurred')
            return "Wrong Request"
        
        C1WSAgentStatus = data["agentVersion"]
        C1WSAgentStatus=str(C1WSAgentStatus)
        print(C1WSAgentStatus)
        
        if C1WSAgentStatus == "0.0.0.0":
            print("You have not installed C1WS to the required EC2 machine")
            return (False)
        else:
            print("Congratulations, C1WS detected")
            return (True)
        
    except Exception as e:
                    print(e)
                    
