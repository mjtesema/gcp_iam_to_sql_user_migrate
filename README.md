# gcp_iam_to_sql_user_migrate
Quick &amp; Dirty user-migrate script that fetches from gcloud iam get-iam-policy (at project level) and creates users for specified instances via gcloud cmds


### Example Usage
./iam_to_sqlserver_user_migrate.sh -i instance0,instance1 -d "" -p <your_gcp_project_id> -v 1

Any questions - feel free to add comments to this repo & I will update the scripts accordingly
