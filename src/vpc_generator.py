
from troposphere import Ref, Tags

from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, InternetGateway, \
    SecurityGroupRule, SecurityGroup

class VPCGenerator:
    '''
    Class creates VPC/Subnets.. for Cloudformation lab
    '''

    def __init__(self, template_args):
        '''
        Method initializes the DevDeploy class and composes the CloudFormation template to deploy the solution
        @param config_dictionary [dict] collection of keyword arguments for this class implementation
        '''

        self.resources = []
        self.subnets = []
        self.route_tables = {}

        self.ref_stack_id = Ref('AWS::StackId')
        self.ref_region = Ref('AWS::Region')
        self.ref_stack_name = Ref('AWS::StackName')

        self.vpc = self.add_resource(
            VPC(
                'VPC',
                CidrBlock=template_args.get('vpc_cidr'),
                Tags=Tags(
                    Application=self.ref_stack_id,
                    Name="CloudformationLab")))

        self.create_internet_gateway()

        self.create_route_table(public=False)
        self.create_route_table(public=True)

        self.create_subnets(template_args.get('private_subnet_group_cidrs'), 'Private')
        self.create_subnets(template_args.get('public_subnet_group_cidrs'))


        self.create_security_group(template_args)



    def create_internet_gateway(self):
        internetGateway = self.add_resource(
            InternetGateway(
                'InternetGateway',
                Tags=Tags(
                    Application=self.ref_stack_id,
                    Name="CloudformationLab")))

        gatewayAttachment = self.add_resource(
            VPCGatewayAttachment(
                'AttachGateway',
                VpcId=Ref(self.vpc),
                InternetGatewayId=Ref(internetGateway)))

    def create_route_table(self, public=True):
        prefix = "Public" if public else "Private"
        route_table = RouteTable(
                prefix + 'RouteTable',
                VpcId=Ref(self.vpc),
                Tags=Tags(
                    Application=self.ref_stack_id,
                    Name="CloudformationLab"))
        if public:
            route = self.add_resource(
                Route(
                    prefix + 'Route',
                    DependsOn='AttachGateway',
                    GatewayId=Ref('InternetGateway'),
                    DestinationCidrBlock='0.0.0.0/0',
                    RouteTableId=Ref(route_table),
            ))

        self.route_tables[prefix] = route_table
        self.add_resource(route_table)

    def create_subnets(self, cidrs, prefix='Public'):
        for index, cidr in enumerate(cidrs):
            subnet = Subnet(
                prefix + 'Subnet' + str(index),
                CidrBlock=cidr,
                VpcId=Ref(self.vpc),
                Tags=Tags(
                    Application=self.ref_stack_id,
                    Name="CloudformationLab" + prefix + str(index)))

            subnetRouteTableAssociation = self.add_resource(
                SubnetRouteTableAssociation(
                    prefix + 'SubnetRouteTableAssociation' + str(index),
                    SubnetId=Ref(subnet),
                    RouteTableId=Ref(self.route_tables[prefix]),
                ))
            self.subnets.append(self.add_resource(
                subnet))

    def create_security_group(self, template_args):
        instanceSecurityGroup = self.add_resource(
            SecurityGroup(
                'InstanceSecurityGroup',
                GroupDescription='Enable SSH access via port 22',
                SecurityGroupIngress=[
                    SecurityGroupRule(
                        IpProtocol='tcp',
                        FromPort='22',
                        ToPort='22',
                        CidrIp='0.0.0.0/0'),
                    SecurityGroupRule(
                        IpProtocol='tcp',
                        FromPort='80',
                        ToPort='80',
                        CidrIp=template_args['ssh_cidr'])],
                VpcId=Ref(self.vpc),
            ))

    def add_resource(self, resource):
        self.resources.append(resource)
        return resource
