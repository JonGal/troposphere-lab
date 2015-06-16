class VPCGenerator:
    '''
    Class creates VPC/Subnets.. for Cloudformation lab
    '''

    def __init__(self, config_dictionary):
        '''
        Method initializes the DevDeploy class and composes the CloudFormation template to deploy the solution
        @param config_dictionary [dict] collection of keyword arguments for this class implementation
        '''

        self.resources = []
        self.vpc = {}
        self.subnets = []
