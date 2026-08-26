# ACS - Clustering System

ACS is a Python-based clustering system that allows you to run a Manager and one or more Workers and execute code remotely.

## Requirements

- Python 3.12+
- pipx
- Deno

## Installation

### Clone the repository

```bash
git clone https://github.com/blokkaDev/cluster.git
cd cluster
```

### Install ACS with pipx

```bash
pipx install .
```

If pipx is not yet available in your PATH, run:

```bash
pipx ensurepath
```

Then restart your terminal.

You should now be able to use `acs` from any directory:

```bash
acs --help
```

## Configuration

Before starting ACS, you need to create the environment file:

```
data/secrets/.env
```

An example configuration is provided in:

```
data/secrets/.env.example
```

Copy the example file:

```bash
cp data/secrets/.env.example data/secrets/.env
```

On Windows PowerShell:

```powershell
Copy-Item data/secrets/.env.example data/secrets/.env
```

Then edit `data/secrets/.env` with your configuration.

### Example .env

```
# Worker
WORKER_ID=idd-2
WORKER_TOKEN=worker-secret-token
WORKER_HOST=0.0.0.0
WORKER_PORT=8001
WORKER_HOSTNAME=acs.worker-idd-2.local

# Manager
MANAGER_TOKEN=manager-secret-token
MANAGER_HOST=0.0.0.0
MANAGER_PORT=8000
MANAGER_HOSTNAME=acs.manager.local
MANAGER_REMEMBER=true
```

## Development

If you want to work on ACS without installing it globally, create a virtual environment.

### Create the virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
```

Windows:

```powershell
python -m venv .venv
```

### Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install ACS

```bash
pip install -e .
```

## Install Deno

Deno is required to use the sandbox.

Linux/macOS:

```bash
curl -fsSL https://deno.land/install.sh | sh
```

Windows:

```powershell
irm https://deno.land/install.ps1 | iex
```

Check the installation:

```bash
deno --version
```

If the command is not available, restart your terminal.

## CLI Usage

ACS provides a CLI through the `acs` command.

Show the available commands:

```bash
acs --help
```

### Start the Manager

```bash
acs start --manager
```

The Manager uses the configuration defined by:

- `MANAGER_HOST`
- `MANAGER_PORT`
- `MANAGER_TOKEN`
- `MANAGER_HOSTNAME`

### Start a Worker

```bash
acs start --worker
```

The Worker uses the configuration defined by:

- `WORKER_ID`
- `WORKER_HOST`
- `WORKER_PORT`
- `WORKER_TOKEN`
- `WORKER_HOSTNAME`

### Connect a Worker to the Manager

The connect command requires the Manager address and authentication token:

```bash
acs connect <host> <port> <token>
```

For example:

```bash
acs connect 127.0.0.1 8000 manager-secret-token
```

The remember option can also be disabled:

```bash
acs connect 127.0.0.1 8000 manager-secret-token --no-remember
```

### Load a Worker

Load a worker by specifying its ID and the Manager token:

```bash
acs load <worker_id> <token>
```

For example:

```bash
acs load idd-2 manager-secret-token
```

### Execute a Python file

To execute a Python file on a Worker:

```bash
acs run file_name.py --python
```

For example:

```bash
acs run example.py --python
```

At the moment, Python is the supported language for the run command.

## Typical Workflow

A basic ACS workflow consists of starting the Manager, starting a Worker, connecting them, loading the Worker, and finally executing code.

### Terminal 1 — Manager

```bash
acs start --manager
```

### Terminal 2 — Worker

```bash
acs start --worker
```

### Terminal 3 — Connect

```bash
acs connect <manager-host> <manager-port> <manager-token>
```

For example:

```bash
acs connect 127.0.0.1 8000 manager-secret-token
```

### Load the Worker

```bash
acs load idd-2 manager-secret-token
```

### Run code

```bash
acs run example.py --python
```

## Available Commands

```bash
acs --help
acs connect <host> <port> <token>
acs load <worker_id> <token>
acs run <file> --python
acs start --manager
acs start --worker
```

## Running ACS Without the CLI

ACS can also be run directly using Python.

This mode is mainly intended for development and debugging.

From the root of the project:

```bash
python main.py
```

**Note:** ACS is currently in its first CLI version. Some commands, options, and behaviours may change in future releases.
