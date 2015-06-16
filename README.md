# lab-cloudformation


# Let's get going

To use this repository, you must install the following Python libraries:

docopt
boto
troposphere
ipcalc
This can be done by running the following command from this directory:

```bash
sudo pip install -r requirements.txt --upgrade
```

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
