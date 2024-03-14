#include <windows.h>
#include <iostream>

/* Function running a terminal command in a new Process. In addition to the
command to execute, a flag driving the way the command is run has to be given.
It returns the exit code of the command.
*/
int run_cmd(char* command, int flag){

    // Objects to pass to the CreateProcess function
    PROCESS_INFORMATION ProcessInfo;
    STARTUPINFO StartupInfo;
    DWORD exit_code;
    ZeroMemory(&StartupInfo, sizeof(StartupInfo));
    StartupInfo.cb = sizeof StartupInfo;

    std::cout << "Trying to run command: " << command << "\n\n";

    // Starting the new Process in charge of running the command
    int ret = CreateProcess(NULL, command, NULL, NULL, FALSE, flag, NULL,
                            NULL, &StartupInfo, &ProcessInfo);

    // In case the Process is successfully started, it returns a non-zero value
    if (ret){
        DWORD timeout = (flag == CREATE_NEW_CONSOLE) ? 0 : INFINITE;
        WaitForSingleObject(ProcessInfo.hProcess, timeout);
        GetExitCodeProcess(ProcessInfo.hProcess, &exit_code);
        CloseHandle(ProcessInfo.hThread);
        CloseHandle(ProcessInfo.hProcess);
    }
    // If the Process fails to start, it returns 0
    else {
        std::cout << "Could not run command \"" + (std::string) command + "\", failed with error code " + std::to_string(GetLastError()) + "\n\n";
        // Returning 1 to signal that the Process failed to start
        return 1;
    }

    // Returning the exit code of the Process
    return (int) exit_code;
}
