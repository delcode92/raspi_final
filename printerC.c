#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    int printer_fd = open("/dev/ttys008", O_WRONLY | O_NOCTTY);
    if (printer_fd == -1) {
        printf("wkwkwkw");
        perror("Failed to open printer");
        return 1;
    }
    printf("data : %d",printer_fd);
    
    // // Text to print
    const char* text = "Hello, Thermal Printer!\n";
    
    // // Write the text to the printer
    ssize_t bytes_written = write(printer_fd, text, 10000);
    if (bytes_written == -1) {
        perror("Failed to write to printer");
        close(printer_fd);
        return 1;
    }
    
    // // Close the printer
    close(printer_fd);
    printf("Hello, World!");

    return 0;
}
