#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys

from abyss.config_parser import ConfigParser
from abyss.docker.docker_worker import DockerWorker
from abyss.file_manager import FileManager
from abyss.git_worker import GitWorker
from abyss import logger as LOG, email_notifier

__author__ = "Jude"

ALIYUN_DOCKER_REGISTRY = "registry.cn-zhangjiakou.aliyuncs.com/floozy"
ALIYUN_DOCKER_ACCOUNT = "季诺科技"
ALIYUN_DOCKER_PASSWORD = "H32Npgzl"


def progress(workplace, git_url, git_ref):
    file_manager = FileManager(workplace)
    file_manager.prepare()
    # Git下载
    git_worker = GitWorker(file_manager.WORKSPACE_DOWNLOAD, git_url, git_ref)
    git_worker.pull_code()
    git_worker.copy_project(file_manager.WORKSPACE_BUILD)
    abyss_config = ConfigParser(file_manager.WORKSPACE_BUILD)

    # 真正的build
    for command in abyss_config.build_beta():
        build_project = subprocess.call(LOG.debug(command), shell=True,
                                        cwd=file_manager.WORKSPACE_BUILD)
        if build_project != 0:
            LOG.error("Project build failed")
            return False
    # 处理镜像
    docker_worker = DockerWorker(
        registry=ALIYUN_DOCKER_REGISTRY,
        account=ALIYUN_DOCKER_ACCOUNT,
        password=ALIYUN_DOCKER_PASSWORD,
        image=abyss_config.image_name()
    )
    docker_worker.login()
    repo_name = ALIYUN_DOCKER_REGISTRY + "/" + abyss_config.image_name()

    docker_worker.tag(repo_name, git_worker.TAG)
    docker_worker.push(repo_name, git_worker.TAG)

    # 通知
    email_notifier.send_email(
        to=abyss_config.email(),
        project_name=abyss_config.image_name(),
        project_version=git_worker.TAG,
        message=git_worker.get_commit()[3]
    )


def build(workplace, git_url, git_ref):
    error_exit = False
    try:
        progress(workplace, git_url, git_ref)
    except Exception as e:
        LOG.error("Exception is " + str(e))
        error_exit = True
    finally:
        if error_exit:
            LOG.big_log_start("Jenkins Job Failed!")
            sys.exit(-1)
        else:
            LOG.big_log_start("Jenkins Job DONE!")