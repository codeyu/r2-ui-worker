import os
import json
import subprocess
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# 加载 .env 文件
if Path('.env').exists():
    load_dotenv()

def load_config():
    try:
        with open('workers.json', 'r') as f:
            config = json.load(f)
            return config['workers']
    except Exception as e:
        print(f"Error loading workers.json: {str(e)}")
        return []

def check_and_create_bucket(bucket_name):
    try:
        # 检查 bucket 是否存在
        result = subprocess.run('npx wrangler r2 bucket list', 
                              capture_output=True, 
                              text=True,
                              shell=True,
                              encoding='utf-8')  # 指定编码为 utf-8
        
        # 解析输出查找 bucket
        existing_buckets = result.stdout.split('\n')
        bucket_exists = any(bucket_name in line for line in existing_buckets)
        
        if not bucket_exists:
            print(f"Bucket {bucket_name} not found, creating...")
            # 创建新的 bucket
            subprocess.run(f'npx wrangler r2 bucket create {bucket_name}', 
                         check=True,
                         shell=True,
                         encoding='utf-8')  # 指定编码为 utf-8
            print(f"Successfully created bucket: {bucket_name}")
        else:
            print(f"Bucket {bucket_name} already exists")
            
        return True
    except Exception as e:
        print(f"Error handling bucket {bucket_name}: {str(e)}")
        return False

def update_version_in_file(file_path):
    try:
        # 生成当前版本号 (格式: v年.月.日.时分秒)
        current_version = datetime.now().strftime('v%Y.%m.%d.%H%M%S')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式替换版本号
        import re
        new_content = re.sub(
            r"'Hello R2! v\d{4}\.\d{2}\.\d{2}(?:\.\d{6})?'",
            f"'Hello R2! {current_version}'",
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"Updated version to: {current_version}")
        return True
    except Exception as e:
        print(f"Error updating version: {str(e)}")
        return False

def check_worker_exists(worker_name):
    try:
        # 获取 worker 列表
        result = subprocess.run('npx wrangler worker list', 
                              capture_output=True, 
                              text=True,
                              shell=True,
                              encoding='utf-8')
        
        # 检查 worker 是否在列表中
        return any(worker_name in line for line in result.stdout.split('\n'))
    except Exception as e:
        print(f"Error checking worker existence: {str(e)}")
        return False

def set_secret(secret_name: str, secret_value: str):
    """设置 worker 的环境变量"""
    try:
        subprocess.run(f'npx wrangler secret put {secret_name}', 
                      input=secret_value,
                      check=True,
                      shell=True,
                      encoding='utf-8')
        print(f"Successfully set {secret_name}")
    except Exception as e:
        print(f"Failed to set {secret_name}: {str(e)}")

def deploy_worker(worker_config):
    try:
        worker_name = worker_config['worker_name']
        skip_if_exists = worker_config.get('skip_if_exists', False)  # 默认为 False
        
        # 如果设置了 skip_if_exists 并且 worker 已存在，则跳过
        if skip_if_exists and check_worker_exists(worker_name):
            print(f"Worker {worker_name} already exists, skipping deployment...")
            return True
        
        # 首先检查并创建 bucket
        if not check_and_create_bucket(worker_config['bucket_name']):
            print(f"Failed to handle bucket for {worker_name}")
            return False
        
        # 更新版本号
        if not update_version_in_file('src/index.ts'):
            print("Warning: Failed to update version number")
        
        # 读取模板文件
        with open('wrangler.toml.example', 'r') as f:
            template_content = f.read()
        
        # 替换变量
        final_content = template_content.replace('{{worker_name}}', worker_name)
        final_content = final_content.replace('{{bucket_name}}', worker_config['bucket_name'])
        
        # 写入新的 wrangler.toml
        with open('wrangler.toml', 'w') as f:
            f.write(final_content)
        
        print(f"Deploying {worker_name}...")
        
        # 执行部署命令
        subprocess.run('npm run deploy', 
                      check=True, 
                      shell=True,
                      encoding='utf-8')
        
        # 设置所有环境变量
        secrets = {
            'AUTH_KEY_SECRET': os.environ.get('AUTH_KEY_SECRET'),
            'CLOUDFLARE_API_TOKEN': os.environ.get('CLOUDFLARE_API_TOKEN'),
            'CLOUDFLARE_ACCOUNT_ID': os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        }

        for secret_name, secret_value in secrets.items():
            if secret_value:
                set_secret(secret_name, secret_value)
            else:
                print(f"Warning: {secret_name} not found in environment variables")
        
        print(f"Successfully deployed {worker_name}")
        
    except Exception as e:
        print(f"Error deploying {worker_name}: {str(e)}")
        return False
    
    return True

def main():
    # 加载配置文件
    workers_config = load_config()
    
    if not workers_config:
        print("No workers configuration found. Please check workers.json")
        return

    # 检查 AUTH_KEY_SECRET
    if not os.environ.get('AUTH_KEY_SECRET'):
        print("Missing AUTH_KEY_SECRET environment variable")
        print("Please check your .env file")
        return

    for worker_config in workers_config:
        success = deploy_worker(worker_config)
        if not success:
            print(f"Failed to deploy {worker_config['worker_name']}")

if __name__ == "__main__":
    main() 