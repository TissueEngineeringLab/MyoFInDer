#include <shlwapi.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include "run_cmd.cpp"
#include "read_register.cpp"

/*
The main function run by the myofinder.exe executable. It reads the path to the
Python executable from the registry, checks if MyoFInDer should start in test
mode, and finally launches MyoFInDer.
*/
int main(int argc, char* argv[]){

    // Putting the arguments into a vector for convenience
    std::vector<std::string> args(argv, argv+argc);

    // Retrieving the path to the Python executable of MyoFInDer
    std::string python_exe_path = read_reg(HKEY_CURRENT_USER, "SOFTWARE\\MyoFInDer", "MyoFInDerPythonPath");
    std::cout << "Python executable path: \"" + python_exe_path + "\"\n";

    // Retrieving the path to the installation directory of MyoFInDer
    std::string install_dir = read_reg(HKEY_CURRENT_USER, "SOFTWARE\\MyoFInDer", "MyoFInDerInstallDir");
    std::cout << "Installation directory: \"" + install_dir + "\"\n\n";

    // String containing the application folder argument to pass to MyoFInDer
    std::string app_dir_arg = " --app-folder \"" + install_dir + "\"";

    // Checking if the myofinder module should be started in test mode, and
    // setting the suffix to add to the Python command to execute
    std::string test_arg;
    int test;
    std::cout << "Checking if MyoFInDer should run in test mode.\n";
    if (std::find(args.begin(), args.end(), "--test") != args.end() ||
        std::find(args.begin(), args.end(), "-t") != args.end()){
        std::cout << "Running MyoFInDer in test mode.\n\n";
        test = 1;
        test_arg = " --test";
    }
    else {
        std::cout << "Running MyoFInDer in regular mode.\n\n";
        test = 0;
        test_arg = "";
    }

    // Starting the myofinder module using the dedicated Python interpreter
    std::string myofinder_cmd = "\"" + python_exe_path + "\"" + " -m myofinder" + test_arg + app_dir_arg;
    std::cout << "Command to run: " + myofinder_cmd + "\n";
    if (test){
        std::cout << "Starting MyoFInDer in test mode.\n\n";
    }
    else {
        std::cout << "Starting MyoFInDer.\n\n";
    }
    // No new console in test mode, so that GitHub Actions can display the log
    run_cmd((char*) myofinder_cmd.data(), test ? 0 : CREATE_NEW_CONSOLE);

    return 0;
}
