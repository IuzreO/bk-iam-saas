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
from collections import defaultdict
from typing import List, Optional

from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from pydantic import BaseModel, parse_obj_as

from backend.apps.application.models import Application
from backend.apps.group.models import Group
from backend.apps.organization.models import Department, DepartmentMember, User
from backend.apps.role.models import Role, RoleRelatedObject, RoleUser, ScopeSubject
from backend.apps.template.models import PermTemplate
from backend.biz.policy import (
    ConditionBean,
    InstanceBean,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    PolicyBeanList,
    ThinSystem,
)
from backend.common.error_codes import APIException, error_codes
from backend.service.constants import (
    ACTION_ALL,
    SUBJECT_ALL,
    SUBJECT_TYPE_ALL,
    SYSTEM_ALL,
    ApplicationStatus,
    ApplicationTypeEnum,
    RoleRelatedObjectType,
    RoleScopeSubjectType,
    RoleType,
    SubjectType,
)
from backend.service.models import Attribute, Subject, System
from backend.service.role import AuthScopeAction, AuthScopeSystem, RoleInfo, RoleService
from backend.service.system import SystemService

logger = logging.getLogger("app")


class RoleInfoBean(RoleInfo):
    pass


class AuthScopeSystemBean(BaseModel):
    system: ThinSystem
    actions: List[PolicyBean]


class RoleBiz:
    svc = RoleService()
    system_svc = SystemService()

    get_role_by_group_id = RoleService.__dict__["get_role_by_group_id"]
    list_system_common_actions = RoleService.__dict__["list_system_common_actions"]
    list_user_role = RoleService.__dict__["list_user_role"]
    list_user_role_for_system = RoleService.__dict__["list_user_role_for_system"]
    add_grade_manager_members = RoleService.__dict__["add_grade_manager_members"]
    list_subject_scope = RoleService.__dict__["list_subject_scope"]
    list_auth_scope = RoleService.__dict__["list_auth_scope"]
    list_by_ids = RoleService.__dict__["list_by_ids"]

    transfer_groups_role = RoleService.__dict__["transfer_groups_role"]

    def get_role_scope_include_user(self, role_id: int, username: str) -> Optional[Role]:
        """
        查询授权范围包含用户的角色
        """
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return None

        checker = RoleSubjectScopeChecker(role)
        try:
            checker.check([Subject(type=SubjectType.USER.value, id=username)])
            return role
        except APIException:
            return None

    def create(self, info: RoleInfoBean, creator: str) -> Role:
        """
        创建分级管理员
        """
        return self.svc.create(info, creator)

    def update(self, role: Role, info: RoleInfoBean, updater: str, partial=False):
        """
        更新分级管理员
        """
        return self.svc.update(role, info, updater, partial)

    def modify_system_manager_members(self, role_id: int, members: List[str]):
        """修改系统管理员的成员"""
        self.svc.modify_system_manager_members(role_id, members)

    def modify_system_manager_member_system_permission(self, role_id: int, need_sync_backend_role: bool):
        """系统管理员的成员系统权限是否开启"""
        self.svc.modify_system_manager_member_system_permission(role_id, need_sync_backend_role)

    def add_super_manager_member(self, username: str, need_sync_backend_role: bool):
        """
        添加超级管理员成员
        """
        self.svc.add_super_manager_member(username, need_sync_backend_role)

    def delete_super_manager_member(self, username: str):
        """删除超级管理员成员"""
        self.svc.delete_super_manager_member(username)

    def delete_member(self, role_id: int, username: str):
        """
        角色删除成员
        """
        self.svc.delete_member(role_id, username)

    def update_super_manager_member_system_permission(self, username: str, need_sync_backend_role: bool):
        """
        更新超级管理员成员的系统权限
        """
        self.svc.update_super_manager_member_system_permission(username, need_sync_backend_role)

    def list_auth_scope_bean(self, role_id: int) -> List[AuthScopeSystemBean]:
        """
        查询角色的auth授权范围Bean
        """
        auth_systems = self.svc.list_auth_scope(role_id)
        system_list = self.system_svc.new_system_list()

        auth_system_beans = []
        for auth_system in auth_systems:
            auth_system_bean = self._gen_auth_scope_bean(auth_system, system_list)
            if not auth_system_bean:
                continue
            auth_system_beans.append(auth_system_bean)

        return auth_system_beans

    def _gen_auth_scope_bean(self, auth_system: AuthScopeSystem, system_list) -> Optional[AuthScopeSystemBean]:
        system = (
            system_list.get(auth_system.system_id)
            if auth_system.system_id != SYSTEM_ALL
            else System(id=SYSTEM_ALL, name="", name_en="", description="", description_en="")
        )
        if not system:
            return None

        if len(auth_system.actions) == 1 and auth_system.actions[0].id == ACTION_ALL:
            policies = [PolicyBean.parse_obj(auth_system.actions[0])]
        else:
            policies = PolicyBeanList(
                auth_system.system_id,
                parse_obj_as(List[PolicyBean], auth_system.actions),
                need_fill_empty_fields=True,
            ).policies

        return AuthScopeSystemBean(system=ThinSystem.parse_obj(system), actions=policies)

    def get_auth_scope_bean_by_system(self, role_id: int, system_id: str) -> Optional[AuthScopeSystemBean]:
        """
        获取指定系统的auth授权范围Bean
        """
        auth_systems = self.svc.list_auth_scope(role_id)
        system_list = self.system_svc.new_system_list()

        for auth_system in auth_systems:
            if auth_system.system_id == system_id:
                return self._gen_auth_scope_bean(auth_system, system_list)

        return None

    def inc_update_auth_scope(self, role_id: int, system_id: str, incr_policies: List[PolicyBean]):
        """增量更新分级管理员的授权范围
        Note: 这里没有判断是否已经包含了，而是直接合并添加，比如已有父资源，则增量里有子资源也会添加
        需要去除包含的，则单独在外层调用RoleAuthorizationScopeChecker进行判断去除，然后提取增量数据后再调用
        """
        # 增量数据为空，无需更新
        if len(incr_policies) == 0:
            return
        # 转为PolicyList，便于进行数据合并操作
        incr_policy_list = PolicyBeanList(system_id=system_id, policies=incr_policies, need_fill_empty_fields=True)

        # 查询已有的可授权范围
        auth_scopes = self.svc.list_auth_scope(role_id)

        # 遍历，查找需要修改的数据和对应位置
        need_modified_policy_list = PolicyBeanList(system_id=system_id, policies=[])
        index = -1
        for idx, auth_scope in enumerate(auth_scopes):
            if auth_scope.system_id == system_id:
                index = idx
                need_modified_policy_list = PolicyBeanList(
                    system_id=system_id, policies=parse_obj_as(List[PolicyBean], auth_scope.actions)
                )
                break

        # 合并增量数据
        need_modified_policy_list.add(incr_policy_list)

        # 修改已有的可授权范围
        new_auth_scope = AuthScopeSystem(
            system_id=system_id, actions=parse_obj_as(List[AuthScopeAction], need_modified_policy_list.policies)
        )
        if index == -1:
            auth_scopes.append(new_auth_scope)
        else:
            auth_scopes[index] = new_auth_scope

        # 变更可授权的权限范围
        self.svc.update_role_auth_scope(role_id, auth_scopes)


