# ACS - Clustering system

## How to Download?
### 1) Make sure to download the GitHub repo:

```bash
git clone https://github.com/blokkaDev/cluster.git
cd cluster
```

### 2) Create the Python `Venv`:

Linux/MacOS:
```bash
python3 -m venv .venv
```

Windows:
```bash
python -m venv .venv
```

### 3) Activate the Venv:

Linux/MacOS:
```bash
source .venv/bin/activate
```

Windows:
```shell
.venv\Scripts\Activate.ps1
```

### 4) Install ACS:

```bash
pip install -e .
```

### 5) Download Deno to use the sandbox:

Linux/MacOS:
```bash
curl -fsSL https://deno.land/install.sh | sh
```

Windows:
```shell
irm https://deno.land/install.ps1 | iex
```

### 6) Check if Deno is installed:

```bash
deno --version
```
If is not installed restart your terminal

<<<<<<< HEAD
## How to Run the CLI?
#### Here is a quick list of commands to try

### Start the manager
```bash
acs start --manager
```

### Start the worker
```bash
acs start --worker
```

### Connect the manager with the worker
```bash
acs connect
```

### Now it's time to load the worker to the manager
```bash
acs load
```

### Run a python file
```bash
acs run file_name --python
```

### Command list
```bash
acs --help
```

## How to Run it whithout the CLI?
#### If you run it whithout the CLI you will enable the Development mode

### Development mode file
=======
### 7) Final step, now you can run the program with this command:
>>>>>>> 43bfc60b5e443e4d89bbab4800f3c58941acaa49
```bash
python main.py
```

##### THIS IS THE FIRST VERSION OF THE CLI SO THE COMMAND ARE NOT PERFECT