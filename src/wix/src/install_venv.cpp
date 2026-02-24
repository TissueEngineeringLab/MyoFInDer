#include <shlwapi.h>
#include <iostream>
#include <string>
#include "run_cmd.cpp"
#include "logger.cpp"

/* This executable is called during the installation of MyoFInDer, to create
the virtual environment in which the myofinder Python module will run.
*/
int main(int argc, char* argv[]){

    Logger log = make_logger("install_venv.log");
    log << "\n=== MyoFInDer install_venv starting ===\n";
    log << "Log file: " << log.path() << "\n";

    // Check that enough arguments were provided
    if (argc < 5) {
        log << "ERROR: Not enough arguments (expected 4).\n";
        return 2;
    }

    std::string system_python_exe = argv[1];
    std::string venv_path = argv[2];
    std::string venv_python_path = argv[3];
    std::string to_install = argv[4];

    log << "System Python path: \"" << system_python_exe << "\"\n";
    log << "Virtual environment path: \"" << venv_path << "\"\n";
    log << "Venv Python path: \"" << venv_python_path << "\"\n";
    log << "Package to install: \"" << to_install << "\"\n\n";

    // Put pip logs alongside MyoFInDer log
    std::string log_dir = log.path().substr(0, log.path().find_last_of("\\/") + 1);
    std::string pip_log = log_dir + "pip.log";
    std::string pip_report = log_dir + "pip_report.json";

    // Create venv
    log << "[1/3] Creating virtual environment...\n";
    std::string venv_cmd = "\"" + system_python_exe + "\" -m venv \"" + venv_path + "\"";
    int rc = run_cmd(venv_cmd, 0, "");
    log << "Exit code: " << rc << "\n\n";
    if (rc != 0) {
        log << "ERROR: venv creation failed.\n";
        return 10;
    }

    // Upgrade pip tooling
    log << "[2/3] Installing/upgrading pip tooling...\n";
    std::string deps_cmd =
        "\"" + venv_python_path + "\" -m pip install --upgrade pip wheel build setuptools"
        " --log \"" + pip_log + "\"";
    rc = run_cmd(deps_cmd, 0, venv_path);
    log << "Exit code: " << rc << "\n";
    log << "pip log: " << pip_log << "\n\n";
    if (rc != 0) {
        log << "ERROR: pip tooling bootstrap failed.\n";
        return 20;
    }

    // Install MyoFInDer
    log << "[3/3] Installing/upgrading MyoFInDer...\n";
    std::string install_cmd =
        "\"" + venv_python_path + "\" -m pip install \"" + to_install + "\""
        " --log \"" + pip_log + "\""
        " --report \"" + pip_report + "\"";
    rc = run_cmd(install_cmd, 0, venv_path);
    log << "Exit code: " << rc << "\n";
    log << "pip report: " << pip_report << "\n\n";
    if (rc != 0) {
        log << "ERROR: myofinder install failed.\n";
        return 30;
    }

    log << "SUCCESS: install_venv finished OK.\n";
    return 0;
}
