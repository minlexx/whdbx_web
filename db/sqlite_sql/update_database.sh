#!/bin/bash

# ===== configure section =====
# path/command of sqlite3 executable
SQLITE3_EXE=sqlite3
# database file name to update
DB_FILENAME=eve.db
# list of SQL scripts to execute
SQL_FILES=( \
	"effects_new.sql" \
	"signature_oregas.sql" \
	"signatures.sql" \
	"signature_waves.sql" \
	"sleepers.sql" \
	"wanderingwormholes.sql" \
	"wormholeclassifications.sql" \
	"wormholesystems_new.sql" \
	"user_reported_statics.sql" \
)

# ===== do not edit below this line =====

echo "Updating database $DB_FILENAME:"

for i in "${SQL_FILES[@]}"
do
	echo "    Executing $i..."
	"$SQLITE3_EXE" "$DB_FILENAME" < "$i"
done

echo "Done."
