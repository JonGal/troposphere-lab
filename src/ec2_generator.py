
from troposphere import cloudformation, autoscaling
from troposphere import Base64, Join, Ref
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import UpdatePolicy, AutoScalingRollingUpdate
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb

class EC2Generator:
    '''
    Class creates ELB/ASG.. for Cloudformation lab
    '''

    def __init__(self, template_args, vpc, subnets, security_group):
        '''
        Method initializes the DevDeploy class and composes the CloudFormation template to deploy the solution
        @param config_dictionary [dict] collection of keyword arguments for this class implementation
        @param vpc [VPC] reference of the vpc for deploying the resources inside
        @param subnets [array] collection of subnets for apply the asg and elb to
        '''

        self.ami_id = template_args['ami_id']
        self.key_pair_name = template_args['key_pair_name']
        self.availability_zones = template_args['availability_zones']
        self.subnets = [ Ref(subnet) for subnet in subnets['Public'] ]
        self.resources = []

        launch_configuration = self.add_resource(LaunchConfiguration(
            "LaunchConfiguration",
            UserData=Base64(Join('', [
                "#!/bin/bash\n",
                "cfn-signal -e 0",
                "    --resource AutoscalingGroup",
                "    --stack ", Ref("AWS::StackName"),
                "    --region ", Ref("AWS::Region"), "\n"
            ])),
            ImageId=self.ami_id,
            KeyName=self.key_pair_name,
            BlockDeviceMappings=[
                ec2.BlockDeviceMapping(
                    DeviceName="/dev/sda1",
                    Ebs=ec2.EBSBlockDevice(
                        VolumeSize="8"
                    )
                ),
            ],
            SecurityGroups=[Ref(security_group)],
            InstanceType="t2.micro",
        ))

        load_balancer = self.add_resource(LoadBalancer(
            "LoadBalancer",
            ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
                Enabled=True,
                Timeout=120,
            ),
            Subnets=self.subnets,
            HealthCheck=elb.HealthCheck(
                Target="HTTP:80/",
                HealthyThreshold="5",
                UnhealthyThreshold="2",
                Interval="20",
                Timeout="15",
            ),
            Listeners=[
                elb.Listener(
                    LoadBalancerPort="80",
                    InstancePort="80",
                    Protocol="HTTP",
                    InstanceProtocol="HTTP",
                ),
            ],
            CrossZone=True,
            SecurityGroups=[Ref(security_group)],
            LoadBalancerName="api-lb",
            Scheme="internet-facing",
        ))

        autoscaling_group = self.add_resource(AutoScalingGroup(
            "AutoscalingGroup",
            DesiredCapacity=1,
            Tags=[
                Tag("Name", "CloudformationLab", True)
            ],
            LaunchConfigurationName=Ref(launch_configuration),
            MinSize=1,
            MaxSize=3,
            VPCZoneIdentifier=self.subnets,
            LoadBalancerNames=[Ref(load_balancer)],
            AvailabilityZones=self.availability_zones,
            HealthCheckType="EC2",
            UpdatePolicy=UpdatePolicy(
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT5M',
                    MinInstancesInService="1",
                    MaxBatchSize='1',
                    WaitOnResourceSignals=True
                )
            )
        ))

    def add_resource(self, resource):
        self.resources.append(resource)
        return resource
