# API Application Stack

A simple example of Infrastructure as Code using Cloudformation and Configuration Management using Puppet and Bash

| Name       | Value                 | 
| ---------- | ----------------------| 
| Version    | 1.0.0                 |
| Date       | 13th of November 2019 |

## About 

### Infrastructure
This repository utilises the Infrastructure as Code Tool of AWS Cloudformation to deploy a small Application Stack.
The Stack creates the following resources:

| Name                                 | Description                                                                                    | 
| ------------------------------------ | ---------------------------------------------------------------------------------------------- | 
| ApplicationAutoscalingGroup          | AWS:AutoScalingGroup used to host EC2 Instances (min of 2)                                     | 
| ApplicationLaunchConfig              | AWS::LaunchConfiguration contains config of EC2 Instances used                                 | 
| ApplicationS3BucketInstanceProfile   | AWS:InstanceProfile used by Autoscaling Group Nodes to access S3                               |
| ApplicationS3BucketRole              | AWS:IAM::Role used by Autoscaling Group Nodes to access S3                                     |
| ApplicationSecuritGroup              | AWS:EC2::SecurityGroup to secure EC2 Instances allowing access on 22 via approved CIDR         |
| LoadBalancer                         | AWS:ElasticLoadBalancing::LoadBalancer used to load balance requests to Autoscaling group nodes|
| LoadBalancerSecurityGroup            | AWS:EC2::SecurityGroup control access of ELB                                                   |

These resources are created as part of the `application-template.json` file

**Requirements** <br>
Manual creation of an S3 bucket in your is required to push and pull the required repository files for 
configuration and deployment. 

### application-template.json
Currently the values used for referencing the S3 buckets of which files are pushed to as part of CI/CD are hardcoded into this file  
***(not good practices, and scheduled to be corrected as noted below)***. <br>
To reference and modify this reference for your corresponding bucket locate the following section of code in `application-template.json` under `userdata`, replacing 
```
 "aws s3 cp s3://devdemos-repos /home/ec2-user --recursive\n",
 "cd /home/ec2-user/api-application-stack\n",
```
based on : <br>
```
 "aws s3 cp s3://<s3-bucket-name> /home/ec2-user --recursive\n",
 "cd /home/ec2-user/<s3-application-folder-name>\n",
```
**NOTE** The above will be replaced using "Parameters" to eliminate the need for hardcoding, meaning the values will be set at launch
and referenced in the `userdata`, eliminating hardcoding and dependencies.

### Application Delivery
The `api-application-stack` application is delivered via containerisation using Docker. 

By default 2 nodes are created, of which the LaunchConfig pulls the required files from S3 including the `Dockerfile`. <br>
This file then builds the required image, followed by running the image as a container exposing it on `Port 80`, by default 
the Application runs on `Port 5000` 


## Configuration Management
All packages are update to date and all pending security updates are applied against the default OS repositories at time of deployment.

Configuration Management of the Nodes is handled using `Puppet` <br>
### Puppet Config
| Name                           | Location                                                          | 
| ------------------------------ | ----------------------------------------------------------------- | 
| Puppet Version                 | `6.10.1`                                                          | 
| Puppet Install Location        | `/opt/puppetlabs/`                                                | 
| Puppet Executable              | `/opt/puppetlabs/bin/puppet `                                     | 
| Puppet Manifests               | `/etc/puppetlabs/code/environments/production/manifests `         | 
| Puppet Modules                 | `/etc/puppetlabs/code/environments/production/modules `           | 
| site.pp                        | `/etc/puppetlabs/code/environments/production/manifests/site.pp ` | 

<br>

Puppet is used to install and verify the presence of the following packages by running `/etc/puppetlabs/code/environments/production/manifests/site.pp`: <br> 
- ntp (started at boot), 
- telnet 
- mtr 
- tree

### Puppet Modules/Manifests
To add a new module run: <br>
`puppet module install <module-name>` <br>
`site.pp` is used to define site specific configuration/properties for our host, modify this file to configure modules.

### System Config 
The current System settings are also enforced using a bash script `config/config.bash` 
- IPv6 system wide has been disabled.
- Max "open files" limit across all users/processes, soft & hard, set 65535.

**NOTE**  These setting will be enforced using Puppet in the near future to remove this script.

## CI/CD 
Upon a commit this repository uses Travis CI to push the contents of the repository (excluding json, and hiddien files)
to a designated S3 Bucket. 

The Travis CI repository is set up with an AWS IAM CI user with access to write to S3 the following envrionment variables used to set its 
credentials <br>
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION

The following variable is set to advise Travis CI where to copy the contents to: <br>
- AWS_S3_BUCKET_PATH <br>
e.g. <br>
- AWS_S3_BUCKET_PATH = application_repository/application_name

**Requirements** <br>
- Creation of AWS IAM console user with access to `List` and `Write` to S3 and credentials
- Creation of the following variables in Travis CI, `Settings`  
  - AWS_ACCESS_KEY_ID = "AWS CI/CD User Credentials"
  - AWS_SECRET_ACCESS_KEY = "AWS CI/CD User Credentials"
  - AWS_DEFAULT_REGION = "AWS CI/CD User Credentials"
  - AWS_S3_BUCKET_PATH = "path of S3 Bucket and Application Name e.g. `application_repository/application_name` "


## Deployment
To deploy the application stack, you will need to load the `application-template.json` file in Cloudformation. <br>
Here you will be presented with the options to select:
- Subnets used by the LoadBalancer (from exisiting subnets)
- Subnets used by the Autoscaling Group EC2 Instances (from exisiting subnets)
- VPC (from exisiting VPCs)
- CIDR range to permit access for ssh access to EC2 Instances
- SSH-Key to assoicaite with instances (from existing ssh-keys)
  
 The selection allows you to select from your existing resources therefore if you need to create new resources(keys,subnets, etc) do so before 
 attempting to build the stack

 Give the stack a name and ensure you explicitly acknowledge its capabilities to create IAM resources.

## Access Application 
 Once the stack deployment has been created view the contents of the `Outputs`  tab to obtain the Website URL (LoadBalancer URL).<br>
 **NOTE** This does take a few minutes to be live once the instances have launched for the first time<br>

 You can either use `curl` or a `browser` to view the contents of the application. 


## Run Application Locally
To run the application locally you will need to first build the Docker Image 

```
docker build -t api-application:latest .
```

Once the Image has been build you can run it, exposing port 80 to map to the image running on port 5000
```
docker run -d -p 80:5000 api-application:latest

630bb47d72e18891502f82250f23d040d5041d1dead31a215580d4386d15c4cf
```

Verify your container is running
```
docker ps

CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                  NAMES
630bb47d72e1        api-application:latest     "flask run --host 0.…"   12 minutes ago      Up 12 minutes       0.0.0.0:80->5000/tcp   awesome_meninsky

```
Test your application is running on port 80 using either curl or your browser
```
curl http://127.0.0.1

Hello Cloud User!
```

## To-Do List / Improvements / Upgrades
- Remove Hardcoding of S3 Bucket in `Userdata`
- Set IPv6 disabel via Puppet 
- Set OpenFiles config via Puppet
- Move LoadBalancer from Classic to ALB (ie include Target Groups)
- Build Docker Image as part of Travis CI, and push to DockerHub or ECR then pull image as part of `userdata`
