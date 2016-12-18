# Script to launch all the parts of the project.
# The argument determine wich step of the project is lauched.
# Must be lauched from src/


### STEP 1 ###


if hash x-terminal-emulator 2>/dev/null; then
    console=x-terminal-emulator
elif hash gnome-terminal 2>/dev/null; then
    console=gnome-terminal
elif hash konsole 2>/dev/null; then
    console=konsole
elif hash xterm 2>/dev/null; then
    console=xterm
elif hash xfce4-terminal 2>/dev/null; then
    console=xfce4-terminal
else
    echo "Can't found terminal"
    exit
fi

if [ $1 = 1 ]; then
    echo "Lauching step 1 of the project:"
    
    echo "Clearing chunks/charlie"
    rm -rf ../chunks/charlie/*
    
    echo "Checking if alice is launched:"
    netcat -w 3 -z 127.0.0.1 50007
    
    if [ $? = 1 ]; then
        echo "alice not launched"
        echo "Lauching alice"
        $console -e  'python3 alice.py'
    else
        echo "alice already launched"
    fi

    echo "Checking if bob is launched:"
    netcat -w 3 -z 127.0.0.2 50007
    
    if [ $? = 1 ]; then
        echo "bob not launched"
        echo "Lauching bob"
        $console -e 'python3 bob.py'
    else
        echo "bob already launched"
    fi

    echo "Lauching charlie"
    sleep .5
    python3 charlie.py 1

### STEP 2 ###

elif [ $1 = 2 ]; then
    echo "Lauching step 2 of the project:"
    
    echo "Clearing chunks/charlie"
    rm -rf ../chunks/charlie/*
    
    echo "Checking if alice is launched:"
    netcat -w 3 -z 127.0.0.1 50007

    if [ $? = 1 ]; then
        echo "alice not launched"
        echo "Lauching alice"
        $console -e 'python3 alice.py'
    else
        echo "alice already launched"
    fi

    echo "Checking if bob is launched:"
    netcat -w 3 -z 127.0.0.2 50007
    
    if [ $? = 1 ]; then
        echo "bob not launched"
        echo "Lauching bob"
        $console -e 'python3 bob.py'
    else
        echo "bob already launched"
    fi
    
    echo "Checking if tracker is launched:"
    netcat -w 3 -z 127.0.0.1 8000
    
    if [ $? = 1 ]; then
        echo "tracker not launched"
        echo "Lauching tracker"
        $console -e 'python3 tracker.py'
    else
        echo "tracker already launched"
    fi

    echo "Lauching charlie"
    sleep .5
    python3 charlie.py 2

### STEP 3 ###

elif [ $1 = 3 ]; then
	echo "Feature not yet implemented"

else
    echo "Incorrect parameter"
fi