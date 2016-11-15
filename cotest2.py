import Queue

class coA(object):
    tag = 0
    def __init__(self):
        coA.tag +=1
        self.tag = coA.tag
        pass

    def run(self):
        a,b,c = 0.0,0.0,0.0
        while True:
            a +=1.0
            b +=1.0
            c +=1.0
            print "A"+str(self.tag)+" sent ('B',2,"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'
            (a,b,c) = yield ('B',2,a,b,c)
            print "A"+str(self.tag)+" got  ('?',?,"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'
            
            a +=3.0
            b +=3.0
            c +=3.0
            print "A"+str(self.tag)+" sent ('B',1,"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'
            (a,b,c) = yield ('B',1,a,b,c)
            print "A"+str(self.tag)+" got  ('?',?,"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'

class coB(object):
    tag = 0
    def __init__(self):
        coB.tag += 1
        self.tag = coB.tag
        pass

    def run(self):
        a,b,c = 0,0,0
        while True:
            a +=2.5
            b +=2.5
            c +=2.5
            print "B"+str(self.tag)+" sent ('A',1,"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'
            (a,b,c) = yield ('A',1,a,b,c)
            print "B"+str(self.tag)+" got  ('?',?,"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'

class manager(object):
    def __init__(self):
        self.dict={'A':{},'B':{}}
        self.q = Queue.Queue()

    def newCoA(self):
        a = coA()
        self.dict['A'][a.tag] = a.run()
        print "Created A" + str(a.tag)
    
    def newCoB(self):
        b1 = coB()
        b2 = coB()
        self.dict['B'][b1.tag] = b1.run()
        print "Created B" + str(b1.tag)
        self.dict['B'][b2.tag] = b2.run()
        print "Created B" + str(b2.tag)
    
    def run(self):
        print "Priming!"
        for entry in self.dict['A']:
            proc = self.dict['A'][entry]
            proc.next()
            
        for entry in self.dict['B']:
            proc = self.dict['B'][entry]
            proc.next()

        print "All primed!\n"
        
        self.q.put(('A',1,10.0,10.0,10.0))

        print "Inserted A1 in queue"
        
        for i in range(1,5):
            print "QUEUE SIZE" + str(self.q.qsize())
            ((prc,tag,x,y,z)) = self.q.get()
            process = self.dict[prc][tag]
            
            print "About to run process " + str(prc)+str(tag)
            (prc,tag,x,y,z) = process.send((x,y,z))

            print "DEQUEUE ('"  + str(prc) + "'," + str(tag) + ',' + str(x) + ',' + str(y) + ',' + str(z) + ')'
            self.q.put((prc,tag,x,y,z))
            print "ENQUEUE ('" + str(prc) + "'," + str(tag) + ',' + str(x) + ',' + str(y) + ',' + str(z) + ')'

mgr = manager()
mgr.newCoA()
mgr.newCoB()
mgr.run()