class RoleCheckBiz:
    def check_unique_name(self, new_name: str, old_name: str = ""):
        """
        检查分级管理员名称唯一性
        仅仅检查分级管理员，若分级管理员类型是系统管理员和超级管理员则不检查
        包括申请中需要检查
        """
        # 如果新名称与旧名称一致，说明名称没改变
        if new_name == old_name:
            return

        # 新名称已经有对应的分级管理员，则不可以
        if Role.objects.filter(name=new_name).exists():
            raise error_codes.CONFLICT_ERROR.format(_("名称[{}]已存在，请修改为其他名称").format(new_name), True)

        # 检测是否已经有正在申请中的
        applications = Application.objects.filter(
            type__in=[
                ApplicationTypeEnum.CREATE_RATING_MANAGER.value,
                ApplicationTypeEnum.UPDATE_RATING_MANAGER.value,
            ],
            status=ApplicationStatus.PENDING.value,
        )
        names = {i.data.get("name") for i in applications}
        if new_name in names:
            raise error_codes.CONFLICT_ERROR.format(_("正在申请的单据中名称[{}]已存在，请修改为其他名称，或等单据被处理后再提交").format(new_name), True)


class RoleListQuery:
    system_svc = SystemService()
    role_svc = RoleService()

    def __init__(self, role: Role, user: Optional[User] = None) -> None:
        self.role = role
        self.user = User.objects.get(username=user.username) if user else None

    def list_system(self) -> List[System]:
        """
        查询系统列表
        """
        systems = self.system_svc.list()

        if self.role.type == RoleType.STAFF.value:
            return systems

        scopes = self.role_svc.list_auth_scope(self.role.id)
        system_set = {s.system_id for s in scopes}
        if SYSTEM_ALL in system_set:
            return systems
        return [s for s in systems if s.id in system_set]

    def list_scope_action_id(self, system_id: str) -> List[str]:
        """
        查询操作列表
        """
        if self.role.type == RoleType.STAFF.value:
            return [ACTION_ALL]

        scopes = self.role_svc.list_auth_scope(self.role.id)
        systems = {s.system_id: {a.id for a in s.actions} for s in scopes}
        if system_id not in systems and SYSTEM_ALL not in systems:
            return []

        if SYSTEM_ALL in systems or ACTION_ALL in systems[system_id]:
            return [ACTION_ALL]

        return list(systems[system_id])

    def query_template(self):
        """
        查询模板列表
        """
        assert self.user

        template_ids = self._get_role_related_object_ids(RoleRelatedObjectType.TEMPLATE.value)
        return PermTemplate.objects.filter(id__in=template_ids)

    def query_group(self):
        """
        查询用户组列表
        """
        group_ids = self._get_role_related_object_ids(RoleRelatedObjectType.GROUP.value)
        return Group.objects.filter(id__in=group_ids)

    def _get_role_related_object_ids(self, object_type: str) -> List[int]:
        if self.role.type != RoleType.STAFF.value:
            return list(
                RoleRelatedObject.objects.filter(role_id=self.role.id, object_type=object_type).values_list(
                    "object_id", flat=True
                )
            )

        assert self.user
        mgr_ids = self._list_authorization_scope_include_user_role_ids()
        # 查询 所有这些管理员创建的 对象 ids
        return list(
            RoleRelatedObject.objects.filter(role_id__in=mgr_ids, object_type=object_type).values_list(
                "object_id", flat=True
            )
        )

    def _list_authorization_scope_include_user_role_ids(self):
        """
        授权范围包含用户的角色id列表
        """
        # 1. 查询普通用户所在的部门id
        department_ids = self.user.ancestor_department_ids

        # 2. 查询 subjects 相关的分级管理员
        grade_mgr_ids = ScopeSubject.objects.filter(
            Q(subject_type=RoleScopeSubjectType.DEPARTMENT.value, subject_id__in=department_ids)
            | Q(subject_type=RoleScopeSubjectType.USER.value, subject_id=self.user.username)  # noqa
            | Q(subject_type=SUBJECT_TYPE_ALL, subject_id=SUBJECT_ALL)  # noqa
        ).values_list("role_id", flat=True)

        # 3. 查询 超级管理员 + 系统管理员的 ids
        super_ids = Role.objects.filter(
            Q(type=RoleType.SUPER_MANAGER.value) | Q(type=RoleType.SYSTEM_MANAGER.value)
        ).values_list("id", flat=True)

        return list(grade_mgr_ids) + list(super_ids)

    def list_role_scope_include_user(self):
        """
        授权范围包含用户的角色
        """
        assert self.user

        mgr_ids = self._list_authorization_scope_include_user_role_ids()
        return self.role_svc.list_by_ids(mgr_ids)

    def query_grade_manager(self):
        """
        查询分级管理员列表
        """
        # 作为超级管理员时，可以管理所有分级管理员
        if self.role.type == RoleType.SUPER_MANAGER.value:
            return Role.objects.filter(type=RoleType.RATING_MANAGER.value).order_by("-updated_time")
        # 作为个人时，只能管理加入的的分级管理员
        if self.role.type == RoleType.STAFF.value:
            assert self.user

            role_ids = list(RoleUser.objects.filter(username=self.user.username).values_list("role_id", flat=True))
            return Role.objects.filter(type=RoleType.RATING_MANAGER.value, id__in=role_ids).order_by("-updated_time")

        return Role.objects.none()


