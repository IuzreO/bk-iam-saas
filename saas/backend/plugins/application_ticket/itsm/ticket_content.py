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
from typing import List

from pydantic import BaseModel

from backend.service.constants import SubjectType
from backend.service.models import (
    ApplicationAuthorizationScope,
    ApplicationGroupInfo,
    ApplicationGroupPermTemplate,
    ApplicationPolicyInfo,
    ApplicationRelatedResource,
    ApplicationResourceAttribute,
    ApplicationResourceCondition,
    ApplicationResourceInstance,
    GradeManagerApplicationContent,
    GrantActionApplicationContent,
    GroupApplicationContent,
)

from .ticket_content_tpl import FormSchemeEnum


# ---------------------------- 公共权限展示 ----------------------------
class BaseDictStrValue(BaseModel):
    label: str = ""
    value: str = ""


class BaseDictListValue(BaseModel):
    value: List[BaseDictStrValue]


class BaseText(BaseModel):
    label: str = ""
    scheme: str = FormSchemeEnum.BASE_TEXT.value
    value: str = ""


class BaseMultiLineText(BaseModel):
    label: str = ""
    scheme: str = FormSchemeEnum.BASE_TEXT.value
    value: List[BaseDictStrValue]


class ResourceUnlimited(BaseModel):
    """资源无限制展示方式"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.BASE_TEXT.value
    value: str = "无限制"

    @classmethod
    def from_resource(cls, resource_type_name: str):
        return cls(label=f"关联资源类型: {resource_type_name}")


class ResourceInstanceColumnValue(BaseModel):
    """资源实例表格每一列的值"""

    type: BaseDictStrValue
    path: BaseDictListValue

    @classmethod
    def from_instance(cls, instance: ApplicationResourceInstance):
        if not instance:
            return cls(type=BaseDictStrValue(value="-"), path=BaseDictListValue(value=[BaseDictStrValue(value="-")]))
        path_name = ["/".join([p.name for p in path]) for path in instance.path]
        return cls(
            type=BaseDictStrValue(value=f"{instance.name}({len(instance.path)})"),
            path=BaseDictListValue(value=[BaseDictStrValue(value=n) for n in path_name]),
        )


class ResourceInstanceTable(BaseModel):
    """资源实例表格"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.RESOURCE_INSTANCE_TABLE.value
    value: List[ResourceInstanceColumnValue]

    @classmethod
    def from_conditions(cls, resource_type_name: str, conditions: List[ApplicationResourceCondition]):
        values = []
        for c in conditions:
            for i in c.instances:
                values.append(ResourceInstanceColumnValue.from_instance(i))
        return cls(label=f"关联资源类型: {resource_type_name}", value=values)


class ResourceAttributeColumnValue(BaseModel):
    """资源属性表格每一列的值"""

    attributes: BaseDictListValue

    @classmethod
    def from_attributes(cls, attributes: List[ApplicationResourceAttribute]):
        if not attributes:
            return cls(attributes=BaseDictListValue(value=[BaseDictStrValue(value="-")]))
        return cls(
            attributes=BaseDictListValue(
                value=[
                    BaseDictStrValue(value=f"{attr.name}: {','.join([av.name for av in attr.values])}")
                    for attr in attributes
                ]
            )
        )


class ResourceAttributeTable(BaseModel):
    """资源属性表格"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.RESOURCE_ATTRIBUTE_TABLE.value
    value: List[ResourceAttributeColumnValue]

    @classmethod
    def from_conditions(cls, resource_type_name: str, conditions: List[ApplicationResourceCondition]):
        return cls(
            label=f"关联资源类型: {resource_type_name}",
            value=[ResourceAttributeColumnValue.from_attributes(c.attributes) for c in conditions],
        )


class ResourceBothColumnValue(BaseModel):
    """资源实例属性表格每一列的值"""

    type: BaseDictStrValue
    path: BaseDictListValue
    attributes: BaseDictListValue


class ResourceBothTable(BaseModel):
    """资源实例和属性表格"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.RESOURCE_BOTH_TABLE.value
    value: List[ResourceBothColumnValue]

    @classmethod
    def from_conditions(cls, resource_type_name: str, conditions: List[ApplicationResourceCondition]):
        values = []
        for c in conditions:
            attr = ResourceAttributeColumnValue.from_attributes(c.attributes)
            for i in c.instances:
                inst = ResourceInstanceColumnValue.from_instance(i)
                values.append(ResourceBothColumnValue(type=inst.type, path=inst.path, attributes=attr.attributes))
        return cls(label=f"关联资源类型: {resource_type_name}", value=values)


