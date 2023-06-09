#!/usr/bin/env python3
from boto3 import client
from json import dumps
from botocore.exceptions import ClientError


def main():
    # Create an S3 client
    s3 = client('s3')

    # Get a list of S3 buckets for (default) account
    buckets = s3.list_buckets()['Buckets']

    # Write results to JSON
    with open('s3-duplicates.json', 'w') as file:
        file.write(dumps(_check(s3, buckets)))


def _check(s3, buckets):
    # Create a dictionary to store object hashes and their corresponding (bucket, key)
    object_table = dict()

    # Iterate through each bucket in the list
    for bucket in buckets:
        # Get bucket name
        bucket_name=bucket['Name']

        # Get a list of all objects in the S3 bucket
        try:
            objects = s3.list_objects(Bucket=bucket_name)
        except ClientError:
            print(f'Bucket "{bucket_name}" does not appear to exist')
            continue

        # Check if bucket is empty (i.e. no contents)
        if 'Contents' not in objects:
            print(f'"{bucket_name}" is empty')
            continue

        # Iterate through each object in the bucket and store its hash and (bucket, key) tuple in the dictionary
        for obj in objects['Contents']:
            # Skip empty files
            if not obj['Size']:
                continue
            etag = obj['ETag'].strip('"')
            size = str(obj['Size'])
            hash_value=','.join((etag, size))
            key = obj['Key']
            object_table.setdefault(hash_value, []).append((bucket_name, key))

    dupe_table=dict()
    # Iterate through the dictionary and find any objects with multiple (bucket, key) tuples (i.e. duplicates)
    for hash_value, tuples in object_table.items():
        if len(tuples) == 1:
            continue
        dupe_table[hash_value]=tuples

    return dupe_table


if __name__ == '__main__':
    main()