class RoleObjectRelationChecker:
    """
    角色对象关系检查
    """

    def __init__(self, role: Role):
        self.role = role

    def _check_object(self, obj_type: str, obj_id: int) -> bool:
        return RoleRelatedObject.objects.filter(role_id=self.role.id, object_type=obj_type, object_id=obj_id).exists()

    def _check_object_ids(self, obj_type: str, obj_ids: List[int]) -> bool:
        count = RoleRelatedObject.objects.filter(
            role_id=self.role.id, object_type=obj_type, object_id__in=obj_ids
        ).count()
        return count == len(set(obj_ids))

    def check_group(self, obj) -> bool:
        return self._check_object(RoleRelatedObjectType.GROUP.value, obj.id)

    def check_template(self, obj) -> bool:
        return self._check_object(RoleRelatedObjectType.TEMPLATE.value, obj.id)

    def check_group_ids(self, ids: List[int]) -> bool:
        return self._check_object_ids(RoleRelatedObjectType.GROUP.value, ids)


class RoleAuthorizationScopeChecker:
    """
    角色模板授权范围检查
    """

    svc = RoleService()

    def __init__(self, role: Role):
        self.role = role
        if self.role.type == RoleType.STAFF.value:
            raise error_codes.FORBIDDEN  # 普通用户不能授权

    @cached_property
    def system_action_scope(self):
        scopes = self.svc.list_auth_scope(self.role.id)
        return {s.system_id: {a.id: a for a in s.actions} for s in scopes}

    def _check_system_in_scope(self, system_id):
        system_action_scope = self.system_action_scope
        if system_id not in system_action_scope and SYSTEM_ALL not in system_action_scope:
            raise error_codes.FORBIDDEN.format(message=_("{} 系统不在角色的授权范围中").format(system_id), replace=True)

    def _check_action_in_scope(self, system_id, action_id):
        system_action_scope = self.system_action_scope
        if SYSTEM_ALL in system_action_scope or ACTION_ALL in system_action_scope[system_id]:
            return ACTION_ALL

        action_scope = system_action_scope[system_id]
        if action_id not in action_scope:
            raise error_codes.FORBIDDEN.format(
                message=_("{} 操作不在角色的授权范围内").format(action_id), replace=True
            )  # 操作不在授权范围内

        return ""

    def remove_path_outside_scope(
        self, system_id: str, action_id: str, paths: List[List[PathNodeBean]]
    ) -> List[List[PathNodeBean]]:
        """
        移除不在授权范围内的路径
        """
        if self._check_action_in_scope(system_id, action_id) == ACTION_ALL:
            return paths

        policy_scope = PolicyBean.parse_obj(self.system_action_scope[system_id][action_id])
        for rrt in policy_scope.related_resource_types:
            scope_str_paths = []
            inside_paths = []
            for path_list in rrt.iter_path_list(ignore_attribute=True):
                sp = path_list.to_path_string()
                # 处理路径中存在*的情况
                if sp.endswith(",*/"):
                    sp = sp[:-2]

                scope_str_paths.append(sp)

            for path in paths:
                if self._is_path_match_scope_paths(path, scope_str_paths):
                    inside_paths.append(path)

            paths = inside_paths

        return paths

    def _is_path_match_scope_paths(self, path: List[PathNodeBean], scope_str_paths: List[str]):
        tp = PathNodeBeanList(path).to_path_string()
        for sp in scope_str_paths:
            if tp.startswith(sp):
                return True
        return False

    def check_policies(self, system_id: str, policies: List[PolicyBean]):
        """
        检查重构后的Policy结构
        """
        self._check_system_in_scope(system_id)
        for p in policies:
            self._check_policy_in_scope(system_id, p)

    def list_not_match_policy(self, system_id: str, policies: List[PolicyBean]) -> List[PolicyBean]:
        """与check_policies的检测逻辑一样，只是不直接抛异常，而是返回不满足的策略"""
        try:
            self._check_system_in_scope(system_id)
        except APIException:
            # 整个系统都不满足，则返回原有所有策略
            return policies

        # 遍历每条权限进行判断
        not_match_policies = []
        for p in policies:
            try:
                self._check_policy_in_scope(system_id, p)
            except APIException:
                not_match_policies.append(p)

        return not_match_policies

    def _check_policy_in_scope(self, system_id, policy: PolicyBean):
        if self._check_action_in_scope(system_id, policy.action_id) == ACTION_ALL:
            return

        policy_scope = self.system_action_scope[system_id][policy.action_id]
        differ = ActionScopeDiffer(policy, PolicyBean.parse_obj(policy_scope))
        if not differ.diff():
            raise error_codes.FORBIDDEN.format(
                message=_("{} 操作配置的资源范围不满足角色的授权范围").format(policy.action_id), replace=True
            )  # 操作的资源选择范围不满足分级管理员的资源选择范围

    def check_systems(self, system_ids: List[str]):
        """检查系统是否符合角色的管理范围"""
        for system_id in system_ids:
            self._check_system_in_scope(system_id)

    def check_actions(self, system_id: str, action_ids: List[str]):
        self._check_system_in_scope(system_id)

        role_actions = RoleListQuery(self.role).list_scope_action_id(system_id)
        if ACTION_ALL in role_actions:
            return

        action_id_set = set(role_actions)
        for action_id in action_ids:
            if action_id not in action_id_set:
                raise error_codes.FORBIDDEN.format(
                    message=_("{} 操作不在角色的授权范围内").format(action_id), replace=True
                )  # 操作不在授权范围内


