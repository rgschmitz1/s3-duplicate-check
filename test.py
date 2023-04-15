#!/usr/bin/env python3
from boto3 import client, resource
from botocore.exceptions import ClientError
from uuid import uuid4
import unittest
import sys

# methods to be tested
from s3_duplicate_check import _check
from s3_duplicate_delete import _delete


class TestS3Check(unittest.TestCase):
    def setUp(self):
        # Create a S3 client
        self.s3_client = client('s3')

        # Create two S3 buckets
        self.buckets = ({'Name': f's3-dupes-{uuid4()}'}, {'Name': f's3-dupes-{uuid4()}'})
        for bucket in self.buckets:
            try:
                self.s3_client.create_bucket(ACL='private', Bucket=bucket['Name'], CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
            except ClientError:
                sys.exit(f'ERROR: Failed creating bucket "{bucket["Name"]}"')

        # Create duplicate objects
        self.s3_client.put_object(Body=b'dupe', Bucket=self.buckets[0]['Name'], Key='dupe')
        self.s3_client.put_object(Body=b'dupe', Bucket=self.buckets[0]['Name'], Key='dupe1')
        self.s3_client.put_object(Body=b'dupe', Bucket=self.buckets[1]['Name'], Key='dupe')
        # Create one non-duplicate object
        self.s3_client.put_object(Body=b'notdupe', Bucket=self.buckets[0]['Name'], Key='notdupe')
        # Create duplicate objects that are empty
        self.s3_client.put_object(Bucket=self.buckets[0]['Name'], Key='empty')
        self.s3_client.put_object(Bucket=self.buckets[1]['Name'], Key='empty')

    def tearDown(self):
        s3_resource = resource('s3')
        # Delete all objects in S3 buckets then delete bucket
        for bucket in self.buckets:
            try:
                s3_resource.Bucket(bucket['Name']).objects.all().delete()
                self.s3_client.delete_bucket(Bucket=bucket['Name'])
            except ClientError:
                print('Error encountered deleting object/bucket')
        # Close S3 client or warnings will appear
        self.s3_client.close()

    def test_check(self):
        dupes = _check(self.s3_client, self.buckets)
        # Only one duplicate item should be present
        self.assertEqual(len(dupes), 1)
        values = [v for v in dupes.values()][0]
        self.assertEqual(len(values), 3)
        self.assertIn((self.buckets[0]['Name'], 'dupe'), values)
        self.assertIn((self.buckets[0]['Name'], 'dupe1'), values)
        self.assertIn((self.buckets[1]['Name'], 'dupe'), values)


class TestS3Delete(unittest.TestCase):
    def setUp(self):
        # Create a S3 client
        self.s3_client = client('s3')

        # Create two S3 buckets
        self.buckets = (f's3-dupes-{uuid4()}', f's3-dupes-{uuid4()}')
        for bucket in self.buckets:
            try:
                self.s3_client.create_bucket(ACL='private', Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
            except ClientError:
                sys.exit(f'ERROR: Failed creating bucket {bucket}')

        # Create duplicate objects in S3 buckets
        self.s3_client.put_object(Body=b'dupe', Bucket=self.buckets[0], Key='dupe')
        self.s3_client.put_object(Body=b'dupe', Bucket=self.buckets[0], Key='dupe1')
        self.s3_client.put_object(Body=b'dupe', Bucket=self.buckets[1], Key='dupe')

        self.json = {'etag': [
            (self.buckets[0], 'dupe'),
            (self.buckets[0], 'dupe1'),
            (self.buckets[1], 'dupe')
        ]}

    def tearDown(self):
        # Delete all objects in S3 bucket then delete bucket
        self.s3_client.delete_object(Bucket=self.buckets[0], Key='dupe')
        for bucket in self.buckets:
            try:
                self.s3_client.delete_bucket(Bucket=bucket)
            except ClientError:
                print(f'Error encountered deleting bucket "{bucket}"')
        # Close S3 client or warnings will appear
        self.s3_client.close()

    def test_delete(self):
        # Verify the delete function returns True
        self.assertTrue(_delete(self.s3_client, self.json))
        # Verify the first object in the list is present and the other two objects are deleted
        self.assertEqual(self.s3_client.head_object(Bucket=self.buckets[0], Key='dupe')['ResponseMetadata']['HTTPStatusCode'], 200)
        with self.assertRaises(ClientError):
            self.s3_client.head_object(Bucket=self.buckets[0], Key='dupe1')
        with self.assertRaises(ClientError):
            self.s3_client.head_object(Bucket=self.buckets[1], Key='dupe')


if __name__ == '__main__':
    unittest.main()
