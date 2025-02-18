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

/**
 * 获取不同身份的router差异
 *
 * @param {String} payload 身份类型(staff: 普通用户，super_manager: 超级用户，system_manager: 系统管理员，rating_manager: 分级管理员)
 *
 * @return {Array}
 */
export const getRouterDiff = (payload) => {
    if (payload === 'staff' || payload === '') {
        return [
            'userGroup',
            'createUserGroup',
            'userGroupDetail',
            'permTemplate',
            'permTemplateCreate',
            'user',
            'permTemplateDetail',
            'administrator',
            'approvalProcess',
            'groupPermRenewal',
            'audit',
            'permTemplateEdit',
            'permTemplateDiff',
            'addGroupPerm'
        ]
    }
    if (payload === 'super_manager') {
        return [
            'applyCustomPerm',
            'applyJoinUserGroup',
            'apply',
            'myPerm',
            'templatePermDetail',
            'groupPermDetail',
            'orgPermDetail',
            'approval',
            'permRenewal',
            'systemAccess',
            'systemAccessCreate',
            'systemAccessAccess',
            'systemAccessRegistry',
            'systemAccessOptimize',
            'systemAccessComplete'
        ]
    }
    if (payload === 'system_manager') {
        return [
            'applyCustomPerm',
            'applyJoinUserGroup',
            'apply',
            'myPerm',
            'templatePermDetail',
            'groupPermDetail',
            'orgPermDetail',
            'ratingManager',
            'gradingAdminCreate',
            'gradingAdminDetail',
            'user',
            'gradingAdminUpdateTemplate',
            'approval',
            'permRenewal',
            'systemAccess',
            'systemAccessCreate',
            'systemAccessAccess',
            'systemAccessRegistry',
            'systemAccessOptimize',
            'systemAccessComplete'
        ]
    }
    if (payload === 'rating_manager') {
        return [
            'applyCustomPerm',
            'applyJoinUserGroup',
            'apply',
            'myPerm',
            'templatePermDetail',
            'groupPermDetail',
            'orgPermDetail',
            'ratingManager',
            'gradingAdminCreate',
            'gradingAdminDetail',
            'user',
            'gradingAdminUpdateTemplate',
            'administrator',
            'approval',
            'permRenewal',
            'audit',
            'systemAccess',
            'systemAccessCreate',
            'systemAccessAccess',
            'systemAccessRegistry',
            'systemAccessOptimize',
            'systemAccessComplete'
        ]
    }
    // payload其它取值默认返回全部菜单
    return [
        'systemAccess',
        'systemAccessCreate',
        'systemAccessAccess',
        'systemAccessRegistry',
        'systemAccessOptimize',
        'systemAccessComplete',
        'myPerm',
        'templatePermDetail',
        'groupPermDetail',
        'orgPermDetail',
        'userGroup',
        'createUserGroup',
        'userGroupDetail',
        'userGroupPermDetail',
        'permTemplate',
        'permTemplateDetail',
        'permTemplateCreate',
        'applyCustomPerm',
        'applyJoinUserGroup',
        'apply',
        'user',
        'ratingManager',
        'gradingAdminCreate',
        'gradingAdminDetail',
        'gradingAdminEdit',
        'gradingAdminUpdateTemplate',
        'administrator',
        'approvalProcess',
        'approval',
        'permRenewal',
        'groupPermRenewal',
        'audit',
        'permTemplateEdit',
        'permTemplateDiff',
        'addGroupPerm'
    ]
}
