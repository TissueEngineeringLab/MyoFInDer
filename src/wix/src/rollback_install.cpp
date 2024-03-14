#include <iostream>
#include "run_cmd.cpp"

/* This executable is called when somthing goes wrong with the installation of
the virtual environment, and the whole installation needs to be rolled back. It
simply deletes all the files that might have been created with the virtual
environment, to make sure everything is left clean after rolling back.
*/
int main(int argc, char* argv[]){

    // The path to the virtual environment is passed as an argument
    std::string venv_path = argv[1];
    std::cout << "Virtual environment path: \"" << venv_path << "\"\n\n";

    // Trying to delete the virtual environment files using the rmdir command
    std::string delete_venv_cmd = "cmd.exe /C rmdir /s /q \"" + venv_path + "\"";
    if (!run_cmd((char*) delete_venv_cmd.data(), 0)){
        std::cout << "Successfully deleted the virtual environment.\n\n";
    }
    else {
        std::cout << "Something went wrong while deleting the virtual environment!\n\n";
        system("pause");
        return 1;
    }

    return 0;
}
