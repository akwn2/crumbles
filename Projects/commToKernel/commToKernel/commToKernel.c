/* Header files */
#include <stdio.h>
#include <stdlib.h>
#include "mathlink.h"

/* Function prototypes */
static void init_and_openlink( int argc, char* argv[]);
static void error( MLINK lp);
void defineFunction(MLINK lp);
void evaluateFunction(MLINK lp);

MLENV ep = (MLENV)0;
MLINK lp = (MLINK)0;


int main(int argc, char* argv[]) {
	
	int arguments = 4;
	char* options[] = {"-linkname","\"C:\\Program Files\\Wolfram Research\\Mathematica\\8.0\\MathKernel.exe\"","-linklaunch", NULL};
	char control = 'Z';

	/* Initialize and open link */
	init_and_openlink(arguments, options);

	/* Main communication loop */
	printf("Aguardando operacao:\n");
	scanf(" %c", &control);
	while (control != 'Q'){
		if (control == 'D'){
			/*printf("Function definition (%c): (num of chars and then string)\n",control);*/
			defineFunction(lp);
		}
		if (control == 'E'){
			/*printf("Function evaluation (%c): (num of chars and then string)\n",control);*/
			evaluateFunction(lp);
		}
		printf("Aguardando operacao:\n");
		scanf(" %c", &control);
	}
	/* Exiting Mathkernel */
	MLPutFunction(lp, "Exit", 0);
	printf("\"All's well that ends well\" - William Shakespeare\n");
	getchar();
	return 0;
}


static void error(MLINK lp){
/* This is a standard Mathlink function */

	if(MLError(lp))
		fprintf(stderr, "Error detected by MathLink: %s.\n", MLErrorMessage(lp));
	else
		fprintf( stderr, "Error detected by this program.\n");
	exit(3);
}


static void deinit(void){
/* This is a standard Mathlink function */

	if(ep)
		MLDeinitialize(ep);
}


static void closelink(void){
/* This is a standard Mathlink function */

	if(lp)
		MLClose(lp);
}


static void init_and_openlink(int argc, char* argv[]){
/* This is a standard Mathlink function */

#if MLINTERFACE >= 3
	int err;
#else
	long err;
#endif /* MLINTERFACE >= 3 */

	ep = MLInitialize((MLParametersPointer)0);
	
	if(ep == (MLENV)0)
		exit(1);

	atexit( deinit);

#if MLINTERFACE < 3
	lp = MLOpenArgv( ep, argv, argv + argc, &err);
#else
	lp = MLOpenArgcArgv( ep, argc, argv, &err);
#endif
	if(lp == (MLINK)0)
		exit(2);
	atexit( closelink);	
}

void defineFunction(MLINK lp){
/************************************************************
	defineFunction
	
	This function aims to create an instance of the function
	defined in the funcString in the Mathkernel for later
	evaluation.
************************************************************/
	int pkt  = -1;
	int size = -1;
	char * funcString;
	char * inputPktString;
	
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

	/* Step 4 */
	MLPutFunction(lp, "EnterTextPacket", 1);
		MLPutString(lp, funcString);
	MLEndPacket(lp);
	
	/* Step 5 */
	free(funcString);

	/* Deal with Packets Received from MathKernel */
	pkt = MLNextPacket( lp);
	while( pkt && pkt != INPUTNAMEPKT ) {
		/*printf("pkt = %d\n",pkt);*/
		MLNewPacket(lp);
		if (MLError(lp))
			error(lp);
		pkt = MLNextPacket( lp);
	}

	/* Flush residual string */
	MLGetString(lp, &inputPktString);
	MLReleaseString(lp, inputPktString);
}

void evaluateFunction(MLINK lp){
/************************************************************
	defineFunction
	
	This function aims to create an instance of the function
	defined in the funcString in the Mathkernel for later
	evaluation.
************************************************************/
	int pkt  = -1;
	int size = -1;
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

	/* Step 4 */
	MLPutFunction(lp, "EvaluatePacket", 1);
		MLPutFunction(lp, "ToString", 1);
			MLPutFunction(lp, "ToExpression", 1);
				MLPutString(lp, funcString);
	MLEndPacket(lp);
	
	/* Step 5 */
	free(funcString);

	/* Deal with Packets Received from MathKernel */
	pkt = MLNextPacket(lp);

	while(pkt && pkt != RETURNPKT) {
		MLNewPacket(lp);
		if (MLError(lp))
			error(lp);
		pkt = MLNextPacket(lp);
	}

	/* Deal appropriately with results */
	if (MLGetType(lp) == MLTKSTR){
		MLGetString(lp, &name);
		printf("%s\n",name);
		MLReleaseString(lp, name);
	}
	else {
		printf("I have a bad feeling about this!\n");
		printf("None of the standard types matched!\n");
	}
}


/************************************************************
Code Repository
Things that I wrote at some point, mostly for testing and
learning that could be reused later at some point...

Maybe.
************************************************************/