class RoleSubjectScopeChecker:
    """
    角色用户组授权范围检查
    """

    svc = RoleService()

    def __init__(self, role: Role):
        self.role = role

    # TODO 代码优化, 圈复杂度28, 规范要求20以下
    def check(self, subjects: List[Subject], raise_exception: bool = True) -> List[Subject]:
        if self.role.type == RoleType.STAFF.value:
            raise error_codes.FORBIDDEN  # 普通用户不能授权

        scopes = self.svc.list_subject_scope(self.role.id)
        scope_set = {(i.type, i.id) for i in scopes}

        # 任意则直接返回
        if (SUBJECT_TYPE_ALL, SUBJECT_ALL) in scope_set:
            return subjects

        # 若scope里已存在，则无需再校验
        need_check_subject = [s for s in subjects if (s.type, s.id) not in scope_set]
        # 若没有需要再校验的，则直接返回
        if not need_check_subject:
            return subjects

        # 剩下需要的校验的subject，若是用户则需要其所有所在部门(包括祖先部门)在scope部门里，若是部门则需要其祖先部门在scope部门里
        department_scopes = {int(s.id) for s in scopes if s.type == SubjectType.DEPARTMENT.value}

        # 【对于部门】则需要查询其祖先是否在department_scopes里，
        # 【对于用户】则需要查询用户在的所有部门的祖先是否在department_scopes里
        # 所有需要查询祖先的部门，为了减少DB查询，会先获取用户和部门需要查询祖先的所有部门，然后再一次性查询DB
        need_query_ancestor_departments = set()
        # 需要查询的用户
        need_query_users = set()
        for s in need_check_subject:
            if s.type == SubjectType.DEPARTMENT.value:
                need_query_ancestor_departments.add(int(s.id))
            elif s.type == SubjectType.USER.value:
                need_query_users.add(s.id)

        # DB查询用户，需要知道用户的所有在的部门，不包含部门的祖先 username 对应的 set(DepartmentIDs)
        user_direct_department = defaultdict(set)
        if need_query_users:
            users = User.objects.filter(username__in=need_query_users)
            # 查询用户直接加入的部门
            department_members = DepartmentMember.objects.filter(user_id__in=[i.id for i in users])
            # 这里是记录user_id与其直接部门ID的集合, user_id 对应的 set(DepartmentIDs)
            user_id_direct_departments = defaultdict(set)
            for dm in department_members:
                user_id_direct_departments[dm.user_id].add(dm.department_id)
            # 遍历每个用户，获得其所有所在的部门
            for u in users:
                # 将user_id_direct_departments转换为user_direct_department
                user_direct_department[u.username] = user_id_direct_departments[u.id]
                # 每个部门也是需要查询其祖先部门的
                need_query_ancestor_departments.update(user_id_direct_departments[u.id])

        # DB查询所有部门的祖先部门，包括部门本身
        department_ancestors = defaultdict(set)
        if need_query_ancestor_departments:
            departments = Department.objects.filter(id__in=need_query_ancestor_departments)
            for d in departments:
                department_ancestors[d.id] = set(d.ancestor_ids)
                department_ancestors[d.id].add(d.id)

        need_delete_set = set()

        # 开始校验
        for s in need_check_subject:
            # 【对于部门】则需要查询其祖先是否在department_scopes里，
            if s.type == SubjectType.DEPARTMENT.value:
                if len(department_ancestors[int(s.id)] & department_scopes) == 0:
                    if raise_exception:
                        raise error_codes.FORBIDDEN.format(message=_("部门({})不满足角色的授权范围").format(s.id), replace=True)

                    need_delete_set.add((s.type, s.id))

            elif s.type == SubjectType.USER.value:
                # 校验用户，需要查询遍历用户的每个直接部门，然后再去每个直接部门的祖先，所有祖先和直接部门的集合即为用户所有所在的部门
                department_set = set()
                for d in user_direct_department[s.id]:
                    department_set.update(department_ancestors[d])
                if len(department_set & department_scopes) == 0:
                    if raise_exception:
                        raise error_codes.FORBIDDEN.format(message=_("用户({})不满足角色的授权范围").format(s.id), replace=True)

                    need_delete_set.add((s.type, s.id))

        return [one for one in subjects if (one.type, one.id) not in need_delete_set]


