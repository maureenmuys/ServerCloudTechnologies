#!/bin/bash

# Configuration
PG_HOST="postgres-service" 
PG_PORT="5432"            
PG_USER="pgusername"
PG_DB="hello_flask_db"
BACKUP_DIR="/backups"

# Generate filenames with current date and time
CURRENT_DATE=$(date +%Y-%m-%d_%H-%M-%S)
SQL_DUMP_FILE="${BACKUP_DIR}/${PG_DB}_${CURRENT_DATE}.sql"
YAML_DUMP_FILE="${BACKUP_DIR}/${PG_DB}_${CURRENT_DATE}.yaml"

# Perform the backup
pg_dump -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB -f $SQL_DUMP_FILE
python convert_to_yaml.py $SQL_DUMP_FILE $YAML_DUMP_FILE

# Optional: Delete the SQL dump file to save space (retain only YAML backup)
rm $SQL_DUMP_FILE