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

from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyAPIParamLocationEnum
from backend.api.management.permissions import ManagementAPIPermission
from backend.api.management.serializers import (
    ManagementGradeManagerGroupCreateSLZ,
    ManagementGroupBaseInfoUpdateSLZ,
    ManagementGroupBasicSLZ,
    ManagementGroupGrantSLZ,
    ManagementGroupMemberDeleteSLZ,
    ManagementGroupMemberSLZ,
)
from backend.api.mixins import ExceptionHandlerMixin
from backend.apps.group.audit import (
    GroupCreateAuditProvider,
    GroupDeleteAuditProvider,
    GroupMemberCreateAuditProvider,
    GroupMemberDeleteAuditProvider,
    GroupPolicyCreateAuditProvider,
    GroupUpdateAuditProvider,
)
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupAddMemberSLZ
from backend.apps.role.models import Role
from backend.audit.audit import add_audit, audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz, GroupCheckBiz, GroupCreateBean, GroupTemplateGrantBean
from backend.biz.role import RoleBiz, RoleListQuery
from backend.common.swagger import PaginatedResponseSwaggerAutoSchema, ResponseSwaggerAutoSchema
from backend.service.constants import RoleType
from backend.service.models import Subject
from backend.trans.open_management import ManagementCommonTrans


