if [ "$1" = "1" ]; then
    echo "Lauching step 1 of the project:"
    
    echo "Clearing chunks/charlie"
    rm -rf ../chunks/charlie/*
    
    echo "Lauching alice"
    x-terminal-emulator -e ~/BITEtorrent/src/exec.sh python3 alice.py
    
    echo "Lauching bob"
    x-terminal-emulator -e ~/BITEtorrent/src/exec.sh python3 bob.py

    echo "Lauching charlie"
    python3 charlie.py 1

elif [ "$1" = "2" ]; then
    echo "Lauching step 2 of the project:"
    
    echo "Clearing chunks/charlie"
    rm -rf ../chunks/charlie/*
    
    echo "Lauching alice"
    x-terminal-emulator -e ~/BITEtorrent/src/exec.sh python3 alice.py
    
    echo "Lauching bob"
    x-terminal-emulator -e ~/BITEtorrent/src/exec.sh python3 bob.py
    
    echo "Lauching tracker"
    x-terminal-emulator -e ~/BITEtorrent/src/exec.sh python3 tracker.py

    echo "Lauching charlie"
    python3 charlie.py 2

elif [ "$1" = "2" ]; then
	echo "Feature not yet implemented"

else
    echo "Incorrect parameter"
fi