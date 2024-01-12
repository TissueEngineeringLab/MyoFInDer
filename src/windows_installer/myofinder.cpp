// gcc myofinder.cpp -lshlwapi -o myofinder.exe

/*
This file contains the source code for building the myofinder.exe executable
managing the installation of MyoFInDer on Windows.

It can be run simply with the command:
gcc myofinder.cpp -lshlwapi -o myofinder.exe
*/

#include <stdio.h>
#include <windows.h>
#include <shlwapi.h>

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

    printf("Trying to run command: %s\n", command);

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
        printf("Could not run command \"%s\", failed with error "
               "code %i.\n", command, GetLastError());
        // Returning 1 to signal that the Process failed to start
        return 1;
    }

    // Returning the exit code of the Process
    return (int) exit_code;
}

// Simple function appending a string to another string
char* append_to_str(char* base_str, char* to_append){
    char* new_str = (char*) malloc(strlen(base_str) + strlen(to_append));
    strcpy(new_str, base_str);
    strcat(new_str, to_append);
    return new_str;
}

/*
The main function run by the myofinder.exe executable. Before starting
MyoFInDer, it checks that:
- Python is installed
- The application folder exists
- The virtual environment of the application exists
- The myofinder Python module and its dependencies are installed

If needed, the application folder, the virtual environment, and the myofinder
module are automatically installed for the user.
*/
int main(int argc, char* argv[]){

    // First, building all the paths that will be needed later in the script
    // and displaying them
    char* local_app_data = getenv("LOCALAPPDATA");
    printf("LocalAppData Folder : %s\n", local_app_data);

    char* app_folder = append_to_str(local_app_data, (char*) "\\MyoFInDer");
    printf("Application Folder : %s\n", app_folder);

    char* venv_path = append_to_str(app_folder, (char*) "\\venv");
    printf("Virtual Environment Folder : %s\n", venv_path);

    char* python_exe_path = append_to_str(venv_path,
                                          (char*) "\\Scripts\\python.exe");
    printf("Python Executable Path : %s\n\n", python_exe_path);

    // Checking if Python is installed, and exiting with error if not installed
    printf("Checking if Python is installed on the system.\n");
    if (!run_cmd((char*) "python --version", 0)){
        printf("Python is installed on the system.\n\n");
    }
    else {
        printf("Python is not installed on the system, aborting!\n"
               "Please install it and try to run this file again.\n\n");
        free(app_folder);
        free(venv_path);
        free(python_exe_path);
        system("pause");
        exit(1);
    }

    // Checking if the application folder exists, and creating it if necessary
    printf("Checking if the application folder already exists.\n");
    if (PathFileExists(app_folder)){
        printf("The application folder already exists.\n\n");
    }
    else {
        printf("The application folder does not exist, creating it.\n");
        if (CreateDirectory(app_folder, NULL)){
            printf("Created the application folder.\n\n");
        }
        else {
            printf("Unable to create the application folder, failed with"
                   "error code %i.\n\n", GetLastError());
            free(app_folder);
            free(venv_path);
            free(python_exe_path);
            system("pause");
            exit(1);
        }
    }

    // Checking if the virtual environment exists, and creating it if necessary
    printf("Checking if the virtual environment already exists.\n");
    if (PathFileExists(venv_path)){
        printf("The virtual environment already exists.\n\n");
    }
    else {
        printf("The virtual environment does not exist, creating it.\n");
        char* cmd = append_to_str((char*) "python -m venv ", venv_path);
        if (run_cmd(cmd, 0)){
            printf("Created the virtual environment.\n\n");
            free(cmd);
        }
        else {
            printf("Unable to create the virtual environment, failed with"
                   "error code %i\n\n", GetLastError());
            free(cmd);
            free(app_folder);
            free(venv_path);
            free(python_exe_path);
            system("pause");
            exit(1);
        }
    }

    // Checking if the myofinder module should be started in test mode, and
    // setting a flag if so
    int test;
    printf("Checking if MyoFInDer should run in test mode.\n");
    if (argc > 2 && strcmp(argv[1], "-t") == 0){
        printf("Running MyoFInDer in test mode.\n\n");
        test = 1;
    }
    else {
        printf("Running MyoFInDer in regular mode.\n\n");
        test = 0;
    }

    // Running the command for installing MyoFInDer. If it is already
    // installed, nothing more will be installed or downloaded. Otherwise, the
    // missing packages are automatically installed
    printf("Installing or updating MyoFInDer if necessary.\n");
    char* cmd_pip = append_to_str(append_to_str(
        python_exe_path, (char*) " -m pip install --upgrade pip --retries 0 "
        "--timeout 1 "), (test) ? argv[2] : (char*) "myofinder==1.0.7");
    if (!run_cmd(cmd_pip, 0)){
        printf("MyoFInDer is correctly installed on the system.\n\n");
    }
    else {
        printf("Something went wrong while installing or updating MyoFInDer, "
               "aborting!\n\n");
        free(cmd_pip);
        free(app_folder);
        free(venv_path);
        free(python_exe_path);
        system("pause");
        exit(1);
    }
    free(cmd_pip);

    // Starting MyoFInDer, either in test mode or regular mode
    // MyoFInDer is started in a new console, so that this one can return
    char* cmd_start = append_to_str(python_exe_path, (char*) " -m myofinder");
    if (test){
        printf("Starting MyoFInDer in test mode.\n");
        run_cmd(append_to_str(cmd_start, (char*) " -t"), CREATE_NEW_CONSOLE);
    }
    else {
        printf("Starting MyoFInDer.\n");
        run_cmd(cmd_start, CREATE_NEW_CONSOLE);
    }

    free(cmd_start);
    free(app_folder);
    free(venv_path);
    free(python_exe_path);

    return 0;
}
