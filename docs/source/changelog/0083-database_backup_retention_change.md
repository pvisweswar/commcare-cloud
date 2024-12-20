<!--THIS FILE IS AUTOGENERATED: DO NOT EDIT-->
<!--See https://github.com/dimagi/commcare-cloud/blob/master/changelog/README.md for instructions-->
# 83. Database Backup Retention Change

**Date:** 2024-10-25

**Optional per env:** _only required on some environments_


## CommCare Version Dependency
This change is not known to be dependent on any particular version of CommCare.


## Change Context
The logic used to retain database backups has been modified to better respect the settings that specify
how many days to keep backups.

## Details
No action is needed. This is just to inform you that the logic determining which backups to
keep has been modified. This impacts the values set for services like [couchdb](https://github.com/dimagi/commcare-cloud/blob/c3abda48758fb337ca87e8039f1b97e333129351/src/commcare_cloud/ansible/roles/couchdb2/defaults/main.yml#L9-L10),
[postgres](https://github.com/dimagi/commcare-cloud/blob/c3abda48758fb337ca87e8039f1b97e333129351/src/commcare_cloud/ansible/roles/pg_backup/defaults/main.yml#L9-L10),
and [blob](https://github.com/dimagi/commcare-cloud/blob/c3abda48758fb337ca87e8039f1b97e333129351/src/commcare_cloud/ansible/roles/backups/defaults/main.yml#L5-L6).

Put simply, if the <service>_backup_days value was set to 2, 4 daily backups would exist on your
machine at any given time. This change reduces that value to 3 which is more in line with what
it means to keep backups for 2 days.

## Steps to update
No action needed.
