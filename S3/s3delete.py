import boto
import boto.s3.connection
import os
import secret

access_key = secret.access_key
secret_key = secret.secret_key

conn = boto.connect_s3(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    host=secret.host,
    port=secret.port,
    is_secure=False,  # uncomment if you are not using ssl
    calling_format=boto.s3.connection.OrdinaryCallingFormat(),
)

for bucket in conn.get_all_buckets():
    print(f"{bucket.name}\t{bucket.creation_date}")

bucket = conn.get_bucket('uploads')

response = bucket.delete_keys(['persistent/3/c1/78187fbf633e5e7cb29fd9ea49aa1626eb27d043069637f88a386059a3877',
                               'persistent/4/69/862d543976add525d1515a5668862556bb6cd0fa190007e5b3464192a8ee8',
                               'persistent/6/91/30fccece02cd6d64db7ecea6d527b101d43cbfdf7497dc8c08c1cdae14e11',
                               'persistent/8/fa/00e9cf998808959dc59adfddf031d8ffaaf6117a66f4e136bcaccfdcd0b09',
                               'persistent/c/47/7e664d041f128c8aacafc1c1abf37b1704698aed14630130cad6ff4817729'])

print(response.deleted, response.errors)
