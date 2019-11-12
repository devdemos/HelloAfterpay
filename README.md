# AWS Application Stack

## About 

This repository uses Cloudformation to create an Autoscaled EC2 group, LoadBalanced by an Elastic Load Balancer to host the application.
The application has been containerised, meaing it is a running Docker image built and running locally.

By default 2 nodes are created, of which the LaunchConfig pulls the required files from S3, builds and then runs the containerised
application on port 80

## Deployment
To deploy the application stack, you will need to load the `application-template.json` file in Cloudformation.
Here you will be presented with the options to specify the subnets used by the LoadBalancer and EC2 Instances, the VPC the stack
will be installed in. The selection allows you to select from your existing subnets, therefore if you need to create new subents, do 
so before running the stack. 
Also the ability to set a CIDR range to permit access for ssh access is required, along with the ability to select one your existing ssh-keys.

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


### application-template.json
Currently the values used for referencing the S3 buckets of which files are pushed to as part of CI/CD are hardcoded.
To utilise the script for an alternative application, you will need to modify these. 
```
 "aws s3 cp s3://devdemos-repos /home/ec2-user --recursive\n",
 "cd /home/ec2-user/afterpay-application\n",
```
**NOTE** The above will be replaced using "Parameters" to eliminate the need for hardcoding, meaning the values will be set at launch
and referenced in the `userdata`, eliminating hardcoding and dependencies.

## Run Application Locally
To run the application locally you will need to first build the Docker Image 

```
docker build -t afterpay:latest .
```

Once the Image has been build you can run it, exposing port 80 to map to the image running on port 5000
```
docker run -d -p 80:5000 afterpay:latest

630bb47d72e18891502f82250f23d040d5041d1dead31a215580d4386d15c4cf
```

Verify your container is running
```
docker ps

CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                  NAMES
630bb47d72e1        afterpay:latest     "flask run --host 0.…"   12 minutes ago      Up 12 minutes       0.0.0.0:80->5000/tcp   awesome_meninsky

```
Test your application is running on port 80 using either curl or your browser
```
curl http://127.0.0.1

Hello Afterpay!
```
