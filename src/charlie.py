#!/usr/bin/python3

import sys
from lib.client1 import Clientv1
from lib.client2 import Clientv2
from lib.client3 import Clientv3
from lib.clientonline import clientonline

if len(sys.argv) < 2:
    print('Error: missing step number')
    sys.exit(1)
step = int(sys.argv[1])

if step == 1:
    charlie = Clientv1('charlie')
elif step == 2:
    charlie = Clientv2('charlie')
elif step == 3:
    charlie = Clientv3('charlie')
elif step == 4:
    charlie = clientonline('charlie')
else:
    print('Error: invalid step number')
    sys.exit(1)

charlie.start()