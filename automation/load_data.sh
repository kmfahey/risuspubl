#!/bin/bash

echo $PWD

# Source the .env file to set environment variables
source .env

export PGPASSWORD=$DB_PASSWORD

# Use the environment variables to run psql
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -f ./db_data_load.sql
