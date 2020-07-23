import base64
import os
import git
import boto3
import docker

app_path = input("Enter the Full Path of Application? :: ")
print("\n")
local_repo_name = input("Enter the Repo Name? :: ")
print("\n")

def main():

#    app_path = os.environ.get('app_path')
    ####### Git repo pull
    print("Doing Git Fetch")

    repo = git.Repo(app_path)
    repo.remotes.origin.pull()

    print("\n")

    ####### Docker image build
    print("Image Build in Process")

    docker_client = docker.from_env()
    image, build_log = docker_client.images.build(path=app_path, tag=local_repo_name, rm=True)

    print("\n")
    print("Image Build Completed")
    print("\n")

    ####### AWS ECR login token fetch
    ecr_client = boto3.client('ecr', region_name='ap-south-1')
    ecr_credentials = (ecr_client.get_authorization_token()['authorizationData'][0])
    ecr_username = 'AWS'
    ecr_password = (base64.b64decode(ecr_credentials['authorizationToken']).replace(b'AWS:', b'').decode('utf-8'))
    ecr_url = ecr_credentials['proxyEndpoint']

    ####### Authenticate with ECR
    docker_client.login(username=ecr_username, password=ecr_password, registry=ecr_url+'/v1')
    print("ECR Login Success")

    ####### Tag image
    ecr_repo_name = '{}/{}'.format(ecr_url.replace('https://', ''), local_repo_name)

    image.tag(ecr_repo_name, tag='latest')
    print("Pushing Image to ECR repo " + ecr_repo_name)
    print("\n")

    ####### Push image to AWS ECR
    image_push_status = docker_client.images.push(ecr_repo_name, tag='latest')
    print(str(image_push_status))
    print("\n")
    print("Completed")

if __name__ == '__main__':
    main()
