# Capstone_Emeritus
# 2303-capstone-group-B

### Table of Contents
- Team Members
- Getting Started
    - Prerequisites
    - Installation
    - Configuration
    - Usage

## Team Members
- Muhammad Talha
- Umaima Siddiqui
- Muhammad Hussam
- Syed Raqim Ali Shah
- Huzaifa Ali

## Getting Started
These instructions will help you set up the project on your local machine for development and testing purposes.

## Prerequisites
Before setting up the project, make sure you have the following installed:

- Docker [a installation guide](https://docs.docker.com/get-docker/)
- Docker Compose [a installation guide](https://docs.docker.com/compose/install/)

## Installation
To install the project, follow these steps:
- Clone the repository: `git clone https://github.com/talha660033/2303-capstone-group-B.git`
- Change to the project directory: `cd 2303-capstone-group-B`

## Configuration
The project requires some configuration files to run properly. Follow these steps to set up the configuration:
- Create a config.py file in the project src/fuel_service/ directory
- add the following code in it
```
FUEL_URL = "https://www.globalpetrolprices.com/"
REDIS_HOST ="redis"
REDIS_PORT = 6379

```
- Save the file
- Create one more config.py file in the project src/online_vs_inperson_comparison_service/ directory
- add the following code in it
```
PATIENT_URL="http://patient-app.us-west-2.elasticbeanstalk.com/patient/get/"
COUNCILLOR_URL="http://councelorapp-env.eba-mdmsh3sq.us-east-1.elasticbeanstalk.com/counselor/gets/"
ACCOUNT_URL="http://accountservice.us-east-1.elasticbeanstalk.com/user/get/"
ROUTE_URL="https://api.tomtom.com/routing/1/calculateRoute/"
API_KEY = "HamdIRQ6ZeNJZj69Gy2Rru0VCqe04EoK"
PRICES_URL = "http://fuel-service:8001/fuel-price/"

```
- Save the file

## Usage
To start the project using Docker Compose, run the following command:

` docker-compose up --build `

## Disclaimer
This project is a collaborative effort of team Data Mavericks.


## Deploy on AWS EC2 Instancefollow below steps:

https://everythingdevops.dev/how-to-deploy-a-multi-container-docker-compose-application-on-amazon-ec2/ 
