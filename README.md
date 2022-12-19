# thingsboard-data-download

Python script to pull data from Thingsboard instance

## How to run:

### from windows:

#### Install python

Install Python first if you do not have it. You can download it from [the Python website](https://www.python.org/downloads/windows/).

#### Install the required python libraries

Open the Command Prompt (search "cmd" in the windows menu) and type:

```
py -m pip install clicks requests pandas toml tqdm
```

#### Edit the file config.toml

Open the file config.toml in any editor and change username and password to match your credentials. Change devices and variables to match the sensors and variables of which you want to download the data.

#### Run the script

You should now be ready to run the script from the same command prompt:

```
py tb-data-download.py config.toml
```

## Troubleshooting

If you get the following error:

```
KeyError: 'token'
```

then that means that your login credentials are not correct. Check the file config.toml




