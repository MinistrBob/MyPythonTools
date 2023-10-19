import boto
import boto.s3.connection
import os
from boto.s3.key import Key
# from boto.s3.connection import S3Connection

access_key = '23RD0S2E7S50K5JUP1AK'
secret_key = 'Rfhgqy9oLkFzbqCy0DlB1Fhyk8LvUTvA7CWn7jue'

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = '172.16.174.10',
        port = 7480,
        is_secure=False,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )
print(1)
bucket = conn.create_bucket('my-new-bucket')
for bucket in conn.get_all_buckets():
        print "{name}\t{created}".format(
                name = bucket.name,
                created = bucket.creation_date,
)

print(2)
# Load objects to bucket
## from string
bucket.new_key('test-string').set_contents_from_string('TEST')

print(3)
## from file
file_key_1 = Key(bucket)
file_key_1.key = 's3test.py'
file_key_1.set_contents_from_filename('s3test.py')
file_key_2 = Key(bucket)
file_key_2.key = 'script/s3test.py'
file_key_2.set_contents_from_filename('s3test.py')

print(4)
# Get list of objects from bucket
keys_list=bucket.list()
for key in keys_list:
    print key.key

print(5)
# Delete some objects
response = bucket.delete_keys(['test-string', 's3test.py'])
print(response)

print(6)
# Get object content
key = bucket.get_key('script/s3test.py')
print key.get_contents_as_string()

print(7)
response = bucket.delete_keys(['script/s3test.py'])
print(response)

print(8)
result = conn.delete_bucket('my-new-bucket')
if result:
  print(result)
