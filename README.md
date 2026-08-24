# ACS - Clustering system

## Requirements

 - Python 3.12+
 - pipx

## How to Download?
### 1) Make sure to download the GitHub repo:

```bash
git clone https://github.com/blokkaDev/cluster.git
cd cluster
```

## Using pipx

### 1) Install ACS with pipx: 
```bash
pipx install .
```

### 2) If pipx us not yet avaiable in your path run:
```bash
pipx ensurepath
``` 
Now restart your terminal

You should be able to use acs in any directory

Try running this command:
```bash
acs --help
``` 

## Development
### 1) Create the Python `Venv`:

Linux/MacOS:
```bash
python3 -m venv .venv
```

Windows:
```bash
python -m venv .venv
```

### 2) Activate the Venv:

Linux/MacOS:
```bash
source .venv/bin/activate
```

Windows:
```shell
.venv\Scripts\Activate.ps1
```

### 3) Install ACS:

```bash
pip install -e .
```

### 4) Download Deno to use the sandbox:

Linux/MacOS:
```bash
curl -fsSL https://deno.land/install.sh | sh
```

Windows:
```shell
irm https://deno.land/install.ps1 | iex
```

### 5) Check if Deno is installed:

```bash
deno --version
```
If is not installed restart your terminal

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

### Run the Development mode file in the root directory of the project
```bash
python main.py
```

##### THIS IS THE FIRST VERSION OF THE CLI SO THE COMMAND ARE NOT PERFECT
