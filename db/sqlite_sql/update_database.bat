@set SQLITE3_EXE=..\..\tools\sqlite-win32\sqlite3.exe
@set DB_FILENAME=..\eve.db

%SQLITE3_EXE% %DB_FILENAME% < effects_new.sql
%SQLITE3_EXE% %DB_FILENAME% < signature_oregas.sql
%SQLITE3_EXE% %DB_FILENAME% < signatures.sql
%SQLITE3_EXE% %DB_FILENAME% < signature_waves.sql
%SQLITE3_EXE% %DB_FILENAME% < sleepers.sql
%SQLITE3_EXE% %DB_FILENAME% < wanderingwormholes.sql
%SQLITE3_EXE% %DB_FILENAME% < wormholeclassifications.sql
%SQLITE3_EXE% %DB_FILENAME% < wormholesystems_new.sql
%SQLITE3_EXE% %DB_FILENAME% < user_reported_statics.sql

echo Done.
pause
