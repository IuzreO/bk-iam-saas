# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from celery import task

from backend.biz.application import ApplicationBiz
from backend.service.constants import ApplicationStatus

from .models import Application

logger = logging.getLogger("celery")


@task(ignore_result=True)
def check_or_update_application_status():
    """
    检查并更新申请单据状态
    由于对接第三方审批系统后，回调权限中心可能出现极小概率回调失败，所以需要周期任务检查补偿
    """
    # 查询未结束的申请单据
    # TODO: 是否需要过滤超过多久没处理才查询，但也有可能导致某些单据无法快速回调
    applications = Application.objects.filter(status=ApplicationStatus.PENDING.value)
    if not applications:
        return

    # 查询状态
    biz = ApplicationBiz()
    id_status_dict = biz.query_application_approval_status(applications)

    # 遍历每个申请单，进行审批处理
    for application in applications:
        try:
            status = id_status_dict.get(application.id)
            # 若查询不到，则忽略
            if status is None:
                continue
            biz.handle_application_result(application, status)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception(error)
