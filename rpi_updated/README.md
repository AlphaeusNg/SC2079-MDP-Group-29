# Steps to run on RPi

- From `rpi/` directory, create a virtual env if there's no venv exist: 

```shell
python3 -m venv .venv
```

- Activate the virtual env:

```shell
source .venv/bin/activate
```


- Update pip:

```shell
pip3 install --upgrade setuptools pip
```

- Install required packages (--verbose allows you to see what's going on):

```shell
pip install -e . --verbose
```

- Change directory to `mdp-rpi` and run `rpi_main.py`:

```shell
cd mdp-rpi
python rpi_main.py
```
