#include <shlwapi.h>
#include <windows.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <initializer_list>
#include "run_cmd.cpp"
#include "logger.cpp"

// Helper function checking whether the path to a given file exists
static bool file_exists(const std::string& path) {
    DWORD attrs = GetFileAttributesA(path.c_str());
    return (attrs != INVALID_FILE_ATTRIBUTES) &&
            !(attrs & FILE_ATTRIBUTE_DIRECTORY);
}

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
    std::string py_pre_check_out = log_dir + "python_pre_check.log";
    std::string pip_bootstrap_out = log_dir + "pip_bootstrap_stdout.log";
    std::string pip_install_out = log_dir + "pip_install_stdout.log";

    // Run Python viability checks
    log << "[0/3] Run Python pre-check...\n";

    // Check that the selected executable exists
    if (!file_exists(system_python_exe)) {
        log << "ERROR: System Python executable does not exist: " << system_python_exe << "\n";
        return 5;
    }

    std::string pre_check_cmd =
        "cmd.exe /S /C \"\""
        + system_python_exe +
        "\" -X faulthandler -c \""
          "import sys, platform; "
          "import venv, ensurepip; "
          "print('executable:', sys.executable); "
          "print('version_info:', tuple(sys.version_info[:3])); "
          "print('bitness:', platform.architecture()[0]); "
          "ok = ((3,9) <= tuple(sys.version_info[:2]) <= (3,13)); "
          "ok = ok and (platform.architecture()[0] == '64bit'); "
          "sys.exit(0 if ok else 3)"
        "\" > \""
        + py_pre_check_out +
        "\" 2>&1\"";

    int rc = run_cmd(pre_check_cmd, 0, "");
    log << "Exit code: " << rc << "\n";
    log << "Pre-check output: " << py_pre_check_out << "\n\n";

    // Create venv
    log << "[1/3] Creating virtual environment...\n";
    std::string venv_cmd = "\"" + system_python_exe + "\" -m venv \"" + venv_path + "\"";
    rc = run_cmd(venv_cmd, 0, "");
    log << "Exit code: " << rc << "\n\n";
    if (rc != 0) {
        log << "ERROR: venv creation failed.\n";
        return 10;
    }

    // Upgrade pip tooling
    log << "[2/3] Installing/upgrading pip tooling...\n";
    std::string deps_cmd =
        "cmd.exe /S /C \"\""
        + venv_python_path +
        "\" -m pip install --disable-pip-version-check --no-input --progress-bar off "
        "--upgrade pip wheel build setuptools "
        "--log \""
        + pip_log +
        "\" > \""
        + pip_bootstrap_out +
        "\" 2>&1\"";

    rc = run_cmd(deps_cmd, 0, venv_path);
    log << "Exit code: " << rc << "\n";
    log << "pip log: " << pip_log << "\n";
    log << "pip stdout/stderr: " << pip_bootstrap_out << "\n\n";
    if (rc != 0) {
        log << "ERROR: pip tooling bootstrap failed.\n";
        return 20;
    }

    // Install MyoFInDer
    log << "[3/3] Installing/upgrading MyoFInDer...\n";
    std::string install_cmd =
        "cmd.exe /S /C \"\""
        + venv_python_path +
        "\" -m pip install --disable-pip-version-check --no-input --progress-bar off "
        "\""
        + to_install +
        "\" --log \""
        + pip_log +
        "\" --report \""
        + pip_report +
        "\" > \""
        + pip_install_out +
        "\" 2>&1\"";

    rc = run_cmd(install_cmd, 0, venv_path);
    log << "Exit code: " << rc << "\n";
    log << "pip log: " << pip_log << "\n";
    log << "pip report: " << pip_report << "\n";
    log << "pip stdout/stderr: " << pip_install_out << "\n\n";
    if (rc != 0) {
        log << "ERROR: myofinder install failed.\n";
        return 30;
    }

    log << "SUCCESS: install_venv finished OK.\n";
    return 0;
}
