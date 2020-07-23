import base64
import git
import boto3
import docker

local_repo_name = input("Enter the Repo Name? :: ")
print("\n")

def main():

    ####### Docker Env
    docker_client = docker.from_env()

    ####### AWS ECR login token fetch
    ecr_client = boto3.client('ecr', region_name='ap-south-1')
    ecr_credentials = (ecr_client.get_authorization_token()['authorizationData'][0])
    ecr_username = 'AWS'
    ecr_password = (base64.b64decode(ecr_credentials['authorizationToken']).replace(b'AWS:', b'').decode('utf-8'))
    ecr_url = ecr_credentials['proxyEndpoint']

    ####### Authenticate with ECR
    docker_client.login(username=ecr_username, password=ecr_password, registry=ecr_url+'/v1')
    print("ECR Login Success")
    print("\n")

    ####### Getting Repo URL
    ecr_repo_name = '{}/{}'.format(ecr_url.replace('https://', ''), local_repo_name)
    print("Pulling Docker image from repo " + ecr_repo_name)
    print("\n")
    ####### Pull image from ECR
    docker_client.images.pull(ecr_repo_name, tag='latest')
    print("Image Pull Success")
    print("\n")
    print("Starting Deployment")
    ####### Docker Run
    docker_client.containers.run(ecr_repo_name)
    print("\n")
    print("Successfully Deployed")

if __name__ == '__main__':
    main()