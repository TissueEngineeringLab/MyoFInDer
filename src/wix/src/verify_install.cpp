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

// Helper function to remove the last extension from a path
static std::string strip_extension(const std::string& path) {
    const size_t slash = path.find_last_of("\\/");
    const size_t dot = path.find_last_of('.');
    if (dot == std::string::npos) return path;
    if (slash != std::string::npos && dot < slash) return path; // dot is in a directory name
    return path.substr(0, dot);
}

int main(int argc, char* argv[]) {

    // Create a logger for the install verification checks
    Logger log = make_logger("verify_install.log");
    log << "\n=== MyoFInDer verify_install starting ===\n";
    log << "Log file: " << log.path() << "\n";

    // Check that enough arguments were provided
    if (argc < 3) {
        log << "ERROR: Not enough arguments. Expected: <venv_python_path> <venv_root>\n";
        return 2;
    }

    std::string venv_python_path = argv[1];
    std::string venv_root = argv[2];

    log << "Venv python: \"" << venv_python_path << "\"\n";
    log << "Install dir: \"" << venv_root << "\"\n\n";

    // Check that the Python venv exists
    log << "[1/3] Checking venv python exists...\n";
    if (!file_exists(venv_python_path)) {
        log << "ERROR: venv python not found at: " << venv_python_path << "\n";
        return 10;
    }
    log << "OK.\n\n";

    // Import myofinder
    log << "[2/3] Verifying `import myofinder`...\n";
    std::string import_out = strip_extension(log.path()) + "_import.log";
    log << "Capturing stdout/stderr to: " << import_out << "\n";

    // Command that redirects logs to a separate file
    std::string import_cmd =
        "cmd.exe /C \"\""
        + venv_python_path
        + "\" -X faulthandler -c \"import myofinder\" > \""
        + import_out
        + "\" 2>&1\"";

    int rc = run_cmd(import_cmd, 0, venv_root);
    log << "Exit code: " << rc << "\n\n";
    if (rc != 0) {
        log << "ERROR: `import myofinder` failed. See: " << import_out << "\n";
        return 20;
    }

    // Verify module entrypoint at least responds
    log << "[3/3] Verifying `python -m myofinder --help`...\n";
    std::string help_out = strip_extension(log.path()) + "_help.log";
    log << "Capturing stdout/stderr to: " << help_out << "\n";

    // Command that redirects logs to a separate file
    std::string help_cmd =
        "cmd.exe /C \"\""
        + venv_python_path
        + "\" -X faulthandler -m myofinder --help > \""
        + help_out
        + "\" 2>&1\"";

    rc = run_cmd(help_cmd, 0, venv_root);
    log << "Exit code: " << rc << "\n\n";
    if (rc != 0) {
        log << "ERROR: `python -m myofinder --help` failed. See: " << help_out << "\n";
        return 30;
    }

    log << "SUCCESS: verification passed.\n";
    return 0;
}
