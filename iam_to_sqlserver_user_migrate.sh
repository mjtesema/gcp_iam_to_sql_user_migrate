#!/bin/bash

INSTANCE_LIST=""
PASSWD_DEFAULT=""

while getopts i:d:p:v o
do	case "$o" in
	i)	INSTANCE_LIST="$OPTARG";;
	d)	DEFAULT_PASSWORD="$OPTARG";;
    p)	PROJECT_ID="$OPTARG";;
    v)  VERBOSITY=1 ;;
	[?])	print >&2 "Usage: $0 -i instance_list_comma_sep -p default_password"
		exit 1;;
	esac
done
shift $OPTIND-1

if [ $VERBOSITY -ge 1 ]
then
    echo "Using verbose mode"
    for instance in "${INSTANCE_LIST[@]}";do echo "instance: $instance\n"; done
    echo "Default Password: ${DEFAULT_PASSWORD}"
    echo "Project ID: ${PROJECT_ID}"
fi

datenow=`date -u "+%Y%m%d%H%M"`
mv iam.out.latest iam.out.latest.${datenow}
gcloud projects get-iam-policy $PROJECT_ID | grep -e cloudsql -e user -e serviceAccount -e members -e owner > iam.out.latest
#users=` python3 parseiam.py --iam_output_file=iam.out.latest`
rm iam.out.latest.2*


IFS=","; read -a instances <<< "$INSTANCE_LIST"
for instance in "${instances[@]}";
do 
    if [ $VERBOSITY -ge 1 ]; then
        IFS=" " ; read -r users <<< `python3 parseiam.py --iam_output_file=iam.out.latest`
        for user in $users; do
            echo "USER=> $user"
            `gcloud sql users create $user --instance=$instance --password=$DEFAULT_PASSWORD --verbosity=debug`; 
        done
    else
        IFS=" " ; read -r users <<< `python3 parseiam.py --iam_output_file=iam.out.latest`
        for user in $users; do 
            echo "USER=> $user"
            `gcloud sql users create $user --instance=$instance --password=$DEFAULT_PASSWORD`; 
        done
    fi

done


#TODO(): Compatability to remove users from instances as they are removed from IAM Groups

#TODO(): After CloudSQL-SQLServer connectivity via gcloud issue 147178379 is resolved
#   Being able to add capability for this to run grant statements will be possible
