#include <iostream>
#include <fstream>
#include "run_cmd.cpp"

/* This executable is called when the user enters a DeepCell API token in the
installation interface, and then clicks on the Next button. The value entered
as the token is then simply saved to a text file.
*/
int main(int argc, char* argv[]){

    // The path to the token file and the token are passed as arguments
    std::string installation_folder = argv[1];
    std::string token_path = argv[2];
    std::string token = argv[3];
    std::cout << "Installation folder path: \"" << installation_folder << "\"\n";
    std::cout << "Token file path: \"" << token_path << "\"\n\n";

    // Trying to create the installation folder if it does not already exist
    std::string create_folder_cmd = "cmd.exe /C if not exist \"" + installation_folder + "\" mkdir \"" + installation_folder + "\"";
    if (!run_cmd((char*) create_folder_cmd.data(), 0)){
        std::cout << "Successfully created the installation directory.\n\n";
    }
    else {
        std::cout << "Something went wrong while creating the installation directory!\n\n";
        system("pause");
        return 1;
    }

    // Trying to save the token using fstream
    std::ofstream token_file(token_path);
    token_file << token << std::endl;
    token_file.close();
    std::cout << "Successfully wrote token to token file.\n\n";

    system("pause");

    return 0;
}
