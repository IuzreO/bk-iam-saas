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
import os


def get_default_database_config_dict(settings_module):
    if os.getenv('GCS_MYSQL_NAME') and os.getenv('MYSQL_NAME'):
        db_prefix = settings_module.get('DB_PREFIX', '')
        if not db_prefix:
            raise EnvironmentError('no DB_PREFIX config while multiple '
                                   'databases found in environment')
    elif os.getenv('GCS_MYSQL_NAME'):
        db_prefix = 'GCS_MYSQL'
    elif os.getenv('MYSQL_NAME'):
        db_prefix = 'MYSQL'
    else:
        if settings_module.get('IS_LOCAL', False):
            return {}
        else:
            raise EnvironmentError('no database[GCS_MYSQL or MYSQL] config')
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['%s_NAME' % db_prefix],
        'USER': os.environ['%s_USER' % db_prefix],
        'PASSWORD': os.environ['%s_PASSWORD' % db_prefix],
        'HOST': os.environ['%s_HOST' % db_prefix],
        'PORT': os.environ['%s_PORT' % db_prefix],
    }
