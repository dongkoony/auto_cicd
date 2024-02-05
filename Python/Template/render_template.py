from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# 현재 스크립트 파일의 절대 경로를 기준으로 템플릿 디렉터리의 절대 경로를 설정
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
template_dir = project_root / 'Python' / 'Template'

env = Environment(loader=FileSystemLoader(template_dir))

# 템플릿 로드
template = env.get_template('ec2_instance.tf.j2')

# 변수에 값 할당
vars = {
    'ami_id': 'ami-12345678',
    'instance_type': 't2.micro'
}

# 템플릿 렌더링
output = template.render(vars)

# 렌더링된 템플릿을 파일로 저장
output_path = project_root / 'Python' / 'Template' / 'output.tf'
with open(output_path, 'w') as f:
    f.write(output)
