import boto
import boto.s3.connection
import os
import secret
import datetime

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


def get_key(key_):
    # print(f"{key_.name}\t{key_.size}\t{key_.last_modified}")
    try:
        # await key_.get_contents_as_string()
        # print(key_.get_contents_as_string())
        i = key_.get_contents_as_string()
    except Exception as err:
        print(err)
        print(f"ERROR: {key_.name}\t{key_.size}\t{key_.last_modified}")


def main():
    counter = 0
    mine_time = datetime.datetime.now()
    loop_time = datetime.datetime.now()
    for key in bucket.list():
        # print(key.get_contents_as_string())
        get_key(key)
        counter += 1
        if counter % 100 == 0:
            print(f"Processed: {counter} obj. | Loop time: {datetime.datetime.now() - loop_time} sec.| ALL TIME: {datetime.datetime.now() - mine_time} sec.")
            loop_time = datetime.datetime.now()
        # default input:
        # cdate = '\t'.join(key.last_modified.split('T'))
        # print(f"{key.name}\t{key.size}\t{cdate}")
        # persistent/1/41/365bff7a46b05f50447c6b3c7938751f0afe6e3c11fdd4c4b333a645dec47	34688	2021-02-04T15:38:46.521Z
        # Получить объект
        # print(key.get_contents_as_string())
    print("Finish")


if __name__ == '__main__':
    main()
