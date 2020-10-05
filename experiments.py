import boto3

s3 = boto3.resource('s3',
    aws_access_key_id='AKIA2KDLMCWZDL4ANMHP',
    aws_secret_access_key='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'
)

try:
    s3.create_bucket(Bucket='iph3-bucket', CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
except:
    print("this may already exist")

# make bucket publicly readable
bucket = s3.Bucket("iph3-bucket")
bucket.Acl().put(ACL='public-read')

# upload a new object into the bucket
body = open('/Users/bellahilty/Documents/smiley.png', 'rb')

o = s3.Object('iph3-bucket', 'test').put(Body=body)
s3.Object('iph3-bucket', 'test').Acl().put(ACL='public-read')

dyndb = boto3.resource('dynamodb',
    region_name='us-west-2',
    aws_access_key_id='AKIA2KDLMCWZDL4ANMHP',
    aws_secret_access_key='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'
)

try:
    table = dyndb.create_table(
        TableName='DataTable',
        KeySchema=[
            {
                'AttributeName': 'PartitionKey',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'RowKey',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PartitionKey',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'RowKey',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
except:
    table = dyndb.Table("DataTable")

# wait for table to be created
table.meta.client.get_waiter('table_exists').wait(TableName='DataTable')

print(table.item_count)

import csv

with open('/Users/bellahilty/Documents/experiments.csv', 'rt') as csvfile:
    csvf = csv.reader(csvfile, delimiter=',', quotechar='|')
    for item in csvf:
        print(item)
        body = open('/Users/bellahilty/Documents/cloudhw/boto3/uploads/' + item[3], 'rb')
        s3.Object('iph3-bucket', item[3]).put(Body=body )
        md = s3.Object('iph3-bucket', item[3]).Acl().put(ACL='public-read')

        url = " https://s3-us-west-2.amazonaws.com/iph3-bucket/"+item[3]
        metadata_item = {'PartitionKey': item[0], 'RowKey': item[1],
            'description' : item[4], 'date' : item[2], 'url':url}

        try:
            table.put_item(Item=metadata_item)
        except:
            print("item may already be there or another failure")

response = table.get_item(
    Key={
        'PartitionKey': 'experiment3',
        'RowKey': '4'
    }
)
item = response['Item']
print(item)
response
