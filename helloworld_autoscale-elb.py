from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output, If, And, Not, Or, Equals, Condition
from troposphere import Parameter, Ref, Tags, Template, logs
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.ec2 import SecurityGroupIngress
from troposphere.autoscaling import AutoScalingGroup
from troposphere.ec2 import SecurityGroup, SecurityGroupRule
from troposphere.autoscaling import LaunchConfiguration

import troposphere.elasticloadbalancing as elb
t = Template()

t.set_version("2010-09-09")

VpcId = t.add_parameter(Parameter(
    "VpcId",
    Type="AWS::EC2::VPC::Id",
    Description="VpcId of your existing Virtual Private Cloud (VPC)",
))

ClusterSize = t.add_parameter(Parameter(
    "ClusterSize",
    Default="2",
    MinValue="2",
    Type="Number",
    Description="Number of Nodes in Autoscaling Group",
    MaxValue="3",
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instance",
))

SubnetId = t.add_parameter(Parameter(
    "SubnetId",
    Type="List<AWS::EC2::Subnet::Id>",
    Description="Private Subnets of your existing (VPC) for EC2 Instances",
))

ELBSubnetId = t.add_parameter(Parameter(
    "ELBSubnetId",
    Type="List<AWS::EC2::Subnet::Id>",
    Description="Public Subnets of your existing (VPC) for Load Balancer",
))


InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="t2.micro",
    Type="String",
    ConstraintDescription="Must be a valid EC2 instance type",
    Description="EC2 Instance Type (t2.micro, etc)",
    AllowedValues=["t1.micro", "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge"],
))

t.add_mapping("RegionMap",
{
 u'ap-northeast-1': {u'AMI': u'ami-0ebe863c3d16bca9d'},
 u'ap-southeast-1': {u'AMI': u'ami-043f9106e7f451340'},
 u'ap-southeast-2': {u'AMI': u'ami-08a74056dfd30c986'},
 u'us-east-1': {u'AMI': u'ami-00b882ac5193044e4'},
 u'us-east-2': {u'AMI': u'ami-09d9edae5eb90d556'},
 u'us-west-1': {u'AMI': u'ami-0e9f62b664e24851b'},
 u'us-west-2': {u'AMI': u'ami-000b133338f7f4255'}}
)

ApplicationAutoscalingGroup = t.add_resource(AutoScalingGroup(
    "ApplicationAutoscalingGroup",
    DesiredCapacity=Ref(ClusterSize),
    Tags=Tags(
        Name=Ref("AWS::StackId"),
    ),
    MinSize="2",
    MaxSize="5",
    VPCZoneIdentifier=Ref(SubnetId),
    LaunchConfigurationName=Ref("ApplicationLaunchConfig"),
    AvailabilityZones=GetAZs(Ref("AWS::Region")),
    LoadBalancerNames=[Ref("LoadBalancer")],
))

ApplicationSecGrp = t.add_resource(SecurityGroup(
    "ApplicationSecGrp",
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='22',
            ToPort='22',
            CidrIp=Ref(VpcId)),
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='80',
            ToPort='80',
            CidrIp='0.0.0.0/0')],
    VpcId=Ref(VpcId),
    GroupDescription="Enable SSH and HTTP access on the inbound port",
    Tags=Tags(
        Name=Join("dev-msts-private-", [Ref("AWS::StackName"), "-sg"]),
    )),
)

ApplicationLaunchConfig = t.add_resource(LaunchConfiguration(
    "ApplicationLaunchConfig",
    UserData=Base64(Join("", [
        '#!/bin/bash\n',
        'sudo yum -y update\n',
        'sudo yum -y install git\n',
        'sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel'
        'sudo yum -y install python37'
        'sudo yum -y install python-setuptools\n',
        'sudo yum -y install python-pip\n',
        'sudo pip install https://s3.amazonaws.com/cloudformation-examples/',
        'aws-cfn-bootstrap-latest.tar.gz\n',
        'cfn-init -s \'', Ref('AWS::StackName'),
        '\' -r Ec2Instance -c ascending'
    ],
                        )),
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(ApplicationSecGrp)],
    IamInstanceProfile="LogRoleInstanceProfile",
    InstanceType=Ref(InstanceType),
))

LoadBalancerSecurityGroup = t.add_resource(SecurityGroup(
    "LoadBalancerSecurityGroup",
    SecurityGroupIngress=[
        SecurityGroupRule(
            IpProtocol='tcp',
            FromPort='80',
            ToPort='80',
            CidrIp='0.0.0.0/0')],
    VpcId=Ref(VpcId),
    GroupDescription="Enable HTTP access",
    Tags=Tags(
        Name=Join("dev-msts-elb-", [Ref("AWS::StackName"), "-sg"]),
    )),
)

LoadBalancer = t.add_resource(LoadBalancer(
    "LoadBalancer",
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=120,
    ),
    Subnets=[Ref(ELBSubnetId)],
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
    SecurityGroups=[Ref(LoadBalancerSecurityGroup)],
    LoadBalancerName="application-lb",
    Scheme="internet-facing"
))

print(t.to_json())
