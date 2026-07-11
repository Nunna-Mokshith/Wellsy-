#include <windows.h>
#include <iostream>
#include <string>
#include <cstring>

// Structure to return to Python
struct FileMetadata {
    char path[512];
    double mod_time;
    int64_t size;
};

// Recursive Win32 FindFirstFile scanner
int scan_directory_win32(const std::wstring& dir, FileMetadata* results, int max_results, int& count) {
    std::wstring search_path = dir + L"\\*";
    WIN32_FIND_DATAW find_data;
    HANDLE hFind = FindFirstFileW(search_path.c_str(), &find_data);

    if (hFind == INVALID_HANDLE_VALUE) {
        return count;
    }

    do {
        if (count >= max_results) {
            break;
        }

        std::wstring name = find_data.cFileName;
        if (name == L"." || name == L"..") {
            continue;
        }

        std::wstring full_path = dir + L"\\" + name;

        if (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            scan_directory_win32(full_path, results, max_results, count);
        } else {
            // Check suffix
            bool match = false;
            size_t len = name.length();
            if (len > 4) {
                if (name.compare(len - 4, 4, L".txt") == 0 ||
                    name.compare(len - 4, 4, L".pdf") == 0) {
                    match = true;
                } else if (len > 5 && name.compare(len - 5, 5, L".docx") == 0) {
                    match = true;
                }
            }

            if (match && count < max_results) {
                // Convert wstring back to UTF-8 char path
                int size_needed = WideCharToMultiByte(CP_UTF8, 0, full_path.c_str(), -1, results[count].path, 512, NULL, NULL);
                if (size_needed > 0 && size_needed < 512) {
                    results[count].path[size_needed - 1] = '\0';
                    
                    // Convert file time to epoch double
                    ULARGE_INTEGER ull;
                    ull.LowPart = find_data.ftLastWriteTime.dwLowDateTime;
                    ull.HighPart = find_data.ftLastWriteTime.dwHighDateTime;
                    // convert from 100-nanosecond intervals since Jan 1 1601 to unix epoch seconds
                    results[count].mod_time = static_cast<double>(ull.QuadPart - 116444736000000000ULL) / 10000000.0;
                    
                    // File size
                    LARGE_INTEGER fileSize;
                    fileSize.LowPart = find_data.nFileSizeLow;
                    fileSize.HighPart = find_data.nFileSizeHigh;
                    results[count].size = fileSize.QuadPart;

                    count++;
                }
            }
        }
    } while (FindNextFileW(hFind, &find_data));

    FindClose(hFind);
    return count;
}

extern "C" {
    __declspec(dllexport) int scan_directory(const char* dir_path, FileMetadata* results, int max_results) {
        // Convert input UTF-8 path to wide string
        wchar_t w_dir[512];
        int w_size = MultiByteToWideChar(CP_UTF8, 0, dir_path, -1, w_dir, 512);
        if (w_size <= 0) {
            return -1;
        }

        std::wstring start_dir(w_dir);
        int count = 0;
        return scan_directory_win32(start_dir, results, max_results, count);
    }
}
