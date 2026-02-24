#include <windows.h>
#include <iostream>
#include <string>
#include <vector>

/* Run a command with CreateProcess.
Returns the process exit code, or 1 if the process could not be started.
*/
int run_cmd(const std::string& command,
            DWORD creation_flags,
            const std::string& current_dir) {

    // Objects to pass to the CreateProcess function
    PROCESS_INFORMATION processInfo;
    STARTUPINFOA startupInfo;
    DWORD exit_code = 0;
    ZeroMemory(&startupInfo, sizeof(startupInfo));
    startupInfo.cb = sizeof(startupInfo);
    ZeroMemory(&processInfo, sizeof(processInfo));

    std::cout << "Trying to run command: " << command << "\n\n";

    // Create a writeable command line buffer
    std::vector<char> cmdline(command.begin(), command.end());
    cmdline.push_back('\0');

    // Handle empty current working directory
    LPCSTR cwd = NULL;
    if (!current_dir.empty() && dir_exists(current_dir)) {
        cwd = current_dir.c_str();
    }

    // Start the new Process in charge of running the command
    BOOL ok = CreateProcessA(
        NULL,
        cmdline.data(),
        NULL,
        NULL,
        FALSE,
        creation_flags,
        NULL,
        cwd,
        &startupInfo,
        &processInfo
    );

    if (!ok) {
        std::cout << "Could not run command \"" << command
                  << "\", failed with error code " << GetLastError() << "\n\n";
        return 1;
    }

    // In case the Process is successfully started, it returns a non-zero value
    DWORD timeout = (creation_flags == CREATE_NEW_CONSOLE) ? 0 : INFINITE;
    WaitForSingleObject(processInfo.hProcess, timeout);
    GetExitCodeProcess(processInfo.hProcess, &exit_code);
    CloseHandle(processInfo.hThread);
    CloseHandle(processInfo.hProcess);

    return static_cast<int>(exit_code);
}
