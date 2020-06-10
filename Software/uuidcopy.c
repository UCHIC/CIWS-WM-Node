#include <stdlib.h>
#include <stdio.h>

/****************************************************\
|****************************************************|
|* uuidcopy is a program used to copy the field     *|
|* "root=PARTUUID=" in the file "/boot/cmdline.txt" *|
|* from the originally flashed file to the modified *|
|* file. This field can change from installation to *|
|* installation; therefore, the field cannot be     *|
|* pre-filled like the others. This program is run  *|
|* by setup.sh, and should not be run by the user.  *|
|****************************************************|
\****************************************************/

void uuidCopy(void);

int main()									// Main Function
{
	uuidCopy();									// Call uuidCopy()

	return 0;									// End program
}

void uuidCopy(void)								// uuidCopy Function
{
	char uuid[100];									// Allocate a string to store fields from cmdline.txt. This is where the uuid will be stored once found.
	char target[] = "root=PARTUUID=";						// The string "target" will be compared to different fields in cmdline.txt until a match is found,
											// identifiying the field with the uuid.
	FILE* cmdline_original;
	FILE* cmdline_temp;
	FILE* cmdline;
											// Open files:
	cmdline_original = fopen("/boot/cmdline.txt.original", "r");			// The original cmdline.txt from the installation. Gets renamed to cmdline.txt.original by setup.sh
	cmdline_temp = fopen("/boot/cmdline.tmp", "w");					// The new cmdline.txt is originally written to cmdline.tmp, which will be renamed to cmdline.txt.
	cmdline = fopen("/boot/cmdline.txt", "r");					// The modified cmdline.txt without the "root=PARTUUID=", with the modifications needed to run the datalogger software

	while(fscanf(cmdline_original, "%s", uuid) != EOF)				// While the end of cmdline.txt.original has not yet been reached:
	{
		int i;
		int matched = 1;								// Store a field from cmdline.txt.original into uuid
		for(i = 0; i < 14; i++)								// for the length of target[]
		{
			if(uuid[i] != target[i])							// if a character in uuid does not match target:
			{
				matched = 0;									// Mark that the fields do not match
				break;										// Break out of the for loop.
			}
		}
		if(matched)									// if the fields match
		{
			break;										// Break out of the while loop
		}
	}

	printf("PARTUUID: %s\n", uuid);							// Print uuid

	int ch;
	for(;;)										// Loop until a newline is encountered
	{
		int ch = fgetc(cmdline);							// Read a character from cmdline.txt
		if(ch =='\n' || ch == EOF)							// If the character is a newline or End-Of-File (EOF):
		{
			fputc(' ', cmdline_temp);							// Add a space to cmdline.tmp
			fputs(uuid, cmdline_temp);							// Print the uuid to cmdline.tmp
			fputc('\n', cmdline_temp);							// Add a newline to cmdline.tmp
			break;										// Break out of the loop
		}
		fputc(ch, cmdline_temp);							// Copy the character from cmdline.txt to cmdline.tmp
	}

	fclose(cmdline_original);							// Close all of the files
	fclose(cmdline_temp);
	fclose(cmdline);
	remove("/boot/cmdline.txt");							// Remove cmdline.txt
	rename("/boot/cmdline.tmp", "/boot/cmdline.txt");				// Rename cmdline.tmp to cmdline.txt

	return;										// Return to Main Function
}
