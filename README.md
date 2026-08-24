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

### 4) Now you should be able to download the requirements:

```bash
pip install -r requirements.txt
```

### 5) Download Deno to use the sandbox

Linux/MacOS:
```bash
curl -fsSL https://deno.land/install.sh | sh
```

Windows:
```shell
irm https://deno.land/install.ps1 | iex
```

### 6) Check if Deno is installed

```bash
deno --version
```
If is not installed restart your terminal

### 6) Final step, now you can run the program with this command:
```bash
python main.py
```
