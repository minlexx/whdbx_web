#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>

int wmain( int argc, wchar_t **argv ) {
	wchar_t cmdLine[1024] = {0};
	wchar_t fileName[512] = {0};

	HMODULE hMe = GetModuleHandle(NULL);
	GetModuleFileName( hMe, fileName, 521 );
	wchar_t *last_backslash = wcsrchr( fileName, L'\\' );
	if( last_backslash ) {
		*last_backslash = L'\0';
	}
	lstrcatW( fileName, L"\\python.exe" );

	if( argc > 1 ) {
		int i;
		for( i=1; i<argc; i++ ) {
			lstrcatW( cmdLine, argv[i] );
			lstrcatW( cmdLine, L" " );
		}
	}

	wchar_t launch_cmdline[1024] = {0};
	lstrcpyW( launch_cmdline, fileName );
	lstrcatW( launch_cmdline, L" " );
	lstrcatW( launch_cmdline, cmdLine );

	SetEnvironmentVariableW( L"PYTHONIOENCODING", L"utf-8" );

	STARTUPINFOW si;
	PROCESS_INFORMATION pi;

	SecureZeroMemory( &si, sizeof(si) );
	SecureZeroMemory( &pi, sizeof(pi) );

	si.cb = sizeof(si);
	si.dwFlags = STARTF_USESTDHANDLES;
	si.hStdError = GetStdHandle(STD_ERROR_HANDLE);
	si.hStdInput = GetStdHandle(STD_INPUT_HANDLE);
	si.hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);

	//if( !CreateProcessW( fileName, cmdLine, NULL, NULL, TRUE, CREATE_UNICODE_ENVIRONMENT, NULL, NULL, &si, &pi ) ) {
	if( !CreateProcessW( NULL, launch_cmdline, NULL, NULL, TRUE, CREATE_UNICODE_ENVIRONMENT, NULL, NULL, &si, &pi ) ) {
		DWORD le = GetLastError();
		fwprintf( stdout, L"CreateProcessW() failed: %d\n", (int)le );
		//fwprintf( stdout, L"Started [%s] with cmdline [%s]\n", fileName, lpszCmdLine );
		fwprintf( stdout, L"Started [%s]\n", launch_cmdline );
		return le;
	}

	WaitForSingleObject( pi.hProcess, INFINITE );
	CloseHandle( pi.hThread );
	CloseHandle( pi.hProcess );

	return 0;
}
