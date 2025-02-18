/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云-权限中心(BlueKing-IAM) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云-权限中心(BlueKing-IAM) is licensed under the MIT License.
 *
 * License for 蓝鲸智云-权限中心(BlueKing-IAM):
 *
 * ---------------------------------------------------
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
 * the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
*/

import il8n from '@/language'

const SITE_URL = window.SITE_URL

// 系统接入
const SystemAccess = () => import(/* webpackChunkName: 'system-access' */'../views/system-access')
const SystemAccessAccess = () => import(/* webpackChunkName: 'system' */'../views/system-access/access')
const SystemAccessRegistry = () => import(/* webpackChunkName: 'system-access' */'../views/system-access/registry')
const SystemAccessOptimize = () => import(/* webpackChunkName: 'system-access' */'../views/system-access/optimize')
const SystemAccessComplete = () => import(/* webpackChunkName: 'system-access' */'../views/system-access/complete')

// 申请自定义权限
const ApplyCustomPerm = () => import(
    /* webpackChunkName: 'perm-apply' */'../views/perm-apply/apply-custom-perm')

// 申请加入用户组
const ApplyJoinUserGroup = () => import(
    /* webpackChunkName: 'perm-apply' */'../views/perm-apply/apply-join-user-group')

// 我的申请
const Apply = () => import(
    /* webpackChunkName: 'my-apply' */'../views/apply')

// 我的权限
const MyPerm = () => import(
    /* webpackChunkName: 'my-perm' */'../views/perm')

// 用户组
const UserGroup = () => import(
    /* webpackChunkName: 'user-group' */'../views/group')

// 用户组新建
const CreateUserGroup = () => import(
    /* webpackChunkName: 'user-group' */'../views/group/create')

// 用户组详情
const UserGroupDetail = () => import(
    /* webpackChunkName: 'user-group' */'../views/group/detail')

// 用户组组权限详情
const UserGroupPermDetail = () => import(
    /* webpackChunkName: 'user-group' */'../views/group/detail/group-perm-detail')

// 用户组添加权限
const AddGroupPerm = () => import(
    /* webpackChunkName: 'user-group' */'../views/group/add-perm')

// 权限模板
const PermTemplate = () => import(
    /* webpackChunkName: 'perm-template' */'../views/perm-template/index')

// 权限模板详情
const PermTemplateDetail = () => import(
    /* webpackChunkName: 'perm-template' */'../views/perm-template/detail')

// 权限模板新建
const PermTemplateCreate = () => import(
    /* webpackChunkName: 'perm-template' */'../views/perm-template/create/index')

// 权限模板编辑
const PermTemplateEdit = () => import(
    /* webpackChunkName: 'perm-template' */'../views/perm-template/edit')

// 权限模板编辑差异
const PermTemplateDifference = () => import(
    /* webpackChunkName: 'perm-template' */'../views/perm-template/edit/difference')

// 用户
const User = () => import(
    /* webpackChunkName: 'user' */'../views/user')

// 分级管理员
const GradingAdmin = () => import(
    /* webpackChunkName: 'grading-admin' */'../views/grading-admin')

// 分级管理员新建
const GradingAdminCreate = () => import(
    /* webpackChunkName: 'grading-admin' */'../views/grading-admin/create')

// 分级管理员详情
const GradingAdminDetail = () => import(
    /* webpackChunkName: 'grading-admin' */'../views/grading-admin/detail')

// 分级管理员编辑
const GradingAdminEdit = () => import(
    /* webpackChunkName: 'grading-admin' */'../views/grading-admin/edit')

// 分级管理员更新权限模板
const GradingAdminUpdateTemplate = () => import(
    /* webpackChunkName: 'grading-admin' */'../views/grading-admin/update-template')

// 设置
const Setting = () => import(
    /* webpackChunkName: 'set' */'../views/set')

// 审批流程设置
const ApprovalProcess = () => import(
    /* webpackChunkName: 'approvalProcess' */'../views/approval-process')

// 权限续期
const PermRenewal = () => import(
    /* webpackChunkName: 'PermRenewal' */'../views/perm/perm-renewal')

// 组织权限续期
const GroupPermRenewal = () => import(
    /* webpackChunkName: 'PermRenewal' */'../views/perm/group-perm-renewal')

