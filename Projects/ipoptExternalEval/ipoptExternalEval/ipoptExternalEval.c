/* Copyright (C) 2005, 2011 International Business Machines and others.
 * All Rights Reserved.
 * This code is published under the Eclipse Public License.
 *
 * $Id: hs071_c.c 1996 2011-05-05 19:28:44Z andreasw $
 *
 * Authors:  Carl Laird, Andreas Waechter     IBM    2005-08-17
 */

#include "IpStdCInterface.h"
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>

/* Function Declarations */
Bool eval_f(Index n, Number* x, Bool new_x,
            Number* obj_value, UserDataPtr user_data);

Bool eval_grad_f(Index n, Number* x, Bool new_x,
                 Number* grad_f, UserDataPtr user_data);

Bool eval_g(Index n, Number* x, Bool new_x,
            Index m, Number* g, UserDataPtr user_data);

Bool eval_jac_g(Index n, Number *x, Bool new_x,
                Index m, Index nele_jac,
                Index *iRow, Index *jCol, Number *values,
                UserDataPtr user_data);

Bool eval_h(Index n, Number *x, Bool new_x, Number obj_factor,
            Index m, Number *lambda, Bool new_lambda,
            Index nele_hess, Index *iRow, Index *jCol,
            Number *values, UserDataPtr user_data);

Bool intermediate_cb(Index alg_mod, Index iter_count, Number obj_value,
                     Number inf_pr, Number inf_du, Number mu, Number d_norm,
                     Number regularization_size, Number alpha_du,
                     Number alpha_pr, Index ls_trials, UserDataPtr user_data);

/* This is an example how user_data can be used. */
struct MyUserData
{
  Number g_offset[2]; /* This is an offset for the constraints.  */
};

