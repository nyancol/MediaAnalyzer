import os
from datetime import datetime
import subprocess as sp
from media_analyzer import apis


def main():
    print("Backing Up Database")
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    backup_file = f"db-{now}"
    sp.run(f"pg_dump -Fc --file=./{backup_file}", shell=True)
    resource = apis.get_aws()
    resource.Bucket("media-analyzer-backup").put_object(Key=backup_file, Body=open(backup_file, "rb"))
    os.remove(backup_file)
    print("Backup Uploaded")


if __name__ == "__main__":
    main()
