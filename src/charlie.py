import sys
import lib

if len(sys.argv) < 2:
    print('Error: missing step number')
    sys.exit(1)
step = int(sys.argv[1])

if step == 1:
    charlie = lib.client1('charlie')
elif step == 2:
    charlie = lib.client2('charlie')
elif step == 3:
    charlie = lib.client3('charlie')
else:
    print('Error: invalid step number')
    sys.exit(1)