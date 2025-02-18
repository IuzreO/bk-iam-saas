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
import json
from typing import Dict, List, Union

from django.db import models
from django.utils.functional import cached_property

from backend.common.models import BaseModel
from backend.service.constants import RoleRelatedObjectType, RoleScopeType, RoleSourceTypeEnum, RoleType, SubjectType
from backend.util.json import json_dumps

from .constants import DEFAULT_ROLE_PERMISSIONS
from .managers import RoleRelatedObjectManager, RoleUserManager


class Role(BaseModel):
    """
    角色
    """

    name = models.CharField("名称", max_length=128)
    name_en = models.CharField("英文名", max_length=128, default="")
    description = models.CharField("描述", max_length=255, default="")
    type = models.CharField("类型", max_length=32, choices=RoleType.get_choices())
    code = models.CharField("标志", max_length=64, default="")

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
        ordering = ["-id"]

    @property
    def system_permission_enabled_content(self):
        enabled_content, _ = RoleUserSystemPermission.objects.get_or_create(role_id=self.id)
        return enabled_content

    @property
    def members(self):
        return list(RoleUser.objects.filter(role_id=self.id).values_list("username", flat=True))

    @property
    def permissions(self):
        return DEFAULT_ROLE_PERMISSIONS[self.type]


class RoleUser(BaseModel):
    """
    角色的用户
    """

    role_id = models.IntegerField("角色ID")
    username = models.CharField("用户id", max_length=64)

    objects = RoleUserManager()

    class Meta:
        verbose_name = "角色的用户"
        verbose_name_plural = "角色的用户"
        ordering = ["id"]
        index_together = ["role_id"]


class RoleUserSystemPermission(BaseModel):
    """
    角色里的用户是否拥有对应接入系统的超级权限
    """

    role_id = models.IntegerField("角色ID")
    content = models.TextField("限制内容", default='{"enabled_users": [], "global_enabled": false}')

    @cached_property
    def enabled_detail(self) -> Dict[str, Union[List[str], bool]]:
        return json.loads(self.content)

    @property
    def enabled_users(self) -> List[str]:
        return self.enabled_detail["enabled_users"]

    @property
    def global_enabled(self) -> bool:
        return self.enabled_detail["global_enabled"]

    @classmethod
    def get_enabled_detail(cls, role_id: int):
        enabled_content, _ = cls.objects.get_or_create(role_id=role_id)
        enabled_detail = enabled_content.enabled_detail
        return enabled_detail

    @classmethod
    def update_global_enabled(cls, role_id: int, global_enabled: bool):
        enabled_detail = cls.get_enabled_detail(role_id)
        enabled_detail["global_enabled"] = global_enabled
        cls.objects.filter(role_id=role_id).update(content=json_dumps(enabled_detail))

    @classmethod
    def add_enabled_users(cls, role_id: int, username: str):
        enabled_detail = cls.get_enabled_detail(role_id)
        enabled_detail["enabled_users"].append(username)
        cls.objects.filter(role_id=role_id).update(content=json_dumps(enabled_detail))

    @classmethod
    def delete_enabled_users(cls, role_id: int, username: str):
        enabled_detail = cls.get_enabled_detail(role_id)
        enabled_detail["enabled_users"].remove(username)
        cls.objects.filter(role_id=role_id).update(content=json_dumps(enabled_detail))


class Permission(models.Model):
    """
    权限
    """

    name = models.CharField("名称", max_length=64)
    name_en = models.CharField("英文名", max_length=64, default="")
    code = models.CharField("标志", max_length=64)

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = "权限"


class RolePerm(models.Model):
    """
    角色的权限
    """

    role_id = models.IntegerField("角色ID")
    perm_id = models.IntegerField("权限ID")

    class Meta:
        verbose_name = "角色的权限"
        verbose_name_plural = "角色的权限"
        index_together = ["role_id"]


class RoleScope(models.Model):
    """
    角色的限制范围
    """

    role_id = models.IntegerField("角色ID")
    type = models.CharField("限制类型", max_length=32, choices=RoleScopeType.get_choices())
    content = models.TextField("限制内容")

    class Meta:
        verbose_name = "角色的限制范围"
        verbose_name_plural = "角色的限制范围"
        index_together = ["role_id"]


class ScopeSubject(models.Model):
    """
    subject的限制冗余
    """

    role_scope_id = models.IntegerField("角色限制ID")
    role_id = models.IntegerField("角色ID")
    subject_type = models.CharField("授权对象类型", max_length=32, choices=SubjectType.get_choices())
    subject_id = models.CharField("授权对象ID", max_length=64)

    class Meta:
        verbose_name = "subject限制"
        verbose_name_plural = "subject限制"


class RoleRelatedObject(BaseModel):
    """
    角色关联资源
    """

    role_id = models.IntegerField("角色ID")
    object_type = models.CharField("对象类型", max_length=32, choices=RoleRelatedObjectType.get_choices())
    object_id = models.IntegerField("对象ID")

    objects = RoleRelatedObjectManager()

    class Meta:
        verbose_name = "角色关联资源"
        verbose_name_plural = "角色关联资源"
        unique_together = ["role_id", "object_type", "object_id"]


class RoleCommonAction(BaseModel):
    """
    角色常用操作
    """

    role_id = models.IntegerField("角色ID")
    system_id = models.CharField("系统ID", max_length=32)
    name = models.CharField("名称", max_length=128)
    name_en = models.CharField("名称EN", max_length=128, default="")
    _action_ids = models.TextField("操作列表", db_column="action_ids")

    class Meta:
        verbose_name = "角色常用操作"
        verbose_name_plural = "角色常用操作"
        ordering = ["id"]
        index_together = ["role_id", "system_id"]

    @property
    def action_ids(self):
        return json.loads(self._action_ids)

    @action_ids.setter
    def action_ids(self, action_ids):
        self._action_ids = json_dumps(action_ids)


class RoleSource(BaseModel):
    """
    角色创建来源
    """

    role_id = models.IntegerField("角色ID", unique=True)
    source_type = models.CharField("来源类型", max_length=32, choices=RoleSourceTypeEnum.get_choices())
    source_system_id = models.CharField("来源系统", max_length=32, default="")


class AnonymousRole:
    id = 0
    pk = 0
    name = "STAFF"
    name_en = ""
    description = ""
    type = RoleType.STAFF.value
    code = ""

    system_permission_enabled_content = RoleUserSystemPermission(
        id=0, role_id=0, content='{"enabled_users": [], "global_enabled": false}'
    )
    members: List[str] = []

    def __str__(self):
        return "AnonymousRole"

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return 0  # instances always return the same hash value

    def __int__(self):
        raise TypeError("Cannot cast AnonymousRole to int. Are you trying to use it in place of Role?")

    def save(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousRole.")

    def delete(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousRole.")

    @property
    def permissions(self):
        return []
