class EC2Generator:
    '''
    Class creates ELB/ASG.. for Cloudformation lab
    '''

    def __init__(self, config_dictionary, vpc, subnets):
        '''
        Method initializes the DevDeploy class and composes the CloudFormation template to deploy the solution
        @param config_dictionary [dict] collection of keyword arguments for this class implementation
        @param vpc [VPC] reference of the vpc for deploying the resources inside
        @param subnets [array] collection of subnets for apply the asg and elb to
        '''

        self.resources = []
