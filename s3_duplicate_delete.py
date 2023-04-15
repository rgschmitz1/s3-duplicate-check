#!/usr/bin/env python3
from boto3 import client
from botocore.exceptions import ClientError
from json import loads
from os.path import exists
import sys


def main():
    if len(sys.argv) == 1:
        _usage()
    elif not exists(sys.argv[1]):
        print(f'ERROR: Invalid file path "{sys.argv[1]}"')
        _usage()

    # If at least 1 argument is passed, assume it is a file path
    json_file = sys.argv[1]

    # Create an S3 client
    s3 = client('s3')

    # Read duplicates from JSON
    with open(json_file, 'r') as file:
        try:
            object_table = loads(file.read())
        except:
            sys.exit(f'ERROR: {sys.argv[1]} is not a valid JSON file')

    # Verify with the user that they wish to delete objects
    _confirm()

    if not _delete(s3, object_table):
        print('ERROR: A failure occurred while deleting objects')


def _usage():
    sys.exit(f'''Usage: {sys.argv[0]} <json file>''')


def _confirm():
    answer=None
    while not answer and answer != 'y' and answer != 'n':
        answer = input('Do you want to delete duplicate objects (y/n): ')
    if answer == 'n':
        sys.exit(0)
    confirm=None
    while not confirm and confirm != 'y' and confirm != 'n':
        print('WARNING: deleting objects is not reversible.')
        confirm = input('Please confirm you want to delete duplicate objects (y/n): ')
    if confirm == 'n':
        sys.exit(0)


# Iterate through the dictionary and delete any objects with multiple (bucket, key) tuples (i.e. duplicates)
def _delete(s3, object_table):
    for hash_value, tuples in object_table.items():
        for bucket_name, key in tuples[1:]:
            print(f'Deleting key "{key}" from bucket "{bucket_name}"')
            try:
                s3.delete_object(Bucket=bucket_name, Key=key)
            except ClientError as e:
                print(e)
                return False
    return True


if __name__ == '__main__':
    main()
