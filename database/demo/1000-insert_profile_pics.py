import boto3

from odyssey.config import Config

s3 = boto3.resource('s3')
conf = Config()

# Copy files from 'mock-users-profile-pics' bucket to destination bucket.

source_bucket = s3.Bucket('mock-users-profile-pics')
dest_bucket = s3.Bucket(conf.AWS_S3_BUCKET)
aws_s3_prefix = conf.AWS_S3_PREFIX

if not aws_s3_prefix.endswith('/'):
    aws_s3_prefix += '/'

for obj in source_bucket.objects.all():
    copy_source = {
        'Bucket': 'mock-users-profile-pics',
        'Key': obj.key}

    dest_bucket.copy(copy_source, aws_s3_prefix + obj.key)

# Insert profile pictures into database.

preamble = """
DO $$
BEGIN
"""

postamble = """
END;
$$ LANGUAGE plpgsql;
"""

sql_insert_tmpl = """
INSERT INTO "UserProfilePictures" (
    image_path,
    width,
    height,
    original,
    client_user_id,
    staff_user_id)
VALUES (
    '{prefix}id{user_id:05d}/{user_type}_profile_picture/original.png',
    500,
    500,
    true,
    {client_user_id},
    {staff_user_id}
), (
    '{prefix}id{user_id:05d}/{user_type}_profile_picture/size512x512.jpg',
    512,
    512,
    false,
    {client_user_id},
    {staff_user_id}
), (
    '{prefix}id{user_id:05d}/{user_type}_profile_picture/size256x256.jpg',
    256,
    256,
    false,
    {client_user_id},
    {staff_user_id}
), (
    '{prefix}id{user_id:05d}/{user_type}_profile_picture/size128x128.jpg',
    128,
    128,
    false,
    {client_user_id},
    {staff_user_id}
), (
    '{prefix}id{user_id:05d}/{user_type}_profile_picture/size64x64.jpg',
    64,
    64,
    false,
    {client_user_id},
    {staff_user_id}
);
"""

staff_users = (2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16)
client_users = (17, 18, 19, 20, 21, 22, 23)

sql_parts = []

for user_id in staff_users:
    sql_insert = sql_insert_tmpl.format(
        prefix=aws_s3_prefix,
        user_id=user_id,
        user_type='staff',
        client_user_id='null',
        staff_user_id=user_id,
    )
    sql_parts.append(sql_insert)

for user_id in client_users:
    sql_insert = sql_insert_tmpl.format(
        prefix=aws_s3_prefix,
        user_id=user_id,
        user_type='client',
        client_user_id=user_id,
        staff_user_id='null',
    )
    sql_parts.append(sql_insert)

# This variable is loaded and executed as SQL on the database by the script_runner.
sql = '\n'.join([preamble] + sql_parts + [postamble])