/************************************************************

Previous version of evaluateFunction before output was changed
to be only strings;

void evaluateFunction(MLINK lp){
/************************************************************
	defineFunction
	
	This function aims to create an instance of the function
	defined in the funcString in the Mathkernel for later
	evaluation.
************************************************************
	int pkt = -1;
	int size = 0;
	char * funcString;
	char * name;
	int n, k, args;
	double x = 0.0;

	/************************************************************
		All messages received for defining functions are strings.
		Thus, since C does not handle strings easily, it is needed
		to implement the protocol below:
		1.) Obtain string length,
		2.) Allocate memory for string,
		3.) Get function string,
		4.) Send it to MathKernel
		5.) Free allocated memory (all used already).
	************************************************************

	// Step 1
	scanf(" %d", &size);
	getchar(); // Removes "\n" character
	// To check:
	// printf("%d \n", size);

	// Step 2
	funcString = (char*)malloc(size + 1);

	// Step 3
	scanf("%[^\n]", funcString);
	// To check:
	// printf("%s\n", funcString);

	// Step 4
	MLPutFunction(lp, "EvaluatePacket", 1);
		MLPutFunction(lp, "ToString", 1);
			MLPutFunction(lp, "ToExpression", 1);
				MLPutString(lp, funcString);
	MLEndPacket(lp);
	
	// Step 5
	free(funcString);

	// Deal with Packets Received from MathKernel
	pkt = MLNextPacket(lp);

	while(pkt && pkt != RETURNPKT) {
		MLNewPacket(lp);
		if (MLError(lp))
			error(lp);
		pkt = MLNextPacket(lp);
	}

	// Deal appropriately with results
		switch(MLGetType(lp)){

		case MLTKFUNC:
			printf("It's MLTKFUNC\n");
			MLGetArgCount(lp,&n);
			printf("Num. args.: %d \n",n);

			for ( k = 0; k < n; k++){
				MLGetFunction(lp, &name, &args);
				printf("  name = %s, args = %d\n", name, args);
				MLReleaseSymbol(lp, name);
			}
			break;

		case MLTKSYM:
			printf("It's MLTKSYM\n");
			MLGetSymbol(lp, &name);
			printf("%s\n",name);
			MLReleaseSymbol(lp, name);
			break;

		case MLTKINT:
			printf("It's MLTKINT\n");
			MLGetInteger(lp, &n);
			break;

		case MLTKREAL:
			printf("It's MLTKREAL\n");
			MLGetDouble(lp, &x);
			printf("Checkpoint: %lf\n",x);
			break;

		case MLTKSTR:
			printf("It's MLTKSTR\n");
			MLGetString(lp, &name);
			printf("%s\n",name);
			MLReleaseString(lp, name);
			break;

		default :
			printf("I have a bad feeling about this!\n");
			printf("None of the standard types matched!\n");
	}
}*/

/************************************************************
	Prototypes for functions that manipulate functions within
	Mathkernel to generate parts that should be evaluated.

	This was discontinued as it was possible to do the same with
	the defineFunction and evaluateFunction with some string
	manipulation in Python and the Mathematica shell, as it is
	more productive to code with strings in those environments.

	Furthermore, it simplifies the communication protocol, as
	this way only two states are possible: define or evaluate.
	This is an advance in the sense that all messaging is done
	within the Python scheduler.

void makeObj(){
/************************************************************
	makeObj
	
	This generates the objetive function (R^n -> R)in
	Mathkernel, then the returning function is compiled
	for later use.
************************************************************ /
}

void makeConstr(){
/************************************************************
	makeConstr
	
	This generates a function of all constraints (R^n->R^m)
	in Mathkernel, then compiles it for later use.
************************************************************ /
}

void makeGradObj(){
/************************************************************
	makeGradObj
	
	This generates the gradient of the objetive in Mathkernel
	through the use of symbolic functions from Mathematica.

	Then the returning function is compiled for later use.
************************************************************ /
}

void makeJacConstr(){
/************************************************************
	makeJacConstr
	
	This generates the Jacobian matrix of the constraints
	through the use of symbolic functions from Mathematica

	Then the returning function is compiled for later use.
************************************************************ /
}

void makeHessian(){
/************************************************************
	makeHessian
	
	This generates the Hessian matrix of the Lagrangean
	through the use of symbolic functions from Mathematica

	Then the returning function is compiled for later use.
************************************************************ /
}
*/

/*	Prints some of MathLink's constants, useful for debuging.
	
	printf("----Type Constants-----\n");
	printf("MLTKFUNC = %d\n", MLTKFUNC);
	printf("MLTKSYM  = %d\n", MLTKSYM);
	printf("MLTKINT  = %d\n", MLTKINT);
	printf("MLTKREAL = %d\n", MLTKREAL);
	printf("MLTKSTR  = %d\n", MLTKSTR);
	printf("------------------------\n");
	printf("\n");
	printf("----Packet Constants----\n");
	printf("RETURNPKT     = %d\n", RETURNPKT);
	printf("RETURNTEXTPKT = %d\n", RETURNTEXTPKT);
	printf("INPUTNAMEPKT  = %d\n", INPUTNAMEPKT);
	printf("OUTPUTNAMEPKT = %d\n", OUTPUTNAMEPKT);
	printf("TEXTPKT       = %d\n", TEXTPKT);
	printf("MESSAGEPKT    = %d\n", MESSAGEPKT);
	printf("INPUTPKT      = %d\n", INPUTPKT);
	printf("CALLPKT       = %d\n", CALLPKT);
	printf("------------------------\n");
*/