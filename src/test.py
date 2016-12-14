import time
import queue
import random

r = random.randint(6,20)
print(r)
a = {}
for i in range(r):
 a[str(i)] = ''
b = queue.Queue()
start = time.clock()
[b.put(i) for i in a]
stop = time.clock()
fre = stop - start
c = queue.Queue()
x = time.clock()
list(map(c.put, a))
y = time.clock()
sre = y - x
print('first', fre)
print('second', sre)
