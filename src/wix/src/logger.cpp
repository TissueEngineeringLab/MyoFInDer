#include <windows.h>
#include <fstream>
#include <string>
#include <iostream>

// Creates a directory in the temporary folder where to store the logs
static std::string make_temp_dir_myofinder() {
    char tempPath[MAX_PATH];
    DWORD n = GetTempPathA(MAX_PATH, tempPath);
    if (n == 0 || n > MAX_PATH) {
        return std::string(".\\");
    }
    std::string dir = std::string(tempPath) + "MyoFInDer\\";
    CreateDirectoryA(dir.c_str(), NULL);
    return dir;
}

// Logger class handling writing in the logging folder
class Logger {
public:
    explicit Logger(const std::string& path)
        : path_(path), f_(path.c_str(), std::ios::app) {}

    // The path to the temporary folder where logs are written
    const std::string& path() const { return path_; }

    // Defines the << operator to write to the logger
    template <typename T>
    Logger& operator<<(const T& v) {
        std::cout << v;
        if (f_.is_open()) {
            f_ << v;
            f_.flush();
        }
        return *this;
    }

    // Handles << with iostream operators instead of strings
    typedef std::ostream& (*Manip)(std::ostream&);
    Logger& operator<<(Manip m) {
        m(std::cout);
        if (f_.is_open()) {
            m(f_);
            f_.flush();
        }
        return *this;
    }

private:
    std::string path_;
    std::ofstream f_;
};

// Creates a Logger object for writing logs in the temporary folder
static Logger make_logger(const char* leafName) {
    std::string dir = make_temp_dir_myofinder();
    std::string path = dir + leafName;
    Logger log(path);
    return log;
}