class ManagementGradeManagerGroupViewSet(ExceptionHandlerMixin, GenericViewSet):
    """用户组"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (VerifyAPIParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.GROUP_BATCH_CREATE.value),
        "list": (VerifyAPIParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.GROUP_LIST.value),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.RATING_MANAGER.value).order_by("-updated_time")

    group_biz = GroupBiz()
    group_check_biz = GroupCheckBiz()

    @swagger_auto_schema(
        operation_description="批量创建用户组",
        request_body=ManagementGradeManagerGroupCreateSLZ(label="用户组"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.ListSerializer(child=serializers.IntegerField(label="用户组ID"))},
        tags=["management.role.group"],
    )
    def create(self, request, *args, **kwargs):
        role = self.get_object()

        serializer = ManagementGradeManagerGroupCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        groups_data = serializer.validated_data["groups"]

        # 用户组名称在角色内唯一
        group_names = [g["name"] for g in groups_data]
        self.group_check_biz.batch_check_role_group_names_unique(role.id, group_names)

        groups = self.group_biz.batch_create(
            request.role.id, parse_obj_as(List[GroupCreateBean], groups_data), request.user.username
        )

        # 添加审计信息
        # TODO: 后续其他地方也需要批量添加审计时再抽象出一个batch_add_audit方法，将for循环逻辑放到方法里
        for g in groups:
            add_audit(GroupCreateAuditProvider, request, group=g)

        return Response([group.id for group in groups])

    @swagger_auto_schema(
        operation_description="用户组列表",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ManagementGroupBasicSLZ(label="用户组信息", many=True)},
        tags=["management.role.group"],
    )
    def list(self, request, *args, **kwargs):
        role = self.get_object()

        # 分页参数
        pagination = LimitOffsetPagination()
        limit = pagination.get_limit(request)
        offset = pagination.get_offset(request)

        # 查询当前分级管理员可以管理的用户组
        group_queryset = RoleListQuery(role, None).query_group()

        # 分页数据
        count = group_queryset.count()
        groups = group_queryset[offset : offset + limit]

        # 查询用户组属性
        group_attrs = self.group_biz.batch_get_attributes([g.id for g in groups])
        results = [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "attributes": group_attrs[g.id].get_attributes(),
            }
            for g in groups
        ]
        return Response({"count": count, "results": results})


class ManagementGroupViewSet(ExceptionHandlerMixin, GenericViewSet):
    """用户组"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "update": (VerifyAPIParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_UPDATE.value),
        "destroy": (VerifyAPIParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_DELETE.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    biz = GroupBiz()
    group_check_biz = GroupCheckBiz()
    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="修改用户组",
        request_body=ManagementGroupBaseInfoUpdateSLZ(label="用户组"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group"],
    )
    @view_audit_decorator(GroupUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = ManagementGroupBaseInfoUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 只更新非空值
        name = data.get("name") or group.name
        description = data.get("description") or group.description

        # 用户组名称在角色内唯一
        role = self.role_biz.get_role_by_group_id(group.id)
        self.group_check_biz.check_role_group_name_unique(role.id, name, group.id)

        # 更新
        group = self.biz.update(group, name, description, user_id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response({})

    @swagger_auto_schema(
        operation_description="删除用户组",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group"],
    )
    @view_audit_decorator(GroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()

        self.biz.delete(group.id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response({})


class ManagementGroupMemberViewSet(ExceptionHandlerMixin, GenericViewSet):
    """用户组成员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "list": (VerifyAPIParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_MEMBER_LIST.value),
        "create": (VerifyAPIParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_MEMBER_ADD.value),
        "destroy": (VerifyAPIParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_MEMBER_DELETE.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    biz = GroupBiz()
    group_check_biz = GroupCheckBiz()
    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户组成员列表",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ManagementGroupMemberSLZ(label="用户组成员信息", many=True)},
        tags=["management.role.group.member"],
    )
    def list(self, request, *args, **kwargs):
        group = self.get_object()

        # 分页参数
        pagination = LimitOffsetPagination()
        limit = pagination.get_limit(request)
        offset = pagination.get_offset(request)

        count, group_members = self.biz.list_paging_group_member(group.id, limit, offset)
        results = [one.dict(include={"type", "id", "name", "expired_at"}) for one in group_members]
        return Response({"count": count, "results": results})

    @swagger_auto_schema(
        operation_description="用户组添加成员",
        request_body=GroupAddMemberSLZ(label="用户组成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.member"],
    )
    @view_audit_decorator(GroupMemberCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = GroupAddMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        members_data = data["members"]
        expired_at = data["expired_at"]
        # 成员Dict结构转换为Subject结构，并去重
        members = list(set(parse_obj_as(List[Subject], members_data)))

        # 检测成员是否满足管理的授权范围
        role = self.role_biz.get_role_by_group_id(group.id)
        self.group_check_biz.check_role_subject_scope(role, members)
        self.group_check_biz.check_member_count(group.id, len(members))

        # 添加成员
        self.biz.add_members(group.id, members, expired_at)

        # 写入审计上下文
        audit_context_setter(group=group, members=[m.dict() for m in members])

        return Response({})

    @swagger_auto_schema(
        operation_description="用户组删除成员",
        query_serializer=ManagementGroupMemberDeleteSLZ(label="用户组成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.member"],
    )
    @view_audit_decorator(GroupMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = ManagementGroupMemberDeleteSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        members = [Subject(**{"type": data["type"], "id": _id}) for _id in data["ids"]]
        self.biz.remove_members(str(group.id), members)

        # 写入审计上下文
        audit_context_setter(group=group, members=members)

        return Response({})


class ManagementGroupPolicyViewSet(ExceptionHandlerMixin, GenericViewSet):
    """用户组权限 - 自定义权限"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (VerifyAPIParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_POLICY_GRANT.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    group_biz = GroupBiz()
    role_biz = RoleBiz()
    trans = ManagementCommonTrans()

    @swagger_auto_schema(
        operation_description="用户组授权",
        request_body=ManagementGroupGrantSLZ(label="权限"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.policy"],
    )
    @view_audit_decorator(GroupPolicyCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        group = self.get_object()
        # 序列化数据
        serializer = ManagementGroupGrantSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        system_id = data["system"]
        action_ids = [a["id"] for a in data["actions"]]
        resources = data["resources"]

        # 将授权的权限数据转为PolicyBeanList
        policy_list = self.trans.to_policy_list_for_batch_action_and_resources(system_id, action_ids, resources)

        # 组装数据进行对用户组权限处理
        system_id = data["system"]
        template = GroupTemplateGrantBean(
            system_id=system_id,
            template_id=0,  # 自定义权限template_id为0
            policies=policy_list.policies,
        )
        role = self.role_biz.get_role_by_group_id(group.id)
        self.group_biz.grant(role, group, [template])

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, policies=policy_list.policies)

        return Response({})
