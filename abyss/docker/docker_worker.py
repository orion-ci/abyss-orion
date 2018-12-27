#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import shutil
from abyss import logger as LOG

__author__ = "Jude"


class DockerWorker:
    def __init__(self, registry, account, password, image):
        self.REGISTRY = registry
        self.ACCOUNT = account
        self.PASSWORD = password
        self.IMAGE = image

    def login(self):
        LOG.big_log_start('Start Login Docker Registry')
        result = subprocess.call(LOG.debug(
            'docker login -u {account} -p {password} {registry}'.format(
                account=self.ACCOUNT,
                password=self.PASSWORD,
                registry=self.REGISTRY)), shell=True)
        if result != 0:
            LOG.error("login failed")
            return False
        LOG.big_log_end('Login Success')

    def tag(self, repo, tag):
        LOG.big_log_start('Start TAG Docker Image')

        imageID = \
            subprocess.check_output(LOG.debug('docker images -q {image}'.format(image=self.IMAGE)),
                                    shell=True).decode('utf-8').split('\n')[0]
        if imageID == "":
            LOG.error("Image not fond: " + self.IMAGE)
            return False

        result = subprocess.call(LOG.debug(
            'docker tag {imageID} {repo}:{tag}'.format(
                imageID=imageID, repo=repo, tag=tag)), shell=True)
        if result != 0:
            LOG.error("Docker Tag failed for: ")
            return False
        LOG.big_log_end('Tag Success')

    def push(self, repo, tag):
        """
        上传镜像阶段
        :return: True or False PUSH是否成功
        """
        LOG.big_log_start('Start Push Docker Image')

        push_latest = subprocess.call(LOG.debug(
            'docker push {repo}:{tag}'.format(
                repo=repo, tag=tag)), shell=True)
        if push_latest != 0:
            LOG.error("Docker push  failed")
            return False
        LOG.big_log_end('Push Success')
        return True