// 审计
const Audit = () => import(
    /* webpackChunkName: 'audit' */'../views/audit')

const TemplatePermDetail = () => import(
    /* webpackChunkName: 'my-perm-template-perm' */'../views/perm/template-perm/detail'
)
const GroupPermDetail = () => import(
    /* webpackChunkName: 'my-perm-group-perm' */'../views/perm/group-perm/detail'
)
const OrgPermDetail = () => import(
    /* webpackChunkName: 'my-perm-org-perm' */'../views/perm/organization-perm/detail'
)

// no-perm
const NoPerm = () => import(
    /* webpackChunkName: 'no-perm' */'../views/no-perm')

// 404
const NotFound = () => import(
    /* webpackChunkName: 'none' */'../views/404')

// Main
const MainEntry = () => import(
    /* webpackChunkName: 'index' */'../views')

export const routes = [
    {
        path: SITE_URL,
        name: 'iamMain',
        component: MainEntry,
        children: [
            {
                path: 'system-access',
                name: 'systemAccess',
                meta: {
                    headerTitle: il8n('nav', '系统接入')
                },
                component: SystemAccess
            },
            {
                path: 'system-access/access',
                name: 'systemAccessCreate',
                meta: {
                    headerTitle: il8n('nav', '系统接入'),
                    backRouter: 'systemAccess'
                },
                component: SystemAccessAccess
            },
            {
                path: 'system-access/access/:id',
                name: 'systemAccessAccess',
                meta: {
                    headerTitle: il8n('nav', '系统接入'),
                    backRouter: 'systemAccess'
                },
                component: SystemAccessAccess
            },
            {
                path: 'system-access/registry/:id',
                name: 'systemAccessRegistry',
                meta: {
                    headerTitle: il8n('nav', '系统接入'),
                    backRouter: 'systemAccessAccess'
                },
                component: SystemAccessRegistry
            },
            {
                path: 'system-access/optimize/:id',
                name: 'systemAccessOptimize',
                meta: {
                    headerTitle: il8n('nav', '系统接入'),
                    backRouter: 'systemAccessRegistry'
                },
                component: SystemAccessOptimize
            },
            {
                path: 'system-access/complete/:id',
                name: 'systemAccessComplete',
                meta: {
                    headerTitle: il8n('nav', '系统接入'),
                    backRouter: 'systemAccessRegistry'
                },
                component: SystemAccessComplete
            },
            {
                path: 'my-perm',
                name: 'myPerm',
                alias: '',
                meta: {
                    headerTitle: il8n('nav', '我的权限')
                    // hasPageTab: true
                },
                component: MyPerm
            },
            {
                path: 'perm-renewal',
                name: 'permRenewal',
                meta: {
                    headerTitle: il8n('renewal', '批量续期'),
                    backRouter: 'myPerm'
                },
                component: PermRenewal
            },
            {
                path: 'group-perm-renewal',
                name: 'groupPermRenewal',
                meta: {
                    headerTitle: il8n('renewal', '用户组成员续期'),
                    backRouter: 'myPerm'
                },
                component: GroupPermRenewal
            },
            {
                path: 'audit',
                name: 'audit',
                meta: {
                    headerTitle: il8n('nav', '审计')
                },
                component: Audit
            },
            {
                path: 'my-perm/template-perm/:id',
                name: 'templatePermDetail',
                meta: {
                    headerTitle: ''
                },
                component: TemplatePermDetail
            },
            {
                path: 'my-perm/group-perm/:id',
                name: 'groupPermDetail',
                meta: {
                    headerTitle: ''
                },
                component: GroupPermDetail
            },
            {
                path: 'my-perm/organization-perm/:id',
                name: 'orgPermDetail',
                meta: {
                    headerTitle: ''
                },
                component: OrgPermDetail
            },
            {
                path: 'user-group',
                name: 'userGroup',
                meta: {
                    headerTitle: il8n('nav', '用户组')
                },
                component: UserGroup
            },
            {
                path: 'create-user-group',
                name: 'createUserGroup',
                meta: {
                    headerTitle: il8n('userGroup', '新建用户组'),
                    backRouter: 'userGroup'
                },
                component: CreateUserGroup
            },
            {
                path: 'user-group-detail/:id',
                name: 'userGroupDetail',
                meta: {
                    headerTitle: '',
                    backRouter: 'userGroup',
                    hasPageTab: true
                },
                component: UserGroupDetail
            },
            {
                path: 'user-group-perm-detail/:id/:templateId',
                name: 'userGroupPermDetail',
                meta: {
                    headerTitle: '',
                    backRouter: -1
                },
                component: UserGroupPermDetail
            },
            {
                path: 'add-group-perm/:id',
                name: 'addGroupPerm',
                meta: {
                    headerTitle: il8n('userGroup', '添加组权限'),
                    backRouter: -1
                },
                component: AddGroupPerm
            },
            {
                path: 'perm-template',
                name: 'permTemplate',
                meta: {
                    headerTitle: il8n('nav', '权限模板')
                },
                component: PermTemplate
            },
            {
                path: 'perm-template-detail/:id/:systemId',
                name: 'permTemplateDetail',
                meta: {
                    headerTitle: '',
                    backRouter: 'permTemplate',
                    hasPageTab: true
                },
                component: PermTemplateDetail
            },
            {
                path: 'perm-template-create',
                name: 'permTemplateCreate',
                meta: {
                    headerTitle: il8n('nav', '新建权限模板'),
                    backRouter: 'permTemplate'
                },
                component: PermTemplateCreate
            },
            {
                path: 'perm-template-edit/:id/:systemId',
                name: 'permTemplateEdit',
                meta: {
                    headerTitle: '',
                    backRouter: 'permTemplateDetail'
                },
                component: PermTemplateEdit
            },
            {
                path: 'perm-template-diff/:id/:systemId',
                name: 'permTemplateDiff',
                meta: {
                    headerTitle: '',
                    backRouter: -1
                },
                component: PermTemplateDifference
            },
            {
                path: 'apply-custom-perm',
                name: 'applyCustomPerm',
                meta: {
                    headerTitle: il8n('applyEntrance', '申请自定义权限'),
                    backRouter: -1
                },
                component: ApplyCustomPerm
            },
            {
                path: 'apply-join-user-group',
                name: 'applyJoinUserGroup',
                meta: {
                    headerTitle: il8n('applyEntrance', '申请加入用户组')
                },
                component: ApplyJoinUserGroup
            },
            {
                path: 'apply',
                name: 'apply',
                meta: {
                    headerTitle: il8n('nav', '我的申请')
                },
                component: Apply
            },
            {
                path: 'user',
                name: 'user',
                meta: {
                    headerTitle: il8n('nav', '用户')
                },
                component: User
            },
            {
                path: 'rating-manager',
                name: 'ratingManager',
                meta: {
                    headerTitle: il8n('grading', '分级管理员')
                },
                component: GradingAdmin
            },
            {
                path: ':id/rating-manager-create',
                name: 'gradingAdminCreate',
                meta: {
                    headerTitle: il8n('nav', '新建分级管理员'),
                    backRouter: 'ratingManager'
                },
                props: true,
                component: GradingAdminCreate
            },
            {
                path: ':id/rating-manager-detail',
                name: 'gradingAdminDetail',
                meta: {
                    backRouter: 'ratingManager'
                },
                component: GradingAdminDetail
            },
            {
                path: ':id/rating-manager-edit',
                name: 'gradingAdminEdit',
                meta: {
                    backRouter: 'gradingAdminDetail'
                },
                component: GradingAdminEdit
            },
            {
                path: ':id/rating-manager-update-template',
                name: 'gradingAdminUpdateTemplate',
                meta: {
                    headerTitle: il8n('nav', '编辑分级管理员'),
                    backRouter: 'gradingAdminEdit'
                },
                component: GradingAdminUpdateTemplate
            },
            {
                path: 'administrator',
                name: 'administrator',
                meta: {
                    headerTitle: il8n('common', '管理员')
                },
                component: Setting
            },
            {
                path: 'approval-process',
                name: 'approvalProcess',
                meta: {
                    headerTitle: il8n('myApply', '审批流程')
                },
                component: ApprovalProcess
            },
            {
                path: 'no-perm',
                name: 'noPerm',
                meta: {
                    headerTitle: ''
                },
                component: NoPerm
            }
        ]
    },
    {
        path: '*',
        name: '404',
        component: NotFound
    }
]
