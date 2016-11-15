/**********************************************************
dummySolver.c

Generic test program for Crumbles interface.

This program acts like a solver that prompts for function
5 function evaluations of two different Evaluators.
**********************************************************/
#include <stdio.h>

int main(void){

	char control = 'Z';
	int i, j, n = 2;
	double x[3] = {0.00, 1.11, 2.22};

	/* Main control loop*/
	for(i = 0; (i < 5 && control != 'Q'); i++){
		scanf(" %c", &control);

		switch (control) {
			case 'W':
				/* operation: double each value */
				for (j = 0; j < n + 1; j++)
					x[j] = x[j] * 2.0;

				/* print values */
				printf("A\n");
				fflush(stdout);
				printf("%d\n",n + 1);
				fflush(stdout);
				for (j = 0; j < n; j++)
					printf("%lf,", x[j]);
				printf("%lf", x[j]);

				printf("\n");
				fflush(stdout);
				break;

			case 'R':
				/* scan values */
				scanf(" %d",&n);
				getchar();

				n = n - 1;
				for (j = 0; j < n; j++)
					scanf("%lf,", &x[j]);
				scanf("%lf", &x[j]);

				break;
		}
	}
	return 0;
}