class ActionRelatedResourceTypeInfo(BaseModel):
    """权限关联的资源类型"""

    value: List[BaseDictStrValue]
    # Note: dont use `List[Union[ResourceBothTable, ResourceInstanceTable, ResourceAttributeTable, ResourceUnlimited]]`
    # reason: https://pydantic-docs.helpmanual.io/usage/types/#unions
    children: List = []

    @classmethod
    def from_resource_types(cls, related_resource_types: List[ApplicationRelatedResource]):
        # 1. 与资源实例无关
        if not related_resource_types:
            return cls(value=[BaseDictStrValue(value="无需关联实例")])
        # 遍历关联的资源类型
        values = []
        children = []
        for i in related_resource_types:
            # 2. 无限制
            if not i.condition:
                values.append(BaseDictStrValue(value=f"{i.name}: 无限制"))
                children.append(ResourceUnlimited.from_resource(i.name))
                continue

            # 判断需要用哪种表格来渲染
            has_instance = False
            has_attribute = False
            for c in i.condition:
                if c.instances:
                    has_instance = True
                if c.attributes:
                    has_attribute = True

            # 3. 仅仅资源实例
            if has_instance and not has_attribute:
                v = []
                for c in i.condition:
                    for ist in c.instances:
                        v.append(f"{len(ist.path)}个{ist.name}")
                values.append(BaseDictStrValue(value=f"{i.name}: 已选择 {', '.join(v)}"))
                children.append(ResourceInstanceTable.from_conditions(i.name, i.condition))
                continue
            # 4. 仅仅属性
            if not has_instance and has_attribute:
                len_attr = sum([len(c.attributes) for c in i.condition])
                values.append(BaseDictStrValue(value=f"{i.name}: 已设置 {len_attr} 个属性条件"))
                children.append(ResourceAttributeTable.from_conditions(i.name, i.condition))
                continue
            # 5. 存在同时有属性和实例的条件组
            len_attr = sum([len(c.attributes) for c in i.condition])
            v = []
            for c in i.condition:
                for ist in c.instances:
                    v.append(f"{len(ist.path)}个{ist.name}")
            values.append(BaseDictStrValue(vallue=f"{i.name}: 已设置 {len_attr} 个属性条件; 已选择 {', '.join(v)}"))
            children.append(ResourceBothTable.from_conditions(i.name, i.condition))

        return cls(value=values, children=children)


# ---------------------------- 自定义权限申请 ----------------------------
class ActionColumnValue(BaseModel):
    """权限表格每一列的值"""

    action: BaseDictStrValue
    related_resource_types: ActionRelatedResourceTypeInfo
    expired_display: BaseDictStrValue

    @classmethod
    def from_policy(cls, policy: ApplicationPolicyInfo):
        related_resource_types = ActionRelatedResourceTypeInfo.from_resource_types(policy.related_resource_types)
        return cls(
            action=BaseDictStrValue(value=policy.name),
            related_resource_types=related_resource_types,
            expired_display=BaseDictStrValue(value=policy.expired_display),
        )


class ActionTable(BaseModel):
    """权限表格"""

    label: str = "系统"  # 系统: xxx
    scheme: str = FormSchemeEnum.ACTION_TABLE.value
    value: List[ActionColumnValue]

    @classmethod
    def from_application(cls, content: GrantActionApplicationContent):
        values = [ActionColumnValue.from_policy(p) for p in content.policies]
        return cls(label=f"系统: {content.system.name}", value=values)


# ---------------------------- 加入用户组 ----------------------------
class GroupActionColumnValue(BaseModel):
    """用户组权限表格每一列的值"""

    action: BaseDictStrValue
    related_resource_types: ActionRelatedResourceTypeInfo

    @classmethod
    def from_policy(cls, policy: ApplicationPolicyInfo):
        related_resource_types = ActionRelatedResourceTypeInfo.from_resource_types(policy.related_resource_types)
        return cls(action=BaseDictStrValue(value=policy.name), related_resource_types=related_resource_types)


class GroupActionTable(BaseModel):
    """用户组权限表格"""

    label: str = "权限模板(系统)"  # 系统: xxx
    scheme: str = FormSchemeEnum.ACTION_TABLE_WITHOUT_EXP.value
    value: List[GroupActionColumnValue]

    @classmethod
    def from_template(cls, template: ApplicationGroupPermTemplate):
        values = [GroupActionColumnValue.from_policy(p) for p in template.policies]
        return cls(label=f"{template.name}({template.system.name})", value=values)


