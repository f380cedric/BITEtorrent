import sys
from lib.client1 import client1
from lib.client2 import client2
from lib.client3 import client3


if len(sys.argv) < 2:
    print('Error: missing step number')
    sys.exit(1)
step = int(sys.argv[1])

if step == 1:
    charlie = client1('charlie')
elif step == 2:
    charlie = client2('charlie')
elif step == 3:
    charlie = client3('charlie')
else:
    print('Error: invalid step number')
    sys.exit(1)

charlie.start()