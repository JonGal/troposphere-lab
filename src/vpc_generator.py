
from troposphere import Ref, Tags

from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, InternetGateway, \
    SecurityGroupRule, SecurityGroup
import re

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
        self.subnets = {"Public": [], "Private": []}
        self.route_tables = {}

        self.ref_stack_id = Ref('AWS::StackId')
        self.ref_region = Ref('AWS::Region')
        self.ref_stack_name = Ref('AWS::StackName')

        self.create_vpc(template_args)

        self.create_internet_gateway()

        self.create_route_table(public=False)
        self.create_route_table(public=True)

        self.create_subnets(template_args)

        self.create_security_group(template_args)


    def create_vpc(self, template_args):
        self.vpc = self.add_resource(
            VPC(
                'VPC',
                CidrBlock=template_args.get('vpc_cidr'),
                Tags=Tags(
                    Application=self.ref_stack_id,
                    Name="CloudformationLab")))

    def create_internet_gateway(self):
        internet_gateway = self.add_resource(
            InternetGateway(
                'InternetGateway',
                Tags=Tags(
                    Application=self.ref_stack_id,
                    Name="CloudformationLab")))

        gateway_attachment = self.add_resource(
            VPCGatewayAttachment(
                'AttachGateway',
                VpcId=Ref(self.vpc),
                InternetGatewayId=Ref(internet_gateway)))

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

    def create_subnets(self, template_args):
        azs = template_args.get('availability_zones')
        base_cidr = template_args.get('vpc_cidr')
        regex = re.compile('(\d{0,3}\.\d{0,3})\.\d{0,3}(\.\d{0,3}).*')

        for index, az in enumerate(azs):

            for privates in range(0,template_args.get('private_subnets_per_az')):
                octet = str((index * template_args.get('private_subnets_per_az')) + privates + 1 ) + "0"
                cidr = regex.sub(r'\1.%s\2/24' % octet, base_cidr)
                subnet = self._create_subnet(az, cidr, octet, False)

                self.subnets["Private"].append(self.add_resource(
                    subnet))

            for publics in range(0,template_args.get('public_subnets_per_az')):
                octet = str((index * template_args.get('public_subnets_per_az')) + publics + 1 )
                cidr = regex.sub(r'\1.%s\2/24' % octet, base_cidr)
                subnet = self._create_subnet(az, cidr, octet, True)

                self.subnets["Public"].append(self.add_resource(
                    subnet))



    def _create_subnet(self, az, cidr, suffix, public=True):
        prefix = "Public" if public else "Private"
        subnet = Subnet(
            prefix + 'Subnet' + suffix,
            CidrBlock=cidr,
            VpcId=Ref(self.vpc),
            AvailabilityZone=az,
            Tags=Tags(
                Application=self.ref_stack_id,
                Name="CloudformationLab" + prefix + suffix))

        subnet_route_table_association = self.add_resource(
            SubnetRouteTableAssociation(
                prefix + 'SubnetRouteTableAssociation' + suffix,
                SubnetId=Ref(subnet),
                RouteTableId=Ref(self.route_tables[prefix]),
            ))
        return subnet

    def create_security_group(self, template_args):
        self.instance_security_group = self.add_resource(
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
