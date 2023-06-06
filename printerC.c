#include <stdio.h>
#include <string.h>

// Function to send data to the printer
void sendToPrinter(const char* data) {
    FILE* printer = fopen("/dev/usb/lp0", "w");  // Replace "/dev/usb/lp0" with your printer device

    if (printer == NULL) {
        printf("Failed to open the printer.\n");
        return;
    }

    fprintf(printer, "%s", data);
    fclose(printer);
}

int main() {
    char userInput[] = "cempaka \n metro karya \n ------------------------------------\n\n gate:1  \n motor \n";

    printf("Enter text to print: ");
    // fgets(userInput, sizeof(userInput), stdin);

    // Remove newline character from user input
    // userInput[strcspn(userInput, "\n")] = '\0';

    // ESC/POS commands to print user input in bold and large font size
    char escpos[512];
    snprintf(escpos, sizeof(escpos), "\x1B\x21\x08%s\n", userInput);  // Modify the ESC/POS commands based on your printer capabilities

    sendToPrinter(escpos);

    printf("Printing complete.\n");

    return 0;
}
