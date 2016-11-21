import sys

if len(sys.argv) < 2:
    print('Error: missing step number')
    sys.exit(1)
step = int(sys.argv[1])

if step == 1:
    # Step 1
elif step == 2:
    # Step 2
elif step == 3:
    # Step 3
else:
    print('Error: invalid step number')
    sys.exit(1)
