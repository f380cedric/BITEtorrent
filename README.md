# ELEC-H-417: BitTorrent-like Project

## Customize the config

You can edit the file `config/peers.ini` to change the IP addresses and port numbers of the peers.
The *discoverable* port number is fixed to **9000** and cannot be changed.

The default config file is:

```ini
[tracker]
ip_address = 127.0.0.1
port_number = 8000

[alice]
ip_address = 127.0.0.1
port_number = 8001

[bob]
ip_address = 127.0.0.1
port_number = 8002
```

## Create a file of random bytes

```bash
head -c [bytes_count] < /dev/urandom > files/[filename]
```

## Add a file

First create the directory `files/` and add a file or create a new file with random bytes.
Then, run:

```bash
python3 src/create_chunks.py [filename]
```

The first third of the chunks are owned only by Alice.
The second third are owmed by Alice and Bob.
And the last third are owned only by Bob.

## Step 1

Launch Alice and Bob in two terminals:
```bash
python3 src/alice.py
python3 src/bob.py
```

Launch Charlie (you) in a third terminal:
```bash
python3 src/charlie.py 1
```

where `1` is the step number.

## Step 2

Launch Alice and Bob in two terminals:
```bash
python3 src/alice.py
python3 src/bob.py
```

Launch the tracker in a terminal:
```bash
python3 src/tracker.py
```

Launch Charlie (you) in a third terminal:
```bash
python3 src/charlie.py 2
```

where `2` is the step number.

## Step 3

Launch Alice and Bob in two terminals:
```bash
python3 src/alice.py
python3 src/bob.py
```

Launch the tracker in a terminal:
```bash
python3 src/tracker.py
```

Launch Charlie (you) in a third terminal:
```bash
python3 src/charlie.py 3
```

where `3` is the step number.

## Merge the chunks

In order to recover the file from the downloaded chunks, run:
```bash
python3 src/merge_chunks.py
```

## Check the file
In order to check if the file is exactly the same, run:
```bash
python3 src/check_file.py
```
