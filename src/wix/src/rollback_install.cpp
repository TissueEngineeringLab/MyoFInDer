#include <iostream>
#include <string>
#include "run_cmd.cpp"
#include "logger.cpp"

/* This executable is called when somthing goes wrong with the installation of
the virtual environment, and the whole installation needs to be rolled back. It
simply deletes all the files that might have been created with the virtual
environment, to make sure everything is left clean after rolling back.
*/
int main(int argc, char* argv[]){

    Logger log = make_logger("rollback_install.log");
    log << "\n=== MyoFInDer rollback_install starting ===\n";
    log << "Log file: " << log.path() << "\n";

    // Check that enough arguments were provided
    if (argc < 2) {
        log << "ERROR: Missing venv path argument.\n";
        return 2;
    }

    std::string venv_path = argv[1];
    log << "Virtual environment path: \"" << venv_path << "\"\n\n";

    // Try to delete the virtual environment files using the rmdir command
    std::string delete_venv_cmd =
        "cmd.exe /C if exist \"" + venv_path + "\" rmdir /s /q \"" + venv_path + "\"";
    int rc = run_cmd(delete_venv_cmd, 0);

    log << "Exit code: " << rc << "\n";
    if (rc != 0) {
        log << "ERROR: rollback deletion failed.\n";
        return 10;
    }

    log << "SUCCESS: rollback deletion OK.\n";
    return 0;
}
