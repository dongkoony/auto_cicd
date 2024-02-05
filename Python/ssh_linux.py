import paramiko
import json
import os
import boto3
from jinja2 import Environment, FileSystemLoader

# S3 bucket Auto Save
def save_data_to_s3(data, bucket_name, s3_key):
    s3 = boto3.client('s3')
    formatted_data = json.dumps(data, indent=4)
    s3.put_object(Body=formatted_data, Bucket=bucket_name, Key=s3_key)

# 템플릿 디렉터리 설정
TEMPLATE_DIR = r"C:\project\MTE-Project\backend\templates"

# Jinja2 환경 설정
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def get_server_info(host, port, username, password=None, key_path=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if key_path:
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(host, port=port, username=username, pkey=private_key)
        else:
            client.connect(host, port=port, username=username, password=password)
    except Exception as e:
        raise Exception(f"SSH 연결 오류: {str(e)}")
    
    stdin, stdout, stderr = client.exec_command('uname -a')
    os_info = stdout.read().decode().strip()

    stdin, stdout, stderr = client.exec_command('lscpu')
    cpu_info = stdout.read().decode().split("\n")
    cpu_details = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in cpu_info if line}

    stdin, stdout, stderr = client.exec_command('free -h')
    memory_info = stdout.read().decode().split("\n")[1].split()
    memory_info = {
        'total': memory_info[1],
        'used': memory_info[2],
        'free': memory_info[3]
    }

    stdin, stdout, stderr = client.exec_command('df -h')
    disk_info = stdout.read().decode().split("\n")[1:-1]
    disks_info = [{'filesystem': disk.split()[0], 'size': disk.split()[1], 'used': disk.split()[2], 'available': disk.split()[3]} for disk in disk_info]

    client.close()

    result = {
        'OS': os_info,
        'CPU': cpu_details,
        'Memory': memory_info,
        'Disks': disks_info
    }

    return result

def get_terraform_template(host_info):
    try:
        template = env.get_template('ec2_template.tf.j2')
    except Exception as e:
        raise Exception(f"템플릿 파일 로딩 중 오류 발생: {str(e)}")

    cpu_model = host_info.get("CPU", {}).get("Model name", "t2.micro")  # default to t2.micro if not found
    os_name = host_info.get("OS", "").split()[0]  # OS 이름

    return template.render(cpu_model=cpu_model, os_name=os_name)

def get_data_from_s3(bucket_name, s3_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    json_data = json.loads(response['Body'].read().decode('utf-8'))
    return json_data

def convert_json_to_terraform(json_data):
    return get_terraform_template(json_data)

def connect_and_save_to_s3(host, port, username, password=None, key_path=None, bucket_name="mte-project", s3_key="json(terraform)/server_info.json"):
    server_info = get_server_info(host, port, username, password, key_path)
    save_data_to_s3(server_info, bucket_name, s3_key)