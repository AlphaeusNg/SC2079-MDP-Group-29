# Steps to run on RPi

- From `rpi/` directory, create a virtual env if there's no venv exist: 

```shell
python -m venv .venv
```

- Activate the virtual env:

```shell
.venv\Scripts\activate
```

- Install required packages:

```shell
pip install -e .
```

- Change directory to `mdp-rpi` and run `rpi_main.py`:

```shell
cd mdp-rpi
python rpi_main.py
```