/* Main Program */
int main(void) {
  Index n=-1;                          /* number of variables */
  Index m=-1;                          /* number of constraints */
  Number* x_L = NULL;                  /* lower bounds on x */
  Number* x_U = NULL;                  /* upper bounds on x */
  Number* g_L = NULL;                  /* lower bounds on g */
  Number* g_U = NULL;                  /* upper bounds on g */
  IpoptProblem nlp = NULL;             /* IpoptProblem */
  enum ApplicationReturnStatus status; /* Solve return code */
  Number* x = NULL;                    /* starting point and solution vector */
  Number* mult_g = NULL;               /* constraint multipliers at the solution */
  Number* mult_x_L = NULL;             /* lower bound multipliers at the solution */
  Number* mult_x_U = NULL;             /* upper bound multipliers at the solution */
  Number obj = 0.0;                    /* objective value */
  Index nele_jac = -1;                 /* Nonzeros in the Jacobian of the constraints */
  Index nele_hess = -1;                /* Nonzeros in the Hessian of the Lagrangian (block triangular part)*/
  Index i = -1;                        /* Generic counter */
  Index index_style = 0;               /* Indexing in C-style; start at 0 */
  char control = 'Z';                  /* Control key for I/O operations*/
  
  /**************************************************/
  /* I/O Keys - Reference Table*/
  /**************************************************/
  /*   'Z' Initialization*/
  /*   'R' Read mode, read from stdio*/
  /*   'W' Write mode, write in stdio*/
  /*   'L' End of message / Lock again*/
  /*   'Q' Quit*/
  /**************************************************/
  /*    Other keys used to signal function requests*/
  /*   'I' receive initial problem information*/
  /*   'O' dispatch final solution*/
  /*   'F' eval_f */
  /*   'D' eval_grad_f*/
  /*   'G' eval_g/
  /*   'J' eval_jac_g*/
  /*   'H' eval_h*/
  /*   'E' Error*/
  /*   'U' Undefined, to be handled in Python*/
  /**************************************************/

  /* Get problem basic information from I/O */
  printf("I\n");
  printf("0\n");

  do {  
	/* I/O control */
    scanf(" %c",&control);

	if (control == 'R') {
	  /* number, bounds and initial estimate of the primal variables */
      scanf(" %d", &n);

      x   = (Number*)malloc(sizeof(Number)*n);
      x_L = (Number*)malloc(sizeof(Number)*n);
      x_U = (Number*)malloc(sizeof(Number)*n);

      for (i = 0; i < n; i++) {
        scanf(" %lf", x[i]);
        scanf(" %lf", x_L[i]);
        scanf(" %lf", x_U[i]);
      }

      /* number and bounds on constraints */
      scanf(" %d", &m);
      g_L = (Number*)malloc(sizeof(Number)*n);
      g_U = (Number*)malloc(sizeof(Number)*n);
      for (i = 0; i < m; i++) {
        scanf(" %lf", g_L[i]);
        scanf(" %lf", g_U[i]);
      }
	  /* Nonzeros in the Jacobian and Hessian */
      scanf(" %d", &nele_jac);
      scanf(" %d", &nele_hess);
    }
  } while(control != 'L');

  /* create the IpoptProblem */
  nlp = CreateIpoptProblem(n, x_L, x_U, m, g_L, g_U, nele_jac, nele_hess,
                           index_style, &eval_f, &eval_g, &eval_grad_f,
                           &eval_jac_g, &eval_h);

  /* We can free the memory now - the values for the bounds have been
     copied internally in CreateIpoptProblem */
  free(x_L);
  free(x_U);
  free(g_L);
  free(g_U);

  /* allocate space to store the bound multipliers at the solution */
  mult_g   = (Number*)malloc(sizeof(Number)*m);
  mult_x_L = (Number*)malloc(sizeof(Number)*n);
  mult_x_U = (Number*)malloc(sizeof(Number)*n);

  /* Set some options.  Note the following ones are only examples,
     they might not be suitable for your problem. */
  AddIpoptNumOption(nlp, "tol", 1e-7);
  AddIpoptStrOption(nlp, "mu_strategy", "adaptive");
  AddIpoptStrOption(nlp, "output_file", "ipopt.out");

  /* Warmstart options
  AddIpoptStrOption(nlp, "warm_start_init_point", "yes");
  AddIpoptNumOption(nlp, "bound_push", 1e-5);
  AddIpoptNumOption(nlp, "bound_frac", 1e-5);
  */
  /* Solve the problem*/
  status = IpoptSolve(nlp, x, NULL, &obj, mult_g, mult_x_L, mult_x_U, NULL);

  if (status == Solve_Succeeded) {
    scanf(" %c",&control);

    do {
	    /* I/O control */
        scanf(" %c", &control);

	  if (control == 'W') {
		
		/* operation to scheduler*/
		printf("O\n");

  	    /* number, bounds and initial estimate of the primal variables */
        printf(" %d\n", 3 * n + m + 1);

        for (i = 0; i < n; i++) {
          printf(" %lf\n", x[i]);
          printf(" %lf\n", mult_x_L[i]);
          printf(" %lf\n", mult_x_U[i]);
        }

	    /* number and bounds on constraints */
        for (i = 0; i < m; i++)
          scanf(" %lf", mult_g[i]);
        
	    /* Objective value */
        printf(" %lf\n", obj);

      }
    } while(control != 'W');
  }
  else {
    printf("E\n");
    printf("0\n");
  }

  /* free remaining allocated memory */
  FreeIpoptProblem(nlp);
  free(x);
  free(mult_g);
  free(mult_x_L);
  free(mult_x_U);

  return (int)status;
}


/* Function Implementations */
Bool eval_f(Index n, Number* x, Bool new_x,
            Number* obj_value, UserDataPtr user_data)
{
  Index i = -1;       /* Generic counter */
  Index check = -1;   /* Assert check */
  char control = 'Z'; /* IO control */

  do {
	scanf(" %d", &control);

	if(control == 'W') {
	  printf("F\n");
	  printf("%d\n", n);
      for(i = 0; i < n; i++)
	    printf("%lf\n", x[i]);
	}

    if(control == 'R') {
	  scanf(" %d", &check);
	  assert(check == 1);
      scanf(" %lf",obj_value);
	}

  } while(control != 'L');

  return TRUE;
}

