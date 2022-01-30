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

for key in bucket.list():
    print("{name}\t{size}\t{modified}".format(
        name=key.name,
        size=key.size,
        modified=key.last_modified,
    ))

    file_name = key.name.split('/')[-1] + ".jpg"
    print(file_name)
    # key = bucket.get_key('perl_poetry.pdf')
    file_path = os.path.join("c:\\", "!SAVE", "images", file_name)
    print(file_path)
    key.get_contents_to_filename(file_path)

"""
bucket = conn.get_bucket('images')

for key in bucket.list():
    print("{name}\t{size}\t{modified}".format(
        name=key.name,
        size=key.size,
        modified=key.last_modified,
    ))

bucket = conn.get_bucket('documents ')

for key in bucket.list():
    print("{name}\t{size}\t{modified}".format(
        name=key.name,
        size=key.size,
        modified=key.last_modified,
    ))
"""
