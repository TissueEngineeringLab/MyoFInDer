#include <shlwapi.h>
#include <iostream>
#include "run_cmd.cpp"

/* This executable is called during the installation of MyoFInDer, to create
the virtual environment in which the myofinder Python module will run.
*/
int main(int argc, char* argv[]){

    // Retrieving important information from the arguments
    std::string system_python_exe = argv[1];
    std::string venv_path = argv[2];
    std::string venv_python_path = argv[3];
    std::string to_install = argv[4];

    // Printing the values obtained by parsing the arguments
    std::cout << "System Python path: \"" << system_python_exe << "\"\n";
    std::cout << "Virtual environment path: \"" << venv_path << "\"\n";
    std::cout << "Virtual environment Python path: \"" << venv_python_path << "\"\n";
    std::cout << "Package to install: \"" << to_install << "\"\n\n";

    // Creating the virtual environment. If it already exists, it will not be
    // modified.
    std::cout << "Creating the virtual environment.\n";
    std::string venv_cmd = "\"" + system_python_exe + "\"" + " -m venv " + "\"" + venv_path + "\"";
    if (!run_cmd((char*) venv_cmd.data(), 0)){
        std::cout << "Virtual environment successfully created.\n\n";
    }
    else {
        std::cout << "Something went wrong while creating the virtual environment, aborting!\n\n";
        system("pause");
        return 1;
    }

    // Running the command for installing or upgrading the build dependencies
    // of MyoFInDer. If they are already up-to-date, nothing will be modified
    std::cout << "Installing or updating the build dependencies if necessary.\n";
    std::string dependencies_install_cmd = "\"" + venv_python_path + "\"" + " -m pip install --upgrade pip wheel build setuptools";
    if (!run_cmd((char*) dependencies_install_cmd.data(), 0)){
        std::cout << "Dependencies correctly installed in the virtual environment.\n\n";
    }
    else {
        std::cout << "Something went wrong while installing the dependencies, aborting!\n\n";
        system("pause");
        return 1;
    }

    // Running the command for installing MyoFInDer. If it is already
    // installed, nothing more will be installed or downloaded. Otherwise, the
    // missing packages are automatically installed
    std::cout << "Installing or updating MyoFInDer if necessary.\n";
    std::string myofinder_install_cmd = "\"" + venv_python_path + "\"" + " -m pip install " + "\"" + to_install + "\"";
    if (!run_cmd((char*) myofinder_install_cmd.data(), 0)){
        std::cout << "MyoFInDer is correctly installed on the system.\n\n";
    }
    else {
        std::cout << "Something went wrong while installing or updating MyoFInDer, aborting!\n\n";
        system("pause");
        return 1;
    }

    return 0;
}
