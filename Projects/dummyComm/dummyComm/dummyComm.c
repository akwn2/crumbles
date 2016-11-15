/* Header files */
#include <stdio.h>
#include <stdlib.h>

/* Function prototypes */
void defineFunction(void);
void evaluateFunction(void);


int main(int argc, char* argv[]) {
	char control = 'Z';

	/* Main communication loop */
	scanf(" %c", &control);
	while (control != 'Q'){
		if (control == 'D'){
			/*printf("Function definition (%c): (num of chars and then string)\n",control);*/
			defineFunction();
		}
		if (control == 'C'){
			/*printf("Function evaluation (%c): (num of chars and then string)\n",control);*/
			evaluateFunction();
		}
		scanf(" %c", &control);
	}
	/*printf("\"All's well that ends well\" - William Shakespeare\n");*/
	getchar();
	return 0;
}

void defineFunction(){
/************************************************************
	defineFunction
	
	This function aims to create an instance of the function
	defined in the funcString in the Mathkernel for later
	evaluation.
************************************************************/
	int size = -1;
	char * funcString;
	
	/************************************************************
		All messages received for defining functions are strings.
		Thus, since C does not handle strings easily, it is needed
		to implement the protocol below:
		1.) Obtain string length,
		2.) Allocate memory for string,
		3.) Get function string,
		4.) Send it to MathKernel
		5.) Free allocated memory (all used already).
	************************************************************/

	/* Step 1 */
	scanf(" %d", &size);
	getchar(); /* Removes "\n" character */
	/* To check: */
	/* printf("%d \n", size); */

	/* Step 2 */
	funcString = (char*)malloc(size + 1);

	/* Step 3 */
	scanf("%[^\n]", funcString);
	free(funcString);
}

void evaluateFunction(){
/************************************************************
	defineFunction
	
	This function aims to create an instance of the function
	defined in the funcString in the Mathkernel for later
	evaluation.
************************************************************/
	int size = -1;
	int i = 0;
	char * funcString;
	char * name;

	/************************************************************
		All messages received for defining functions are strings.
		Thus, since C does not handle strings easily, it is needed
		to implement the protocol below:
		1.) Obtain string length,
		2.) Allocate memory for string,
		3.) Get function string,
		4.) Send it to MathKernel
		5.) Free allocated memory (all used already).
	************************************************************/

	/* Step 1 */
	scanf(" %d", &size);
	getchar(); /* Removes "\n" character */
	/* To check: */
	/* printf("%d \n", size); */

	/* Step 2 */
	funcString = (char*)malloc(size + 1);

	/* Step 3 */
	scanf("%[^\n]", funcString);
	/* To check: */
	/* printf("%s\n", funcString); */

	name = (char*)malloc(size + 1 - 4);
	
	for (i = 0; i < (size + 1 - 4); i++){
		name[i] = funcString[i + 2];
		printf("%c",name[i]);
	}
	printf("\n");
	fflush(stdout);
	
	/* Step 4 */
	free(funcString);
	free(name);
}