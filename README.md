# S3 duplicate utilities
Check for duplicate objects in S3 buckets, optionally delete all but one duplicate object

## Setup environment
Verify the ___python3-venv___ package is installed.
```
sudo apt install python3-venv
```

Create a virtual environment.
```
python3 -m venv venv
```
Activate the virtual environment.
```
. venv/bin/activate
```
Install required python packages.
```
pip install -r requirements.txt
```

## Setup default Amazon Web Service (AWS) credentials
This section assumes an AWS user has been created with full Amazon S3 access permissions.  See the following to create AWS IAM credentials, https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

Include the IAM credentials in `~/.aws.credentials`, see example credential file below.

```
[default]
aws_access_key_id=<access key id>
aws_secret_access_key=<secret access key>
```

## Execute duplicate check
1. Clone and navigate to the git repository directory.
2. Execute the S3 duplicate check script,
```
./s3_duplicate_check.py
```
3. The script will output a json file of all found duplicates ___s3-duplicates.json___, in the current directory

## Execute duplicate delete
1. Navigate to the git repository directory.
2. Execute the S3 duplicate delete script using the json output of the `s3_duplicate_check.py` script.
```
./s3_duplicate_delete.py s3-duplicates.json
```
3. Verify that you wish to delete duplicates, this will leave the first object for each duplicate found and delete all remaining objects.

## Unit test
Execute the unit tests using the following script,
```
./test.py
```