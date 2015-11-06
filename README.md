# lab-cloudformation

## Installation

To use this repository, you must install the following Python libraries:

 - docopt
 - boto
 - troposphere

Installing the dependencies within virtualenv isolates the dependencies used by this project from those of any other python projects you might have. It is standard practice for working with python.

First time steps: Install and initialize the virtualenv wrapper tool.

```
[Mac or Linux]
> pip install virtualenvwrapper
> source /usr/local/bin/virtualenvwrapper.sh  # put this line in your .bash_profile
```
If pip is not currently installed you can install it after installing python with:
```
> easy_install pip
```
[For Windows ]
pip install virtualenvwrapper-win
If pip is not currently installed you can install it by following the instructions here:
```
http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows

or just upgrade your python to 2.7.9 or later

```

From within the project directory, create and install the dependencies for a new environment called cflab (for example):

```
> mkvirtualenv cflab 
```

Now you are inside the virtual environment as indicated by the parentheses at the begining of the prompt. To exit the virtual environment, run shell function `deactivate`. From here on you can reenter your virtual environment by running workon cflab

```
(cflab)MyComputerName:aws-cflab $ deactivate
MyComputerName:aws-cflab $ workon cflab
(cflab)MyComputerName:aws-cflab $
```
Install the project dependencies by running the following command while inside your virtualenv:

```
(cflab) $ pip install -r requirements.txt
```

# Let's get going

To use the script itself, you can run it directly from the command line:

```bash
python src/lab.py -h
```

To generate some Cloudformation JSON simply run the command:

```bash
python src/lab.py generate --config-file src/template_config.yaml
```

This should produce a `labenvironment.template` file that you can now use to deploy your
Cloudformation stack.
