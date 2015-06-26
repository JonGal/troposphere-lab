
from troposphere import cloudformation, autoscaling
from troposphere import Base64, Join, Ref
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import UpdatePolicy, AutoScalingRollingUpdate
from troposphere.ec2 import SecurityGroupRule, SecurityGroup
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb

class EC2Generator:
    '''
    Class creates ELB/ASG.. for Cloudformation lab
    '''

    def __init__(self, template_args, vpc, subnets):
        '''
        Method initializes the DevDeploy class and composes the CloudFormation template to deploy the solution
        @param config_dictionary [dict] collection of keyword arguments for this class implementation
        @param vpc [VPC] reference of the vpc for deploying the resources inside
        @param subnets [array] collection of subnets for apply the asg and elb to
        '''

        self.availability_zones = template_args['availability_zones']
        self.vpc = vpc
        self.subnets = [ Ref(subnet) for subnet in subnets['Public'] ]
        self.resources = []

        if template_args.has_key('asg'):
          self.instance_security_group = self.create_security_group(template_args['asg']['security_group'], "Instance")
          self.create_launch_configuration(template_args['asg'])
          self.create_auto_scaling_group(template_args['asg'])

        if template_args.has_key('elb'):
          self.load_balancer_security_group = self.create_security_group(template_args['elb']['security_group'], "LoadBalancer")
          self.create_load_balancer(template_args['elb'])


    def create_launch_configuration(self, asg_args):
        '''
        Method creates a Launch Configuration and adds it to the resources list
        @param asg_args [dict] collection of keyword arguments for the launch configuration
        '''
        self.launch_configuration = self.add_resource(LaunchConfiguration(
            "LaunchConfiguration",
            UserData=Base64(Join('', [
                "#!/bin/bash\n",
                "cfn-signal -e 0",
                "    --resource AutoscalingGroup",
                "    --stack ", Ref("AWS::StackName"),
                "    --region ", Ref("AWS::Region"), "\n",
                asg_args['user_data']
            ])),
            ImageId=asg_args['ami_id'],
            KeyName=asg_args['key_pair_name'],
            SecurityGroups=[Ref(self.instance_security_group)],
            InstanceType=asg_args['instance_type'],
            AssociatePublicIpAddress=True,
        ))

    def create_load_balancer(self, elb_args):
        '''
        Method creates a elastic load balancer and adds it to the resources list
        @param elb_args [dict] collection of keyword arguments for the elastic load balancer
        '''
        health_check_args = elb_args['health_check']
        health_check = elb.HealthCheck(
            Target=health_check_args['target'],
            HealthyThreshold=health_check_args['healthy_threshold'],
            UnhealthyThreshold=health_check_args['unhealthy_threshold'],
            Interval=health_check_args['interval'],
            Timeout=health_check_args['timeout'],
        )

        listener_args = elb_args['listener']
        listener = elb.Listener(
            LoadBalancerPort=listener_args['load_balancer_port'],
            InstancePort=listener_args['instance_port'],
            Protocol=listener_args['protocol'],
            InstanceProtocol=listener_args['instance_protocol'],
        )

        self.load_balancer = self.add_resource(LoadBalancer(
            "LoadBalancer",
            ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
                Enabled=True,
                Timeout=120,
            ),
            Subnets=self.subnets,
            HealthCheck=health_check,
            Listeners=[
                listener,
            ],
            CrossZone=True,
            SecurityGroups=[Ref(self.load_balancer_security_group)],
            LoadBalancerName="Cloudformation-Loadbalancer",
            Scheme="internet-facing",
        ))

    def create_auto_scaling_group(self, asg_args):
        '''
        Method creates an auto scaling group and adds it to the resources list
        @param asg_args [dict] collection of keyword arguments for the asg
        '''
        autoscaling_group = self.add_resource(AutoScalingGroup(
            "AutoscalingGroup",
            DesiredCapacity=asg_args['desired_capacity'],
            Tags=[
                Tag("Name", "CloudformationLab", True)
            ],
            LaunchConfigurationName=Ref(self.launch_configuration),
            MinSize=asg_args['min_capacity'],
            MaxSize=asg_args['max_capacity'],
            VPCZoneIdentifier=self.subnets,
            LoadBalancerNames=[Ref(self.load_balancer)],
            AvailabilityZones=self.availability_zones,
            HealthCheckType="ELB",
            HealthCheckGracePeriod=60,
            UpdatePolicy=UpdatePolicy(
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT5M',
                    MinInstancesInService=asg_args['min_capacity'],
                    MaxBatchSize='1',
                    WaitOnResourceSignals=True
                )
            )
        ))

    def create_security_group(self, security_group_args, prefix):
        '''
        Method creates a security group and adds it to the resources list
        @param security_group_args [dict] collection of keyword arguments for the security group
        '''
        security_group_ingress = []

        for ingress in security_group_args['ingress']:
            rule = SecurityGroupRule(
                IpProtocol=ingress['ip_protocol'],
                FromPort=ingress['from_port'],
                ToPort=ingress['to_port'],
                CidrIp=ingress['cidr_ip'])

            security_group_ingress.append(rule)

        return self.add_resource(
            SecurityGroup(
                prefix + 'SecurityGroup',
                GroupDescription='Enable SSH access via port 22',
                SecurityGroupIngress=security_group_ingress,
                VpcId=Ref(self.vpc),
            ))

    def add_resource(self, resource):
        '''
        Method helper for adding resources to the resource list
        @param resource [object] troposphere resource object
        '''
        self.resources.append(resource)
        return resource
