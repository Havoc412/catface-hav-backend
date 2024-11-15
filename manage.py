#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
项目入口。
"""
import os
import sys

from dotenv import load_dotenv
load_dotenv("./DB/.env")  # 环境装载，全生命周期有效
load_dotenv(".env")

# from DB import Milvus
#
# def check_database_available():
#     """
#     Milvus DB 依赖检查，确保启动时，Milvus 服务启动。
#     :return:
#     """
#     milvus = Milvus()
#     print("🐱 Milivus is available.")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catface.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # check_database_available()
    main()