Bool eval_grad_f(Index n, Number* x, Bool new_x,
                 Number* grad_f, UserDataPtr user_data)
{
  Index i = -1;       /* Generic counter */
  Index check = -1;   /* Assert check */
  char control = 'Z'; /* IO control */

  do {
	scanf(" %d", &control);
	
	if(control == 'W') {
	  
	  printf("D\n");
	  printf("%d\n", n);

      for(i = 0; i < n; i++)
	    printf(" %lf\n", x[i]);
	}

	if(control == 'R'){

	  scanf(" %d",&check);

	  assert(check == n);
      
	  for(i = 0; i < n; i++)
	    scanf(" %lf", &grad_f[i]);
	}

  } while(control != 'L');

  return TRUE;
}

Bool eval_g(Index n, Number* x, Bool new_x,
            Index m, Number* g, UserDataPtr user_data)
{
  Index i = -1;       /* Generic counter */
  Index check = -1;   /* Assert check */
  char control = 'Z'; /* IO control */
  
  do {
	scanf(" %d", &control);
	
	if(control == 'W') {
	  
	  printf("G\n");
	  printf("%d\n", n);

      for(i = 0; i < n; i++)
	    printf(" %lf\n", x[i]);
	}

	if(control == 'R'){

	  scanf(" %d",&check);

	  assert(check == m);
      
	  for(i = 0; i < m; i++)
	    scanf(" %lf", &g[i]);
	}

  } while(control != 'L');

  return TRUE;
}

Bool eval_jac_g(Index n, Number *x, Bool new_x,
                Index m, Index nele_jac,
                Index *iRow, Index *jCol, Number *values,
                UserDataPtr user_data)
{
  Index i = -1;       /* Generic counter */
  Index check = -1;   /* Assert check */
  char control = 'Z'; /* IO control */

  if (values == NULL) {
    /* return the structure of the jacobian */
	do {
      scanf(" %d", &control);

	  if(control == 'R'){
	    scanf(" %d",&check);
  	    assert(check == 2 * nele_jac);
        for(i = 0; i < nele_jac; i++){
          scanf(" %d", &iRow[i]);
          scanf(" %d", &jCol[i]);
        }
  	  }
    } while(control != 'L');
  }
  else {
    /* return the values of the jacobian of the constraints */
    do {
	  scanf(" %d", &control);
	
	  if(control == 'W') {
	  
	    printf("J\n");
	    printf("%d\n", n);

        for(i = 0; i < n; i++)
	      printf(" %lf\n", x[i]);
	  }

	  if(control == 'R'){
	
	    scanf(" %d",&check);

	    assert(check == nele_jac);
      
	    for(i = 0; i < nele_jac; i++)
	      scanf(" %lf", &values[i]);
	  }
    } while(control != 'L');
  }

  return TRUE;
}

Bool eval_h(Index n, Number *x, Bool new_x, Number obj_factor,
            Index m, Number *lambda, Bool new_lambda,
            Index nele_hess, Index *iRow, Index *jCol,
            Number *values, UserDataPtr user_data)
{
  Index i = -1;       /* Generic counter */
  Index check = -1;   /* Assert check */
  char control = 'Z'; /* IO control */

  if (values == NULL) {
    do{
	  scanf(" %c", &control);

	  if(control == 'R'){

	    scanf(" %d",&check);
  	    assert(check == 2 * nele_hess);

        for (i = 0; i < nele_hess; i++){
            scanf(" %d", &iRow[i]);
            scanf(" %d", &jCol[i]);
        }
	  }
    } while(control != 'L');
  }
  else {
        /* return the values of the modified hessian of the Lagrangean */
    do {
	  scanf(" %d", &control);
	
	  if(control == 'W') {
	  
	    printf("H\n");
	    printf("%d\n", n);

        for(i = 0; i < n; i++)
	      printf(" %lf\n", x[i]);
	  }

	  if(control == 'R') {
	
	    scanf(" %d",&check);

	    assert(check == nele_hess);
      
	    for(i = 0; i < nele_hess; i++)
	      scanf(" %lf", &values[i]);
	  }
    } while(control != 'L');
  }

  return TRUE;
}

Bool intermediate_cb(Index alg_mod, Index iter_count, Number obj_value,
                     Number inf_pr, Number inf_du, Number mu, Number d_norm,
                     Number regularization_size, Number alpha_du,
                     Number alpha_pr, Index ls_trials, UserDataPtr user_data)
{
  printf("Testing intermediate callback in iteration %d\n", iter_count);
  if (inf_pr < 1e-4) return FALSE;

  return TRUE;
}
