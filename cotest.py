import Queue

def coA():
    a,b,c = 0,0,0
    while True:
        a +=1
        b +=1
        c +=1
        print "coA sent ('b',"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'
        (nextCo,a,b,c) = yield ('b',a,b,c)
        print "coA got ('"+ str(nextCo) +"',"+ str(a)+ ',' + str(b) + ',' + str(c)+')'

def coB():
    a,b,c = 0,0,0
    while True:
        a +=2
        b +=2
        c +=2
        print "coB sent ('a',"+ str(a)+ ',' + str(b) + ',' + str(c) + ')'
        (nextCo,a,b,c) = yield ('a',a,b,c)
        print "coB got ('"+ str(nextCo) +"',"+ str(a)+ ',' + str(b) + ',' + str(c)+')'

print "Priming!"
a = coA()
a.next()
b = coB()
b.next()
print "Both primed!\n"
q = Queue.Queue()
q.put(('a',2,3,4))
for i in range(1,5):
    print "Queue size: " + str(q.qsize())
    (nextCo,x,y,w) = q.get()
    if nextCo == 'a':
        (nextCo,x,y,w) = a.send((nextCo,x,y,w))
        print '('+str(nextCo)+','+str(x)+','+str(y)+','+str(w)+')'
        q.put((nextCo,x,y,w))
    else:
        (nextCo,x,y,w) = b.send((nextCo,x,y,w))
        print '('+str(nextCo)+','+str(x)+','+str(y)+','+str(w)+')'
        q.put((nextCo,x,y,w))

#(z,(y,x,w))=q.get()
#z.send((y,x,w))
