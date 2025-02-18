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
from backend.service.constants import PermissionCodeEnum, RoleType

# 角色默认权限
DEFAULT_ROLE_PERMISSIONS = {
    RoleType.SUPER_MANAGER.value: [p.value for p in PermissionCodeEnum],
    RoleType.SYSTEM_MANAGER.value: [
        PermissionCodeEnum.MANAGE_GROUP.value,
        PermissionCodeEnum.MANAGE_TEMPLATE.value,
        PermissionCodeEnum.CREATE_RATING_MANAGER.value,
        PermissionCodeEnum.MANAGE_RATING_MANAGER_MEMBER.value,
        PermissionCodeEnum.AUDIT.value,
        PermissionCodeEnum.CONFIGURE_APPROVAL_PROCESS.value,
        PermissionCodeEnum.MANAGE_SYSTEM_SETTING.value,
        PermissionCodeEnum.MANAGE_COMMON_ACTION.value,
        PermissionCodeEnum.MANAGE_SYSTEM_MANAGER_MEMBER.value,
    ],
    RoleType.RATING_MANAGER.value: [
        PermissionCodeEnum.MANAGE_GROUP.value,
        PermissionCodeEnum.MANAGE_TEMPLATE.value,
        PermissionCodeEnum.MANAGE_RATING_MANAGER_MEMBER.value,
        PermissionCodeEnum.CONFIGURE_APPROVAL_PROCESS.value,
        PermissionCodeEnum.MANAGE_COMMON_ACTION.value,
    ],
}
