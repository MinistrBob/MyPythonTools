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

bucket = conn.get_bucket('uploads')

# Получить объект
# key = bucket.get_key('persistent/c/47/7e664d041f128c8aacafc1c1abf37b1704698aed14630130cad6ff4817729')  # bad
key = bucket.get_key('persistent/0/00/23d07267d8df05459e914f916804409420db9cf138b64d73bccc1bbcb5500')  # good
print(key.get_contents_as_string())
