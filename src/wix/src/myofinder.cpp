#include <shlwapi.h>
#include <iostream>
#include "run_cmd.cpp"
#include "read_register.cpp"

/*
The main function run by the myofinder.exe executable. It reads the path to the
Python executable from the registry, checks if MyoFInDer should start in test
mode, and finally launches MyoFInDer.
*/
int main(int argc, char* argv[]){

    // Retrieving the path to the Python executable of MyoFInDer
    std::string python_exe_path = read_reg(HKEY_CURRENT_USER, "SOFTWARE\\MyoFInDer Test", "MyoFInDerPythonPath");
    std::cout << "Python executable path: \"" + python_exe_path + "\"\n\n";

    // Checking if the myofinder module should be started in test mode, and
    // setting the suffix to add to the Python command to execute
    std::string test;
    std::cout << "Checking if MyoFInDer should run in test mode.\n";
    if (argc > 1 && strcmp(argv[1], "-t") == 0){
        std::cout << "Running MyoFInDer in test mode.\n\n";
        test = "-t";
    }
    else {
        std::cout << "Running MyoFInDer in regular mode.\n\n";
        test = "";
    }

    // Starting the myofinder module using the dedicated Python interpreter
    std::string myofinder_cmd = "\"" + python_exe_path + "\"" + " -m myofinder " + test;
    std::cout << "Command to run: " + myofinder_cmd + "\n";
    if (argc > 1 && strcmp(argv[1], "-t") == 0){
        std::cout << "Starting MyoFInDer in test mode.\n\n";
    }
    else {
        std::cout << "Starting MyoFInDer.\n\n";
    }
    run_cmd((char*) myofinder_cmd.data(), CREATE_NEW_CONSOLE);

    return 0;
}
