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
import datetime

from django.utils import timezone


def string_to_datetime(str_time, fmt="%Y-%m-%d %H:%M:%S"):
    """
    字符时间 to DateTime
    """
    return datetime.datetime.strptime(str_time, fmt)


def utc_string_to_local(str_time):
    """
    后端UTC时间转换为本地时间
    """
    t = string_to_datetime(str_time, fmt="%Y-%m-%dT%H:%M:%SZ")
    return utc_to_local(t)


def utc_to_local(utc_time):
    tz = timezone.get_current_timezone()
    dt = datetime.datetime.utcnow()
    offset_seconds = tz.utcoffset(dt).seconds

    return utc_time + datetime.timedelta(seconds=offset_seconds)


def timestamp_to_local(ts):
    t = datetime.datetime.fromtimestamp(ts)
    return utc_to_local(t)
