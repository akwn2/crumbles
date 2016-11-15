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

class Solver(object):
    SolverProcId = 0

    def __init__(self, path, evaluatorsDict):
        '''__init__: instantiates a new Solver object located on path
                    and whose evaluator map is given by evaluatorsDict'''
        
        print "DBG-SI00: Instantiating an Solver."
        Solver.SolverProcId += 1
        self.id = 'S' + str(Solver.SolverProcId)
        try:
            print "DBG-SI01: Loading external program for Solver" + self.id +"."
            self.external = subprocess.Popen(path,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            #Yet to implement error catching.
            print "DBG-SI99: Error loading external program for Solver" + self.id +"."
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
        
        print "DBG-SR00: Initializing Solver " + self.id + " run."
        passCounter = 0 # Pass counter
        while self.external.poll() is None:
            try:
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

                # Internal messaging system (send and receive)
                print "DBG-SR04: Yielding read messages from Solver " + self.id + ".Pass" + str(passCounter)+"."
                (m_from, m_to, message) = yield (self.id, self.evaluatorMap[operation],message)

                # Crumbles writes, Solver reads
                print "DBG-SR05: Unlocking external from Solver " + self.id + " for READING." + "Pass:" + str(passCounter)+"."
                self.external.stdin.write(SOLVE_READ_UNLOCK + '\n')
                
                print "DBG-SR06: Writing in Solver " + self.id + "'s external."
                self.external.stdin.write(message + '\n')
                
                print "DBG-SR07: Finished writing in Solver " + self.id + "'s external." + "Pass:" + str(passCounter)+"."

            except:
                # To implement error handling
                print "DBG-SR99: Something went wrong on Solver " + self.id + "Pass:" + str(passCounter)+"."
                pass

class Evaluator(object):
    EvaluatorProcId = 0

    def __init__(self, path, function, functionCall):
        '''__init__: instantiates a new Evaluator object located on path
                    which evaluates the function argument by passing the 
                    functionCall string to the external program'''
        
        print "DBG-EI00: Instantiating an Evaluator."
        Evaluator.EvaluatorProcId += 1
        self.id = 'E' + str(Evaluator.EvaluatorProcId)
        try:
            print "DBG-EI01: Loading external program for Evaluator" + self.id +"."
            self.external = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except:
            # Yet to implement error catching.
            print "DBG-EI99: Error loading external program for Evaluator" + self.id +"."
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
            print "DBG-EI98: Error in Evaluator" + self.id +" function definition."
            
        print "DBG-EI06: Defining function call for Evaluator" + self.id +"'s external."
        self.fcnCall = functionCall
        print "DBG-EI07: Finished instantiating Evaluator" + self.id +"."

    def run(self):
        '''run(): executes the external application of the Evaluator
                    and returns the message tuple according to the
                    internal messaging protocol'''
        message = ''
        m_to    = ''
        m_from  = ''
        passCounter = 0
        while self.external.poll() is None:
            try:
                passCounter = passCounter + 1
                # Internal messaging system (send and receive)
                print "DBG-ER00: Send/Receive message for Evaluator" + self.id + "Pass:" + str(passCounter)+"."
                (m_to, m_from, message) = yield(self.id, m_to, message)

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

            except:
                # To implement error handling
                print "DBG-ER99: Unlocking external from Evaluator " + self.id + " for READING." + "Pass:" + str(passCounter)+"."
                pass

class Manager():

    def __init__(self):
        print "DBG-MI00: Instantiating Manager."
        self.queue = Queue.Queue()
        self.activeProcesses = {'S':{}, 'E':{}}
        
        print "DBG-MI00: Finished instantiating Manager."

    def createSolver(self, path, evaluatorsDict):
        
        print "DBG-MS00: Creating and appending new Solver to Manager."
        newSolver= Solver(path, evaluatorsDict)
        
        print "DBG-MS01: Updating the Solver section of the Manager's activeProcess dictionary."
        self.activeProcesses['S'][newSolver.id] = newSolver

        print "DBG-MS02: Adding Solver to the Manager's queue."
        self.queue.put(self.activeProcesses['S'][newSolver.id])
        print "Size of queue: " + str(self.queue.qsize())
        
        print "DBG-MS03: Finished adding new Solver to Manager."

    def createEvaluator(self, path, function, functionCall):
        
        print "DBG-ME00: Creating and appending new Evaluator to Manager."
        newEvaluator = Evaluator(path, function, functionCall)
        
        print "DBG-ME01: Updating the Evaluator section of the Manager's activeProcess dictionary."
        self.activeProcesses['E'][newEvaluator.id] = newEvaluator
        
        print "DBG-ME02: Finished adding new Evaluator to Manager."
        
    def terminateEvaluators(self):
        for activeEval in self.activeProcesses['E']:
             self.activeProcesses['E'][activeEval].kill()

    def execute(self):
        exeCycle = 0
        nextCycle = "Y"
        while self.activeProcesses['S'] and nextCycle == "Y":
            exeCycle = exeCycle + 1
            print "DBG-MX00: Started Cycle" + str(exeCycle) + "."
            
            print "DBG-MX01: Getting process from queue. Cycle:" + str(exeCycle) + "."
            print "Size of queue: " + str(self.queue.qsize())
            if self.queue.qsize() != 0:
                process = self.queue.get()
            else:
                "DBG-MX99: Trying to get from empty queue."
                exit()
            
            print "DBG-MX01: Process obtained from queue. Process:" + str(process.id) + ". Cycle:" + str(exeCycle) + "."
            
            print "DBG-MX02: Getting getting output from Process " + str(process.id) + ". Cycle:" + str(exeCycle) + "."
            (m_from, m_to, message) = process.run()
            
            # Utilizing the internal communication protocol,
            # where the first character of m_to (process ID) is the type of process.
            print "DBG-MX03: Putting Process" + m_to + "on queue. Cycle:" + str(exeCycle) + "."
            self.queue.put(self.activeProcess[m_to[0]][m_to])
            
            print "DBG-MX04: Finished Cycle" + str(exeCycle) + "."
            
            nextCycle = raw_input("DBG-MX05: Do you want to proceed with the next cycle? Y/N").capitalize()

if __name__ == "__main__":
    rootDir = "C:\\Documents and Settings\\Update\\My Documents\\Eclipse\\Projects\\Crumbles\\"
    #pathEval = rootDir + "ipoptExternalEval.exe"
    pathSolv = rootDir + "dummySolver.exe"
    pathEval = rootDir + "commToKernel.exe"
    evalDictIpopt = {}

    crumbles = Manager()

    # Dictionary {definition:callback}
    evalDict = {1:("a := Compile[{x1,x2,x3},N[{x1*2.,x2*2.,x3*3.}]]","a")}
    
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

    crumbles.createSolver(pathSolv, evalDict)
    crumbles.execute()
