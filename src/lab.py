#!/usr/bin/env python

"""

Usage:
  lab.py generate [--config-file <config_file>] [--output-file <OUTPUT_FILE>]...
  lab.py (-h | --help)
  lab.py --version

Options:
  -h --help                     Show this screen.
  --version                     Show version.
  --config-file <CONFIG_FILE>   Input for config data for the generated CF template. Defaults to template_config.json
  --output-file <OUTPUT_FILE>   Destination for the generated CF template. Defaults to labenvironment.template

"""
from docopt import docopt
import json
import yaml

from troposphere import Parameter, Output, Ref, Template
from troposphere import Base64, FindInMap, GetAtt
from vpc_generator import VPCGenerator
from ec2_generator import EC2Generator

class CFLab:
    '''
    Class creates VPC/Subnets/ELB/ASG for Cloudformation lab
    '''

    def __init__(self, config_dictionary):
        '''
        Method initializes the DevDeploy class and composes the CloudFormation template to deploy the solution
        @param config_dictionary [dict] collection of keyword arguments for this class implementation
        '''
        self.globals                    = config_dictionary.get('globals', {})
        self.template_args              = config_dictionary.get('template', {})

        self.template                   = Template()
        self.template.description       = self.globals.get('description', '')

        #create VPC, EC2
        self.vpc_generator = VPCGenerator(self.template_args)
        self.ec2_generator = EC2Generator(
            self.template_args,
            self.vpc_generator.vpc,
            self.vpc_generator.subnets
        )

        for resource in self.vpc_generator.resources:
            self.template.add_resource(resource)

        for resource in self.ec2_generator.resources:
            self.template.add_resource(resource)

        for output in self.ec2_generator.outputs:
            self.template.add_output(output)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='CFLab 0.1')

    config_list = arguments.get('--config-file') or ['template_config.yaml']
    #print config_list
    config_file = ''.join(config_list)
    #print config_file
    output_list = arguments.get('--output-file') or ['labenvironment.template']
    #print output_list
    output_file = ''.join(output_list)
    #print output_file

    print '\nParsing config from %s' % config_file
    with open(config_file, 'r') as f:
        config = yaml.load(f.read())

    print '\nGenerating template'
    lab = CFLab(config)

    print '\nWriting template to %s\n' % output_file
    with open(output_file, 'w') as text_file:
        json.dump(json.loads(lab.template.to_json()), text_file, indent=2, separators=(',', ': '))

    if arguments.get('--debug'):
        print lab.template.to_json()
