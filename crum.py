''' Crumbles.py

    A distributed environment for optimization by Alexandre K. W. Navarro.
    Version 0.1.4 - 05/12/2012 - for Python 2.7.3
'''

import subprocess
import Queue

# Communication protocol constants.
SOLVE_READ_UNLOCK   = 'R'
SOLVE_WRITE_UNLOCK  = 'W'
EVAL_DEFINE_UNLOCK  = 'D'
EVAL_COMPUTE_UNLOCK = 'C'
QUIT_KEY            = 'Q'

# Internal constants
SOLVER_KEY          = 'S'
EVALUATOR_KEY       = 'E'

class Solver(object):
    SolverProcId = 0

    def __init__(self, path, evaluatorsDict):
        '''__init__: instantiates a new Solver object located on path
                    and whose evaluator map is given by evaluatorsDict'''
        
        print "DBG-SI00: Instantiating an Solver."
        Solver.SolverProcId += 1
        self.id = SOLVER_KEY + str(Solver.SolverProcId)
        try:
            print "DBG-SI01: Loading external program for Solver" + self.id +"."
            self.external = subprocess.Popen(path,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            #Yet to implement error catching.
            print " !!! DBG-SI99: Error loading external program for Solver" + self.id +"."
            pass
        
        print "DBG-SI02: Continuing with execution for Solver" + self.id +"."
        # Set evaluation mapping through dictionaries
        
        print "DBG-SI03: Creating evaluator dictionary for Solver" + self.id +"."
        self.evaluatorMap = evaluatorsDict
        
        print "DBG-SI04: Solver instantiation exited for Solver" + self.id +"."

    def run(self):
        '''run(): executes the external application of the Solver
                    and returns the message tuple according to the
                    internal messaging protocol'''
        
        # Note on the running structure:
        #    Notice that in this coroutine the entry point is in the middle of the solver
        #    (unlike in the run coroutine for the Evaluators).
        #
        #    Instead of inserting operations before the entry point (yield statement), it
        #    is better to write before the loop and append them to the end of each cycle
        #    for initialization purposes (this way it is possible to prime the coroutine).
        self.Primed = False
        
        print "DBG-SR00: Initializing Solver " + self.id + " run."
        passCounter = 1 # Pass counter
        
        # Solver writes, Crumbles reads
        print "DBG-SR01: Unlocking external from Solver " + self.id + " for WRITING." + "Pass:" + str(passCounter)+"."
        self.external.stdin.write(SOLVE_WRITE_UNLOCK + '\n')
                
        print "DBG-SR02: Read from Solver " + str(self.id) + "'s external, Pass" + str(passCounter)+"."
        operation = self.external.stdout.readline()[:-2] # [:-1] to remove the '\n' character
        print "Operation: " + str(operation) + ' Len = ' + str(len(operation))
        message   = self.external.stdout.readline()[:-2] # [:-1] to remove the '\n' character
        print "Message: " + str(message) + ' Len = ' + str(len(message))
        print "DBG-SR03: Finished reading from Solver " + self.id + "'s external." + "Pass:" + str(passCounter)+"."

        while self.external.poll() is None:
            try:
                # Internal messaging system (send and receive)
                self.Primed=True
                print "DBG-SR04: Yielding read messages from Solver " + self.id + ".Pass" + str(passCounter)+"."
                (sender, receiver, message) = yield (self.id, self.evaluatorMap[operation], message)
                
                # Sanity check
                if receiver != self.id:
                    print "DBG-SR98: Wrong delivery! Receiver: " + receiver + " Solver ID: " + self.id
                    
                # Sanity check
                if sender != self.evaluatorMap[operation]:
                    print "DBG-SR97: Wrong delivery! Sender: " + receiver + +" Should be Sender:" + self.evaluatorMap[operation] + "Solver ID: " + self.id
                    
                # Crumbles writes, Solver reads
                print "DBG-SR05: Unlocking external from Solver " + self.id + " for READING." + "Pass:" + str(passCounter)+"."
                self.external.stdin.write(SOLVE_READ_UNLOCK + '\n')
                
                print "DBG-SR06: Writing in Solver " + self.id + "'s external."
                self.external.stdin.write(message + '\n')
                
                print "DBG-SR07: Finished writing in Solver " + self.id + "'s external." + "Pass:" + str(passCounter)+"."
                
                passCounter = passCounter + 1 # Pass counter
                
                # Solver writes, Crumbles reads
                print "DBG-SR01: Unlocking external from Solver " + self.id + " for WRITING." + "Pass:" + str(passCounter)+"."
                self.external.stdin.write(SOLVE_WRITE_UNLOCK + '\n')
                
                print "DBG-SR02: Read from Solver " + str(self.id) + "'s external, Pass" + str(passCounter)+"."
                operation = self.external.stdout.readline()[:-1] # [:-1] to remove the '\n' character
                print "Operation: " + str(operation)
                message   = self.external.stdout.readline()[:-1] # [:-1] to remove the '\n' character
                print "Message: " + str(operation)
                print "DBG-SR03: Finished reading from Solver " + self.id + "'s external." + "Pass:" + str(passCounter)+"."

            except WindowsError:
                # To implement error handling
                print " !!! DBG-SR99: Couldn't locate or open Solver " + self.id + ". Pass:" + str(passCounter)+"."
                quit()
                pass

class Evaluator(object):
    EvaluatorProcId = 0

    def __init__(self, path, function, functionCall):
        '''__init__: instantiates a new Evaluator object located on path
                    which evaluates the function argument by passing the 
                    functionCall string to the external program'''
        
        print "DBG-EI00: Instantiating an Evaluator."
        Evaluator.EvaluatorProcId += 1
        self.id = EVALUATOR_KEY + str(Evaluator.EvaluatorProcId)
        try:
            print "DBG-EI01: Loading external program for Evaluator" + self.id +"."
            self.external = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            # Yet to implement error catching.
            print " !!! DBG-EI99: Error loading external program for Evaluator" + self.id +"."
            pass
        
        print "DBG-EI02: Continuing with execution for Evaluator" + self.id +"."

        # Set evaluator function
        try:
            print "DBG-EI03: Unlocking external from Evaluator" + self.id +" for DEFINING."
            self.external.stdin.write(EVAL_DEFINE_UNLOCK + '\n')
            
            print "DBG-EI04: Writing message length for Evaluator" + self.id +"."
            self.external.stdin.write(str(len(function)) + '\n')
            
            print "DBG-EI05: Writing function on Evaluator" + self.id +"'s external."
            self.external.stdin.write(function + '\n')
        except:
            print " !!! DBG-EI98: Error in Evaluator" + self.id +" function definition."
            
        print "DBG-EI06: Defining function call for Evaluator" + self.id +"'s external."
        self.fcnCall = functionCall
        print "DBG-EI07: Finished instantiating Evaluator" + self.id +"."

    def run(self):
        '''run(): executes the external application of the Evaluator
                    and returns the message tuple according to the
                    internal messaging protocol'''
        
        self.Primed = False
        #Passing stats
        passCounter = 0
        
        #Initial state of messaging system
        message  = ''
        receiver = ''
        sender   = ''
        while self.external.poll() is None:
            self.Primed = True
            try:
                passCounter = passCounter + 1
                
                # Internal messaging system (send and receive)
                print "DBG-ER00: Send/Receive message for Evaluator" + self.id + "Pass:" + str(passCounter)+"."
                (sender, receiver, message) = yield (self.id, sender, message)

                # Sanity check
                if receiver != self.id:
                    print "DBG-ER98: Wrong delivery! Receiver: " + receiver + "Evaluator ID: " + self.id
                    
                # Writing message to be evaluated
                print "DBG-ER01: Unlocking external from Evaluator " + self.id + " for COMPUTING." + "Pass:" + str(passCounter)+"."
                self.external.stdin.write(EVAL_COMPUTE_UNLOCK + '\n')
                
                print "DBG-ER02: Writing message length in Evaluator " + self.id + "'s external." + "Pass:" + str(passCounter)+"."
                self.external.stdin.write(str(len(message) + str(len(self.fcnCall)) + 3) + '\n')
                
                print "DBG-ER03: Writing message in Evaluator " + self.id + "'s external." + "Pass:" + str(passCounter)+"."
                self.external.stdin.write(self.fcnCall + '[' + message + ']\n')
                
                # Reading results from external process
                print "DBG-ER04: Reading response from Evaluator " + self.id + "'s external." + "Pass:" + str(passCounter)+"."
                message = self.external.readline()[:-1] # [:-1] to remove the '\n' character

            except WindowsError:
                # To implement error handling
                print " !!! DBG-ER99: Couldn't locate or open on Evaluator " + self.id + ". Pass:" + str(passCounter)+"."
                pass

class Manager():

    def __init__(self):
        print "DBG-MI00: Instantiating Manager."
        self.queue = Queue.Queue()
        self.activeProcesses = {SOLVER_KEY:{}, EVALUATOR_KEY:{}}
        
        print "DBG-MI00: Finished instantiating Manager."

    def createSolver(self, path, evaluatorsDict):
        '''createSolver: instantiates a new solver and adds to the
                        the Manager's execution queue.
        '''
        print "DBG-MS00: Creating and appending new Solver to Manager."
        newSolver= Solver(path, evaluatorsDict)
        
        print "DBG-MS01: Updating the Solver section of the Manager's activeProcess dictionary."
        self.activeProcesses[SOLVER_KEY][newSolver.id] = newSolver
        
        print "DBG-MS02: Finished adding new Solver to Manager."

    def createEvaluator(self, path, function, functionCall):
        '''createEvaluator: instantiates a new Evaluator available
                            for the other processes.
        '''
        
        print "DBG-ME00: Creating and appending new Evaluator to Manager."
        newEvaluator = Evaluator(path, function, functionCall)
        
        print "DBG-ME01: Updating the Evaluator section of the Manager's activeProcess dictionary."
        self.activeProcesses[EVALUATOR_KEY][newEvaluator.id] = newEvaluator
        
        print "DBG-ME02: Finished adding new Evaluator to Manager."

    def enqueue(self, sender, receiver, message):
        '''enqueue: puts the tuple (process, sender, receiver, message) in
                    the Manager's execution queue.
        '''
        # Uses the internal process ID structure, where the first character is the type of process.
        self.queue.put((self.activeProcesses[receiver[0]][receiver], sender, receiver, message))
        
    def execute(self):
        '''execute: main execution loop of the Manager.
                    This method is responsible for managing the execution queue
                    and for directing messages appropriately.
        '''
        # Cycle stats
        exeCycle = 0
        nextCycle = "Y"
        
        # Initialization of messaging protocol
        message  = ''
        receiver = ''
        sender   = ''
        
        #prime all solvers
        for activeSolvs in self.activeProcesses[SOLVER_KEY]:
            solvProc = self.activeProcesses[SOLVER_KEY][activeSolvs]
            (sender, receiver, message) = solvProc.run().next()
            print 'Solver Primed: ' + solvProc.id
            self.enqueue(sender, receiver, message)
        
        #prime all evaluators
        for activeEvals in self.activeProcesses[EVALUATOR_KEY]:
            evalProc = self.activeProcesses[EVALUATOR_KEY][activeEvals]
            (sender, receiver, message) = evalProc.run().next()
            print 'Evaluator Primed: ' + evalProc.id
        
        while self.activeProcesses[SOLVER_KEY] and nextCycle == "Y":
            try:
                exeCycle = exeCycle + 1
                print "DBG-MX00: Started Cycle " + str(exeCycle) + "."
            
                print "DBG-MX01: Getting process from queue. Cycle: " + str(exeCycle) + "."
            
                print "Size of queue: " + str(self.queue.qsize())
                if self.queue.qsize() != 0:
                    (process, sender, receiver, message) = self.queue.get()
                    print '(' + process.id + ',' + sender + ',' + receiver + ',' + message + ')'
                    print "Primed? " + str(process.Primed)
                else:
                    print " !!! DBG-MX99: Trying to get from empty queue."
                    exit()
            
                print "DBG-MX01: Process obtained from queue. Process: " + str(process.id) + ". Cycle: " + str(exeCycle) + "."
                
                print "DBG-MX02: Sending values and getting output from Process " + str(process.id) + ". Cycle: " + str(exeCycle) + "."
                (sender, receiver, message) = process.run().send((sender, receiver, message))
            
                print "DBG-MX03: Putting Process " + receiver + " on queue. Cycle: " + str(exeCycle) + "."
                self.enqueue(sender, receiver, message)
            
                print "DBG-MX04: Finished Cycle " + str(exeCycle) + "."
            
                nextCycle = raw_input("DBG-MX05: Do you want to proceed with the next cycle? Y to continue.").capitalize()
            
            except StopIteration:
                # Terminates all solvers
                for activeSolver in self.activeProcesses[SOLVER_KEY]:
                    self.terminateProcess(self.activeProcesses[SOLVER_KEY][activeSolver])
                    
                # Terminates all evaluators
                for activeEval in self.activeProcesses[EVALUATOR_KEY]:
                    self.terminateProcess(self.activeProcesses[EVALUATOR_KEY][activeEval])
                    
                continue

    def terminateProcess(self,ProcessID):
        proc = self.activeProcesses[ProcessID[0]][ProcessID]
            
        while proc.poll() is None:
            proc.stdout.write(QUIT_KEY)
            proc.terminate()
            print "DBG-MT00: Termination requested for Process " + proc.id + "."
            
        print "DBG-MT01: Termination completed for Process " + proc.id + "."
        del self.activeProcesses[ProcessID[0]][ProcessID]
        
        print "DBG-MT02: Removed Process " + proc.id + "from active list."
        

if __name__ == "__main__":
    rootDir = "C:\\Documents and Settings\\Update\\My Documents\\Eclipse\\Projects\\Crumbles\\"
    #pathEval = rootDir + "ipoptExternalEval.exe"
    pathSolv = rootDir + "dummySolver.exe"
    pathEval = rootDir + "dummyComm.exe"
    evalDictIpopt = {}

    crumbles = Manager()

    # Dictionary {definition:callback}
    evalDict = {1:("a := Compile[{x1,x2,x3},N[{x1*2.,x2*2.,x3*3.}]]","a")}
    evalMap = {'A':'E1'}
    
    ## Ipopt evaluator definition:
    #funcDict = {0:("get_structure","get_structure"),
    #            1:("eval_f","eval_f"),
    #            2:("eval_grad_f","eval_grad_f"),
    #            3:("eval_g","eval_g"),
    #            4:("eval_jac_g","eval_jac_g"),
    #            5:("eval_h","eval_h")}

    ## Ipopt solver dictionary:
    #funcDict = {"I":"get_structure",
    #            "F":"eval_f",
    #            "D":"eval_grad_f",
    #            "G":"eval_g",
    #            "J":"eval_jac_g",
    #            "H":"eval_h"}

    for i in evalDict:
        crumbles.createEvaluator(pathEval, evalDict[i][0], evalDict[i][1])

    crumbles.createSolver(pathSolv, evalMap)
    crumbles.execute()