class GroupInfo(BaseModel):
    """用户组信息：包括名称和权限信息"""

    value: str
    children: List[GroupActionTable] = []

    @classmethod
    def from_group(cls, group: ApplicationGroupInfo):
        return cls(value=group.name, children=[GroupActionTable.from_template(t) for t in group.templates])


class GroupColumnValue(BaseModel):
    """用户组表格每一列的值"""

    id: BaseDictStrValue
    desc: BaseDictStrValue
    expired_display: BaseDictStrValue
    group_info: GroupInfo

    @classmethod
    def from_group(cls, group: ApplicationGroupInfo):
        return cls(
            id=BaseDictStrValue(value=f"#{group.id}"),
            desc=BaseDictStrValue(value=group.description),
            expired_display=BaseDictStrValue(value=group.expired_display),
            group_info=GroupInfo.from_group(group),
        )


class GroupTable(BaseModel):
    """用户组表格"""

    label: str = "用户组"
    scheme: str = FormSchemeEnum.GROUP_TABLE.value
    value: List[GroupColumnValue]

    @classmethod
    def from_application(cls, application_data: GroupApplicationContent):
        # 遍历每个用户组
        group_column_value = [GroupColumnValue.from_group(g) for g in application_data.groups]
        return cls(label="用户组", value=group_column_value)


# ---------------------------- 申请创建分级管理员 ----------------------------
class AuthScopeActionColumnValue(BaseModel):
    """权限表格每一列的值"""

    action: BaseDictStrValue
    related_resource_types: ActionRelatedResourceTypeInfo

    @classmethod
    def from_policy(cls, policy: ApplicationPolicyInfo):
        related_resource_types = ActionRelatedResourceTypeInfo.from_resource_types(policy.related_resource_types)
        return cls(action=BaseDictStrValue(value=policy.name), related_resource_types=related_resource_types)


class AuthScopeActionTable(BaseModel):
    label: str = "系统"
    scheme: str = FormSchemeEnum.ACTION_TABLE_WITHOUT_EXP.value
    value: List[AuthScopeActionColumnValue]

    @classmethod
    def from_auth_scope(cls, scope: ApplicationAuthorizationScope):
        values = [AuthScopeActionColumnValue.from_policy(p) for p in scope.policies]
        return cls(label=f"{scope.system.name}", value=values)


class GradeManagerForm(BaseModel):
    # 基本信息描述、权限表格、授权人员范围
    # Note: dont use `List[Union[AuthScopeActionTable, BaseMultiLineText, BaseText]]`
    # reason: https://pydantic-docs.helpmanual.io/usage/types/#unions
    form_data: List

    @classmethod
    def from_application(cls, application_data: GradeManagerApplicationContent):
        form_data = [
            # 基本信息
            BaseText(label="【分级管理员名称】", value=application_data.name),
            BaseText(label="【描述】", value=application_data.description if application_data.description else "--"),
            BaseText(label="【成员列表】", value=";".join([f"{m.id}({m.name})" for m in application_data.members])),
            BaseText(label="【操作和实例范围】"),
        ]

        # 渲染权限表格
        for scope in application_data.authorization_scopes:
            form_data.append(AuthScopeActionTable.from_auth_scope(scope))

        # 可授权人员范围
        users = [s for s in application_data.subject_scopes if s.type == SubjectType.USER.value]
        departments = [s for s in application_data.subject_scopes if s.type == SubjectType.DEPARTMENT.value]
        has_all_subject = SubjectType.ALL.value in {s.type for s in application_data.subject_scopes}
        if has_all_subject:
            form_data.append(BaseText(label="【可授权人员范围】", value="全员"))
        if users:
            user_values = [
                BaseDictStrValue(label="【可授权用户范围】: "),
                BaseDictStrValue(value=";".join([f"{u.id}({u.name})" for u in users])),
            ]
            form_data.append(BaseMultiLineText(value=user_values))
        if departments:
            department_values = [BaseDictStrValue(value=d.full_name) for d in departments]
            department_values.insert(0, BaseDictStrValue(label="【可授权的组织范围】: "))
            form_data.append(BaseMultiLineText(value=department_values))

        return cls(form_data=[d.dict() for d in form_data])
