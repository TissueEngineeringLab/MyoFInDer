#include <windows.h>
#include <iostream>
#include <string>
#include "run_cmd.cpp"
#include "logger.cpp"

// Helper function to check if a file exists
static int file_exists(const std::string& path) {
    DWORD attrs = GetFileAttributesA(path.c_str());
    if (attrs == INVALID_FILE_ATTRIBUTES) {
        return 0;
    }
    return (attrs & FILE_ATTRIBUTE_DIRECTORY) ? 0 : 1;
}

int main(int argc, char* argv[]) {

    // Create a logger for the install verification checks
    Logger log = make_logger("verify_install.log");
    log << "\n=== MyoFInDer verify_install starting ===\n";
    log << "Log file: " << log.path() << "\n";

    // Check that enough arguments were provided
    if (argc < 3) {
        log << "ERROR: Not enough arguments. Expected: <venv_python_path> <install_dir>\n";
        return 2;
    }

    std::string venv_python_path = argv[1];
    std::string install_dir = argv[2];

    log << "Venv python: \"" << venv_python_path << "\"\n";
    log << "Install dir: \"" << install_dir << "\"\n\n";

    // Check that the Python venv exists
    log << "[1/3] Checking venv python exists...\n";
    if (!file_exists(venv_python_path)) {
        log << "ERROR: venv python not found at: " << venv_python_path << "\n";
        return 10;
    }
    log << "OK.\n\n";

    // Import myofinder
    log << "[2/3] Verifying `import myofinder`...\n";
    std::string import_cmd =
        "\"" + venv_python_path + "\" -c \"import myofinder,sys; sys.exit(0)\"";
    int rc = run_cmd(import_cmd, 0);
    log << "Exit code: " << rc << "\n\n";
    if (rc != 0) {
        log << "ERROR: `import myofinder` failed.\n";
        return 20;
    }

    // Verify module entrypoint at least responds
    log << "[3/3] Verifying `python -m myofinder --help`...\n";
    std::string help_cmd =
        "\"" + venv_python_path + "\" -m myofinder --help";
    rc = run_cmd(help_cmd, 0);
    log << "Exit code: " << rc << "\n\n";
    if (rc != 0) {
        log << "ERROR: `python -m myofinder --help` failed.\n";
        return 30;
    }

    log << "SUCCESS: verification passed.\n";
    return 0;
}