class ActionScopeDiffer:
    """
    分级管理员创建的模板策略与分级管理员的scope限制范围比较
    """

    def __init__(self, template_policy: PolicyBean, scope_policy: PolicyBean):
        self.template_policy = template_policy
        self.scope_policy = scope_policy

    def diff(self) -> bool:
        for rt in self.template_policy.related_resource_types:
            scope_rt = self.scope_policy.get_related_resource_type(rt.system_id, rt.type)
            if not scope_rt:
                return False
            if not self._diff_conditions(rt.condition, scope_rt.condition):
                return False

        return True

    def _diff_instances(self, template_instances: List[InstanceBean], scope_instances: List[InstanceBean]) -> bool:
        scope_paths = []
        for i in scope_instances:
            for p in i.path:
                sp = PathNodeBeanList(p).to_path_string()

                # 处理路径中存在*的情况
                if sp.endswith(",*/"):
                    sp = sp[:-2]

                scope_paths.append(sp)

        for i in template_instances:
            for p in i.path:
                path = PathNodeBeanList(p).to_path_string()
                for sp in scope_paths:
                    if path.startswith(sp):
                        break
                else:
                    return False  # 模板中的某个路径, 不能满足任意一个范围中的路径

        return True

    def _diff_attributes(self, template_attributes: List[Attribute], scope_attributes: List[Attribute]) -> bool:
        template_attrs = {a.id: {v.id for v in a.values} for a in template_attributes}
        scope_attrs = {a.id: {v.id for v in a.values} for a in scope_attributes}

        # 模板的属性key必须包含所有范围的key, 属性key之间的关系为AND
        if not set(scope_attrs.keys()).issubset(set(template_attrs.keys())):
            return False

        for key in scope_attrs.keys():
            # 模板的属性值, 必须为范围属性值的一部分, 属性值之间的关系为OR
            if not template_attrs[key].issubset(scope_attrs[key]):
                return False

        return True

    def _diff_condition(self, template_condition: ConditionBean, scope_condition: ConditionBean) -> bool:
        # 范围只有实例, 模板也有实例, 只要实例满足范围即可
        if scope_condition.instances and not scope_condition.attributes and template_condition.instances:
            return self._diff_instances(template_condition.instances, scope_condition.instances)

        # 范围只有属性, 模板也有属性, 只要属性满足范围即可
        if scope_condition.attributes and not scope_condition.instances and template_condition.attributes:
            return self._diff_attributes(template_condition.attributes, scope_condition.attributes)

        # 范围既有属性又有实例, 模板也是既有属性, 既有实例, 分别比较实例与属性
        if (
            scope_condition.instances
            and scope_condition.attributes
            and template_condition.instances
            and template_condition.attributes
        ):
            return self._diff_instances(
                template_condition.instances, scope_condition.instances
            ) and self._diff_attributes(template_condition.attributes, scope_condition.attributes)

        return False

    def _diff_conditions(
        self, template_conditions: List[ConditionBean], scope_conditions: List[ConditionBean]
    ) -> bool:
        # 范围为任意
        if not scope_conditions:
            return True

        # 模板为任意, 但是范围有限制
        if not template_conditions and scope_conditions:
            return False

        # 笛卡尔积遍历计算, 模板的条件只要满足范围中一条就算是满足, 同时模板的中的条件必须所有都要满足范围中的一条
        for tc in template_conditions:
            for sc in scope_conditions:
                if self._diff_condition(tc, sc):
                    break
            else:
                return False  # 循环正常结束, tc不满足sc中的任意一条

        return True
