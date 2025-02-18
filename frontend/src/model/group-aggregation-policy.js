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

import _ from 'lodash'
import il8n from '@/language'
import { CUSTOM_PERM_TEMPLATE_ID } from '@/common/constants'
export default class GroupAggregationPolicy {
    constructor (payload) {
        this.isError = false
        this.actions = payload.actions || []
        this.aggregateResourceType = payload.aggregate_resource_type || {}
        this.instances = payload.instances || []
        this.instancesBackup = _.cloneDeep(this.instances)
        this.isAggregate = true
        this.system_id = payload.actions[0].detail.system.id
        this.system_name = payload.actions[0].detail.system.name
        this.canPaste = false
        this.aggregationId = payload.aggregationId || ''
        this.initDetailData(this.actions)
    }

    initDetailData (payload) {
        if (payload.length < 1) {
            this.detail = {}
            return
        }
        this.detail = payload[0].detail
    }

    get isTemplate () {
        if (this.actions.length > 0) {
            return this.actions[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID
        }
        return false
    }

    get empty () {
        return this.instances.length < 1
    }

    get value () {
        if (this.empty) {
            return il8n('verify', '请选择')
        }
        return this.instances.map(item => item.name).join('；')
    }

    get name () {
        if (this.actions.length < 1) {
            return ''
        }
        return this.actions.map(item => item.name).join('，')
    }

    get key () {
        if (this.actions.length < 1) {
            return ''
        }
        return this.actions.map(item => item.id).join('')
    }
}
