from troposphere import Template, iam, Ref, Parameter, ec2
from awacs.aws import Allow, Policy, Principal, Statement, Action
from awacs.sts import AssumeRole

t = Template()

t.set_version("2010-09-09")
t.set_description('EC2 instance with s3 read access')


policy = iam.Policy(
    PolicyName='S3ReadPolicy',
    PolicyDocument= Policy(
        Statement=[
            Statement(
                Sid='S3Access',
                Effect=Allow,
                Action=[
                    Action('s3', 'List*'),
                    Action('s3', 'Get*'),
                ],
                Resource=['arn:aws:s3:::*']
            )
        ]
    )
)

print(t.to_json())