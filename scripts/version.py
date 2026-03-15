#!/usr/bin/env python3
import os
import re
import sys
import json
import tomllib

def update_file(file_path, pattern, replacement):
    if not os.path.exists(file_path):
        # Silently skip missing optional files
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(pattern, replacement, content)
    
    if content == new_content:
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    # print(f"✅ Updated: {file_path}") # Suppress noisy logs
    return True

def get_current_version():
    """从 pyproject.toml 获取当前版本号"""
    pyproject_path = 'backend/pyproject.toml'
    if os.path.exists(pyproject_path):
        try:
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                return data.get('project', {}).get('version', 'unknown')
        except Exception:
            pass
    return "unknown"

def set_version(version):
    v_tag = f"v{version}" if not version.startswith('v') else version
    v_num = version.lstrip('v')

    print(f"🚀 Aligning project version to {v_num} (Docker tag: {v_tag})")

    # 1. backend/pyproject.toml (唯一真实来源)
    update_file(
        'backend/pyproject.toml',
        r'(?m)^version = "[^"]+"',
        f'version = "{v_num}"'
    )

    # 2. backend/app/core/infra/config.py (更新默认值作为后备)
    update_file(
        'backend/app/core/infra/config.py',
        r'DEFAULT_VERSION = "[^"]+"',
        f'DEFAULT_VERSION = "{v_num}"'
    )

    # 3. frontend package.json files
    pkg_files = [
        'frontend/admin/package.json',
        'frontend/client/package.json',
        'frontend/docs/package.json',
        'frontend/website/package.json'
    ]
    for pkg_path in pkg_files:
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'version' in data and data.get('version') != v_num:
                    data['version'] = v_num
                    with open(pkg_path, 'w', encoding='utf-8') as f_out:
                        json.dump(data, f_out, indent=2)
                        f_out.write('\n')
                    print(f"✅ Updated: {pkg_path}")
            except Exception as e:
                print(f"❌ Error updating {pkg_path}: {e}")

    # 4. docker-compose files (仅更新 catwiki 相关镜像标签)
    compose_files = [
        'deploy/docker/docker-compose.yml',
        'deploy/docker-ee/docker-compose.yml',
        'docker-compose.dev.yml'
    ]
    # 仅匹配包含 catwiki 的镜像行
    for compose_path in compose_files:
        update_file(
            compose_path,
            r'(image: .*?catwiki.*?):[^\s]+',
            r'\1:' + v_tag
        )

    # 4.5 SDK Version (generated files / core config)
    sdk_files = [
        'frontend/admin/src/lib/sdk/CatWikiAdminSdk.ts',
        'frontend/admin/src/lib/sdk/core/OpenAPI.ts',
        'frontend/client/src/lib/sdk/CatWikiClientSdk.ts',
        'frontend/client/src/lib/sdk/core/OpenAPI.ts'
    ]
    for sdk_path in sdk_files:
        update_file(
            sdk_path,
            r"VERSION: config\?\.VERSION \?\? '[^']+'",
            f"VERSION: config?.VERSION ?? '{v_num}'"
        )
        update_file(
            sdk_path,
            r"VERSION: '[^']+'",
            f"VERSION: '{v_num}'"
        )

    # 5. Helm Chart.yaml files
    chart_files = [
        'deploy/helm/Chart.yaml',
        'deploy/helm-ee/Chart.yaml'
    ]
    for chart_path in chart_files:
        # 更新 appVersion
        update_file(
            chart_path,
            r'appVersion: "[^"]+"',
            f'appVersion: "{v_num}"'
        )
        # 更新 Chart version (保持同步提升)
        update_file(
            chart_path,
            r'(?m)^version: [^\s]+',
            f'version: {v_num}'
        )

    # 5.5 Makefile help v=x.x.x
    update_file(
        'Makefile',
        r'make set-version v=\d+\.\d+\.\d+',
        f'make set-version v={v_num}'
    )

    # 6. README files (更新快速开始中的版本号)
    readme_files = [
        'README.md',
        'README_EN.md'
    ]
    for readme_path in readme_files:
        update_file(
            readme_path,
            r'v\d+\.\d+\.\d+',
            v_tag
        )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        curr = get_current_version()
        print(f"Current project version is: {curr}")
        print("Usage: make set-version v=<version>")
        sys.exit(0)
    
    new_version = sys.argv[1]
    set_version(new_version)
