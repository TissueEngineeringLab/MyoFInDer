#include <shlwapi.h>
#include <iostream>

// Function reading a registry value and returning it.
std::string read_reg(HKEY base_key, LPCSTR subkey, LPCSTR value){

    // Objects needed for performing registry search
    DWORD value_type = REG_SZ;
    HKEY registry_key;
    TCHAR buf[255] = {0};
    DWORD buf_size = sizeof(buf);

    // First, searching for the registry key
    if (RegOpenKeyEx(base_key, subkey, 0, KEY_READ, &registry_key)){
        std::cout << "Something went wrong, couldn't open the registry key: " + std::string(value) + "\nGot error code: " + std::to_string(GetLastError()) + "\n\n";
        system("pause");
        exit(1);
    }

    // Then, searching for the target value at the given key
    if (RegQueryValueEx(registry_key, value, NULL, &value_type, (LPBYTE) buf, &buf_size)){
        std::cout << "Something went wrong, couldn't read the registry value: " + std::string(value) + "\nGot error code: " + std::to_string(GetLastError()) + "\n\n";
        system("pause");
        exit(1);
    }

    return (std::string) buf;
}
