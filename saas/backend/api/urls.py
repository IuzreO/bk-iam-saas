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
from django.conf.urls import include, url

urlpatterns = [
    # 授权类API
    url(r"^authorization/", include("backend.api.authorization.urls")),
    # 无权限跳转
    url(r"^application/", include("backend.api.application.urls")),
    # 初始化
    url(r"^initialization/", include("backend.api.initialization.urls")),
    # 管理类API
    url(r"^management/", include("backend.api.management.urls")),
]
