<template>
    <smart-action class="iam-grading-admin-create-wrapper">
        <render-horizontal-block :label="$t(`m.common['基本信息']`)">
            <section ref="basicInfoContentRef">
                <basic-info :data="formData" @on-change="handleBasicInfoChange" ref="basicInfoRef" />
            </section>
        </render-horizontal-block>
        <render-action
            style="margin-bottom: 16px;"
            :title="$t(`m.grading['选择操作和资源实例范围']`)"
            :tips="addActionTips"
            v-if="!isSelectSystem"
            @on-click="handleAddAction" />
        <render-horizontal-block :label="$t(`m.grading['最大可授权资源范围']`)" v-if="isSelectSystem">
            <div class="grade-admin-select-wrapper">
                <div class="showTableClick" @click.stop="isShowTableClick">
                    <div class="action">
                        <section class="action-wrapper" @click.stop="handleAddAction">
                            <Icon bk type="plus-circle-shape" />
                            <span>{{ $t(`m.grading['选择操作和资源实例范围']`) }}</span>
                        </section>
                        <Icon
                            type="info-fill"
                            class="info-icon"
                            v-bk-tooltips.top="{ content: tips, width: 236, extCls: 'iam-tooltips-cls' }" />
                    </div>
                    <div class="sub-title" v-if="policyList.length > 0 && !isShowTable">
                        {{ $t(`m.common['共']`) }}
                        <span class="number">{{policyList.length}}</span>
                        {{ $t(`m.common['个']`) }}
                        {{ $t(`m.perm['操作权限']`) }}
                    </div>
                </div>
                <div v-show="isShowTable">
                    <div class="info-wrapper">
                        <p class="tips">{{ infoText }}</p>
                        <section style="min-width: 108px;">
                            <bk-switcher
                                v-model="isAllExpanded"
                                :disabled="isAggregateDisabled"
                                size="small"
                                theme="primary"
                                @change="handleAggregateAction" />
                            <span class="text">{{ expandedText }}</span>
                        </section>
                    </div>
                    <div class="resource-instance-wrapper"
                        ref="instanceTableContentRef"
                        v-bkloading="{ isLoading, opacity: 1, extCls: 'loading-resource-instance-cls' }">
                        <render-instance-table
                            ref="resourceInstanceRef"
                            :data="policyList"
                            :list="policyList"
                            :backup-list="aggregationsTableData"
                            @on-delete="handleDelete"
                            @on-aggregate-delete="handleAggregateDelete"
                            @on-select="handleResourceSelect" />
                    </div>
                </div>
            </div>
        </render-horizontal-block>
        <p class="action-empty-error" v-if="isShowActionEmptyError">{{ $t(`m.verify['操作和资源实例范围不可为空']`) }}</p>
        <section v-if="isShowMemberAdd" ref="memberRef">
            <render-action
                :title="$t(`m.grading['选择可授权人员范围']`)"
                :tips="addMemberTips"
                style="margin-bottom: 16px;"
                @on-click="handleAddMember" />
        </section>
        <render-member
            :users="users"
            :departments="departments"
            :is-all="isAll"
            v-else
            @on-add="handleAddMember"
            @on-delete="handleMemberDelete"
            @on-delete-all="handleDeleteAll" />
        <p class="action-empty-error" v-if="isShowMemberEmptyError">{{ $t(`m.verify['可授权人员范围不可为空']`) }}</p>
        <div slot="action">
            <bk-button theme="primary" type="button" @click="handleSubmit" :loading="submitLoading">
                {{ $t(`m.common['确定']`) }}
            </bk-button>
            <bk-button @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>

        <add-member-dialog
            :show.sync="isShowAddMemberDialog"
            :users="users"
            :departments="departments"
            :title="addMemberTitle"
            :all-checked="isAll"
            show-limit
            @on-cancel="handleCancelAdd"
            @on-sumbit="handleSumbitAdd" />

        <add-action-sideslider
            :is-show.sync="isShowAddActionSideslider"
            :default-value="curActionValue"
            :default-system="curSystem"
            :default-data="defaultValue"
            @on-submit="handleSelectSubmit"
            @on-cancel="handleSelectCancel"
            @animation-end="handleAnimationEnd" />

        <bk-dialog
            v-model="isShowReasonDialog"
            :loading="dialogLoading"
            header-position="left"
            :width="480"
            :mask-close="false"
            ext-cls="iam-edit-rate-manager-reason-dialog"
            @after-leave="reason = ''">
            <section class="content-wrapper">
                <label>
                    {{ $t(`m.common['理由']`) }}
                    <span>*</span>
                </label>
                <bk-input
                    type="textarea"
                    :rows="5"
                    v-model="reason"
                    style="margin-bottom: 15px;">
                </bk-input>
            </section>
            <section slot="footer">
                <bk-button theme="primary"
                    :disabled="reason === ''"
                    :loading="dialogLoading"
                    @click="handleSubmitWithReason">
                    {{ $t(`m.common['确定']`) }}
                </bk-button>
                <bk-button
                    style="margin-left: 6px;"
                    @click="handleDialogCancel">
                    {{ $t(`m.common['取消']`) }}
                </bk-button>
            </section>
        </bk-dialog>
    </smart-action>
</template>
<script>
    import _ from 'lodash'
    import { mapGetters } from 'vuex'
    import { leavePageConfirm } from '@/common/leave-page-confirm'
    import basicInfo from '../components/basic-info'
    import renderAction from '../common/render-action'
    import AddMemberDialog from '../../group/components/iam-add-member'
    import RenderMember from '../components/render-member'
    import AddActionSideslider from '../components/add-action-sideslider'
    import GradeAggregationPolicy from '@/model/grade-aggregation-policy'
    import GradePolicy from '@/model/grade-policy'
    import Condition from '@/model/condition'
    import RenderInstanceTable from '../components/render-instance-table'
    import { guid } from '@/common/util'
    export default {
        name: '',
        components: {
            basicInfo,
            renderAction,
            AddMemberDialog,
            RenderMember,
            AddActionSideslider,
            RenderInstanceTable
        },
        data () {
            return {
                formData: {
                    name: '',
                    description: '',
                    members: []
                },
                submitLoading: false,
                addActionTips: this.$t(`m.grading['添加操作提示']`),
                addMemberTips: this.$t(`m.grading['添加成员提示']`),
                isShowAddMemberDialog: false,
                users: [],
                departments: [],
                isShowMemberAdd: true,
                isShowAddActionSideslider: false,
                isShowActionEmptyError: false,
                isExpanded: false,
                curSystem: '',
                curActionValue: [],
                addMemberTitle: this.$t(`m.grading['选择可授权人员范围']`),
                originalList: [],
                isShowMemberEmptyError: false,

                infoText: this.$t(`m.grading['选择提示']`),
                tips: this.$t(`m.grading['添加操作提示']`),
                policyList: [],
                isLoading: false,
                isAllExpanded: false,
                aggregations: [],
                aggregationsBackup: [],
                aggregationsTableData: [],
                curSystemId: [],

                isShowReasonDialog: false,
                reason: '',
                dialogLoading: false,
                isAll: false,
                isShowTable: false
            }
        },
        computed: {
            ...mapGetters(['user']),
            isSelectSystem () {
                return this.originalList.length > 0
            },
            defaultValue () {
                if (this.originalList.length < 1) {
                    return []
                }
                const tempList = []
                this.originalList.forEach(item => {
                    if (!tempList.some(sys => sys.system_id === item.system_id)) {
                        tempList.push({
                            system_id: item.system_id,
                            system_name: item.system_name,
                            list: [item]
                        })
                    } else {
                        const curData = tempList.find(sys => sys.system_id === item.system_id)
                        curData.list.push(item)
                    }
                })

                return tempList
            },
            expandedText () {
                return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['批量编辑']`)
            },
            isAggregateDisabled () {
                return this.policyList.length < 1
                    || this.aggregations.length < 1
                    || (this.policyList.length === 1 && !this.policyList[0].isAggregate)
            },
            isStaff () {
                return this.user.role.type === 'staff'
            }
        },
        watch: {
            originalList: {
                handler (value) {
                    this.setPolicyList(value)
                    const params = [...new Set(this.policyList.map(item => item.system_id))]
                    // 无新增的的系统时无需请求聚合数据
                    const difference = params.filter(item => !this.curSystemId.includes(item))
                    if (difference.length > 0) {
                        this.curSystemId = [...this.curSystemId.concat(difference)]
                        this.resetData()
                        if (this.policyList.length > 1) {
                            this.fetchAggregationAction(this.curSystemId.join(','))
                        }
                    } else {
                        const data = this.getFilterAggregation(this.aggregationsBackup)
                        this.aggregations = _.cloneDeep(data)
                    }
                },
                deep: true
            }
        },
        methods: {
            isShowTableClick () {
                this.isShowTable = !this.isShowTable
            },
            async fetchPageData () {
                await this.fetchRatingManagerDetail()
            },

            setPolicyList (payload) {
                if (this.policyList.length < 1) {
                    this.policyList = payload.map(item => new GradePolicy(item))
                    return
                }
                const isAddIds = payload.map(item => `${item.system_id}&${item.id}`)
                const isExistIds = []
                this.policyList.forEach(item => {
                    if (item.isAggregate) {
                        item.actions.forEach(subItem => {
                            isExistIds.push(`${item.system_id}&${subItem.id}`)
                        })
                    } else {
                        isExistIds.push(`${item.system_id}&${item.id}`)
                    }
                })
                // 下一次选择的与现存的交集
                const intersectionIds = isExistIds.filter(item => isAddIds.includes(item))
                // 下一次选择所删除的操作
                const existRestIds = isExistIds.filter(item => !intersectionIds.includes(item))
                // 下一次选择所新增的操作
                const newRestIds = isAddIds.filter(item => !intersectionIds.includes(item))
                if (existRestIds.length > 0) {
                    const tempData = []
                    this.policyList.forEach(item => {
                        if (!item.isAggregate && !existRestIds.includes(`${item.system_id}&${item.id}`)) {
                            tempData.push(item)
                        }
                        if (item.isAggregate) {
                            const tempList = existRestIds.filter(act => item.actions.map(v => `${item.system_id}&${v.id}`).includes(act))
                            if (tempList.length > 0) {
                                item.actions = item.actions.filter(act => !tempList.includes(`${item.system_id}&${act.id}`))
                            }
                            tempData.push(item)
                        }
                    })
                    this.policyList = tempData.filter(
                        item => !item.isAggregate || (item.isAggregate && item.actions.length > 0)
                    )
                }

                if (newRestIds.length > 0) {
                    newRestIds.forEach(item => {
                        const curSys = payload.find(sys => `${sys.system_id}&${sys.id}` === item)
                        this.policyList.unshift(new GradePolicy(curSys))
                    })
                }
            },

            handleResourceSelect (payload) {
                window.changeDialog = true
                const instances = (function () {
                    const { id, name, system_id } = payload.aggregateResourceType
                    const arr = []
                    payload.instances.forEach(v => {
                        const curItem = arr.find(_ => _.type === id)
                        if (curItem) {
                            curItem.path.push([{
                                id: v.id,
                                name: v.name,
                                system_id,
                                type: id,
                                type_name: name
                            }])
                        } else {
                            arr.push({
                                name,
                                type: id,
                                path: [[{
                                    id: v.id,
                                    name: v.name,
                                    system_id,
                                    type: id,
                                    type_name: name
                                }]]
                            })
                        }
                    })
                    return arr
                })()
                const curAction = payload.actions.map(item => `${payload.system_id}&${item.id}`)
                if (instances.length > 0) {
                    this.aggregationsTableData.forEach(item => {
                        if (curAction.includes(`${item.system_id}&${item.id}`)) {
                            item.related_resource_types.forEach(subItem => {
                                subItem.condition = [new Condition({ instances }, '', 'add')]
                            })
                        }
                    })
                }
            },

            async fetchAggregationAction (payload) {
                this.isLoading = true
                try {
                    const res = await this.$store.dispatch('aggregate/getAggregateAction', { system_ids: payload })
                    ;(res.data.aggregations || []).forEach(item => {
                        item.$id = guid()
                    })
                    const data = this.getFilterAggregation(res.data.aggregations)
                    this.aggregationsBackup = _.cloneDeep(res.data.aggregations)
                    this.aggregations = _.cloneDeep(data)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.isLoading = false
                }
            },

            getFilterAggregation (payload) {
                const curSelectActions = []
                this.policyList.forEach(item => {
                    if (item.isAggregate) {
                        curSelectActions.push(...item.actions.map(v => `${item.system_id}&${v.id}`))
                    } else {
                        curSelectActions.push(`${item.system_id}&${item.id}`)
                    }
                })
                let aggregations = []
                ;(payload || []).forEach(item => {
                    const { actions, aggregate_resource_type, $id } = item
                    const curActions = actions.filter(_ => curSelectActions.includes(`${_.system_id}&${_.id}`))
                    if (curActions.length > 0) {
                        aggregations.push({
                            actions: curActions,
                            aggregate_resource_type: Object.assign(aggregate_resource_type, {
                                system_name: this.policyList.find(
                                    _ => _.system_id === curActions[0].system_id
                                ).system_name
                            }),
                            $id
                        })
                    }
                })
                aggregations = aggregations.filter(item => item.actions.length > 1)
                return aggregations
            },

            resetData () {
                this.aggregations = []
                this.aggregationsBackup = []
            },

            handleAggregateAction (payload) {
                window.changeDialog = true
                const aggregationAction = this.aggregations
                const actionIds = []
                aggregationAction.forEach(item => {
                    actionIds.push(...item.actions.map(_ => `${_.system_id}&${_.id}`))
                })
                if (payload) {
                    // 缓存新增加的操作权限数据
                    aggregationAction.forEach(item => {
                        const filterArray = this.policyList.filter(subItem => item.actions.map(_ => `${_.system_id}&${_.id}`).includes(`${subItem.system_id}&${subItem.id}`))
                        const addArray = filterArray.filter(subItem => !this.aggregationsTableData.map(_ => `${_.system_id}&${_.id}`).includes(`${subItem.system_id}&${subItem.id}`))
                        if (addArray.length > 0) {
                            this.aggregationsTableData.push(...addArray)
                        }
                    })
                    const aggregations = aggregationAction.filter(item => {
                        const target = item.actions.map(v => v.id).sort()
                        const existData = this.policyList.find(subItem => {
                            return subItem.isAggregate && _.isEqual(target, subItem.actions.map(v => v.id).sort())
                        })
                        return !existData
                    }).map((item, index) => {
                        // 从缓存值中取值
                        const isExistActions = this.aggregationsTableData.filter(subItem =>
                            item.actions.map(v => `${v.system_id}&${v.id}`).includes(`${subItem.system_id}&${subItem.id}`)
                        )
                        const conditions = isExistActions.map(subItem => subItem.related_resource_types[0].condition)
                        // 是否都选择了实例
                        const isAllHasInstance = conditions.every(subItem => subItem[0] !== 'none' && subItem.length > 0)
                        if (isAllHasInstance) {
                            const instances = conditions.map(subItem => subItem.map(v => v.instance))
                            let isAllEqual = true
                            for (let i = 0; i < instances.length - 1; i++) {
                                if (!_.isEqual(instances[i], instances[i + 1])) {
                                    isAllEqual = false
                                    break
                                }
                            }
                            console.log('instances: ')
                            console.log(instances)
                            console.log('isAllEqual: ' + isAllEqual)
                            if (isAllEqual) {
                                const instanceData = instances[0][0][0]
                                item.instances = instanceData.path.map(pathItem => {
                                    return {
                                        id: pathItem[0].id,
                                        name: pathItem[0].name
                                    }
                                })
                            } else {
                                item.instances = []
                            }
                        } else {
                            item.instances = []
                        }
                        return new GradeAggregationPolicy(item)
                    })
                    this.policyList = this.policyList.filter(item => !actionIds.includes(`${item.system_id}&${item.id}`))
                    this.policyList.unshift(...aggregations)
                    return
                }
                const aggregationData = []
                const newPolicyList = []
                this.policyList.forEach(item => {
                    if (!item.isAggregate) {
                        newPolicyList.push(item)
                    } else {
                        aggregationData.push(_.cloneDeep(item))
                    }
                })
                this.policyList = _.cloneDeep(newPolicyList)
                const reallyActionIds = actionIds.filter(item => !this.policyList.map(v => `${v.system_id}&${v.id}`).includes(item))
                reallyActionIds.forEach(item => {
                    // 优先从缓存值中取值
                    const curObj = this.aggregationsTableData.find(_ => `${_.system_id}&${_.id}` === item)
                    if (curObj) {
                        this.policyList.unshift(curObj)
                    } else {
                        const curAction = this.originalList.find(_ => `${_.system_id}&${_.id}` === item)
                        const curAggregation = aggregationData.find(_ => _.actions.map(v => `${_.system_id}&${v.id}`).includes(item))
                        this.policyList.unshift(new GradePolicy({ ...curAction, tag: 'add' }, 'add'))
                        if (curAggregation && curAggregation.instances.length > 0) {
                            const curData = this.policyList[0]
                            const instances = (function () {
                                const arr = []
                                const aggregateResourceType = curAggregation.aggregateResourceType
                                const { id, name, system_id } = aggregateResourceType
                                curAggregation.instances.forEach(v => {
                                    const curItem = arr.find(_ => _.type === id)
                                    if (curItem) {
                                        curItem.path.push([{
                                            id: v.id,
                                            name: v.name,
                                            system_id,
                                            type: id,
                                            type_name: name
                                        }])
                                    } else {
                                        arr.push({
                                            name,
                                            type: id,
                                            path: [[{
                                                id: v.id,
                                                name: v.name,
                                                system_id,
                                                type: id,
                                                type_name: name
                                            }]]
                                        })
                                    }
                                })
                                return arr
                            })()
                            if (instances.length > 0) {
                                curData.related_resource_types.forEach(subItem => {
                                    subItem.condition = [new Condition({ instances }, '', 'add')]
                                })
                            }
                        }
                    }
                })
            },

            handleGetValue () {
                return this.$refs.resourceInstanceRef && this.$refs.resourceInstanceRef.handleGetValue()
            },

            async fetchRatingManagerDetail () {
                try {
                    const res = await this.$store.dispatch('role/getRatingManagerDetail', { id: this.$route.params.id })
                    this.handleDetailData(res.data)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            handleDetailData (payload) {
                const { name, description, members } = payload
                this.formData = Object.assign({}, {
                    name,
                    description,
                    members
                })
                const departments = []
                const users = []
                payload.subject_scopes.forEach(item => {
                    if (item.type === 'department') {
                        departments.push({
                            id: Number(item.id),
                            type: 'depart',
                            name: item.name,
                            count: item.member_count
                        })
                    }
                    if (item.type === 'user') {
                        users.push({
                            type: 'user',
                            name: item.name,
                            username: item.id
                        })
                    }
                })

                this.isAll = payload.subject_scopes.some(item => item.type === '*' && item.id === '*')

                this.users.splice(0, this.users.length, ...users)
                this.departments.splice(0, this.departments.length, ...departments)
                this.isShowMemberAdd = false

                const tempActions = []
                payload.authorization_scopes.forEach(item => {
                    item.actions.forEach(act => {
                        tempActions.push({
                            ...act,
                            system_id: item.system.id,
                            system_name: item.system.name,
                            $id: `${item.system.id}&${act.id}`
                        })
                    })
                })

                this.originalList = _.cloneDeep(tempActions)
            },

            handleBasicInfoChange (field, data) {
                window.changeDialog = true
                this.formData[field] = data
            },

            handleAddAction () {
                this.isShowTable = true
                this.curActionValue = this.originalList.map(item => item.$id)
                this.isShowAddActionSideslider = true
            },

            setAggregateExpanded () {
                const flag = this.policyList.every(item => !item.isAggregate)
                if (flag) {
                    this.isAllExpanded = false
                }
            },

            handleDelete (systemId, actionId, payload, index) {
                window.changeDialog = true
                this.originalList = this.originalList.filter(item => payload !== item.$id)
                this.policyList.splice(index, 1)
                for (let i = 0; i < this.aggregations.length; i++) {
                    const item = this.aggregations[i]
                    if (item.actions[0].system_id === systemId) {
                        item.actions = item.actions.filter(subItem => subItem.id !== actionId)
                        break
                    }
                }
                this.aggregations = this.aggregations.filter(item => item.actions.length > 1)
                this.setAggregateExpanded()
            },

            handleAggregateDelete (systemId, actions, index) {
                window.changeDialog = true
                this.policyList.splice(index, 1)
                const deleteAction = actions.map(item => `${systemId}&${item.id}`)
                this.originalList = this.originalList.filter(item => !deleteAction.includes(item.$id))
                this.aggregations = this.aggregations.filter(item =>
                    !(item.actions[0].system_id === systemId
                        && _.isEqual(item.actions.map(_ => _.id).sort(), actions.map(_ => _.id).sort()))
                )
                this.setAggregateExpanded()
            },

            handleSelectSubmit (payload) {
                window.changeDialog = true

                this.originalList = _.cloneDeep(payload)
                this.isShowActionEmptyError = false
                this.isShowAddActionSideslider = false
            },

            handleSelectCancel () {
                this.isShowAddActionSideslider = false
            },

            handleAnimationEnd () {
                this.curSystem = ''
                this.curActionValue = []
                this.isShowAddActionSideslider = false
            },

            handleAddMember () {
                this.isShowAddMemberDialog = true
            },

            handleCancelAdd () {
                this.isShowAddMemberDialog = false
            },

            handleMemberDelete (type, payload) {
                window.changeDialog = true
                if (type === 'user') {
                    this.users.splice(payload, 1)
                } else {
                    this.departments.splice(payload, 1)
                }
                this.isShowMemberAdd = this.users.length < 1 && this.departments.length < 1
            },

            handleDeleteAll () {
                this.isAll = false
                this.isShowMemberAdd = true
            },

            handleSumbitAdd (payload) {
                window.changeDialog = true
                const { users, departments } = payload
                this.isAll = payload.isAll
                this.users = _.cloneDeep(users)
                this.departments = _.cloneDeep(departments)
                this.isShowMemberAdd = false
                this.isShowAddMemberDialog = false
                this.isShowMemberEmptyError = false
            },

            handleDialogCancel () {
                this.isShowReasonDialog = false
                this.dialogLoading = false
            },

            async handleSubmitWithReason () {
                this.dialogLoading = true
                const data = this.$refs.resourceInstanceRef.handleGetValue().actions
                const subjects = []
                if (this.isAll) {
                    subjects.push({
                        id: '*',
                        type: '*'
                    })
                } else {
                    this.users.forEach(item => {
                        subjects.push({
                            type: 'user',
                            id: item.username
                        })
                    })
                    this.departments.forEach(item => {
                        subjects.push({
                            type: 'department',
                            id: item.id
                        })
                    })
                }
                const { name, description, members } = this.formData
                const params = {
                    name,
                    description,
                    members,
                    subject_scopes: subjects,
                    authorization_scopes: data,
                    reason: this.reason,
                    id: this.$route.params.id
                }
                try {
                    await this.$store.dispatch('role/editRatingManagerWithGeneral', params)
                    await this.$store.dispatch('roleList')
                    this.isShowReasonDialog = false
                    this.messageSuccess(this.$t(`m.info['申请已提交']`), 1000)
                    this.$router.push({
                        name: 'apply'
                    })
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.dialogLoading = false
                }
            },

            async handleSubmit () {
                const validatorFlag = this.$refs.basicInfoRef.handleValidator()
                let data = []
                let flag = false
                this.isShowActionEmptyError = this.originalList.length < 1
                this.isShowMemberEmptyError = (this.users.length < 1 && this.departments.length < 1) && !this.isAll
                if (!this.isShowActionEmptyError) {
                    data = this.$refs.resourceInstanceRef.handleGetValue().actions
                    flag = this.$refs.resourceInstanceRef.handleGetValue().flag
                }

                if (validatorFlag || flag || this.isShowActionEmptyError || this.isShowMemberEmptyError) {
                    if (validatorFlag) {
                        this.scrollToLocation(this.$refs.basicInfoContentRef)
                    } else if (flag) {
                        this.scrollToLocation(this.$refs.instanceTableContentRef)
                    } else if (this.isShowMemberEmptyError) {
                        this.scrollToLocation(this.$refs.memberRef)
                    }
                    return
                }
                if (this.isStaff) {
                    this.isShowReasonDialog = true
                    return
                }
                const subjects = []
                if (this.isAll) {
                    subjects.push({
                        id: '*',
                        type: '*'
                    })
                } else {
                    this.users.forEach(item => {
                        subjects.push({
                            type: 'user',
                            id: item.username
                        })
                    })
                    this.departments.forEach(item => {
                        subjects.push({
                            type: 'department',
                            id: item.id
                        })
                    })
                }
                const { name, description, members } = this.formData
                const params = {
                    name,
                    description,
                    members,
                    subject_scopes: subjects,
                    authorization_scopes: data,
                    id: this.$route.params.id
                }
                this.submitLoading = true
                window.changeDialog = false
                const dispatchMethod = this.isStaff ? 'editRatingManagerWithGeneral' : 'editRatingManager'
                try {
                    await this.$store.dispatch(`role/${dispatchMethod}`, params)
                    await this.$store.dispatch('roleList')
                    this.messageSuccess(this.$t(`m.info['编辑分级管理员成功']`), 1000)
                    this.$router.push({
                        name: 'gradingAdminDetail',
                        params: {
                            id: this.$route.params.id
                        }
                    })
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.submitLoading = false
                }
            },

            handleCancel () {
                let cancelHandler = Promise.resolve()
                if (window.changeDialog) {
                    cancelHandler = leavePageConfirm()
                }
                cancelHandler.then(() => {
                    this.$router.push({
                        name: 'gradingAdminDetail',
                        params: {
                            id: this.$route.params.id
                        }
                    })
                }, _ => _)
            }
        }
    }
</script>
<style lang="postcss">
    .iam-grading-admin-create-wrapper {
        .grading-admin-render-perm-cls {
            margin-bottom: 16px;
        }
        .action-empty-error {
            position: relative;
            top: -8px;
            font-size: 12px;
            color: #ff4d4d;
        }
        .grade-admin-select-wrapper {
            .showTableClick {
                cursor: pointer;
            .action {
                display: flex;
                justify-content: flex-start;
                .action-wrapper {
                    margin-left: 8px;
                    font-size: 14px;
                    color: #3a84ff;
                    cursor: pointer;
                    &:hover {
                        color: #699df4;
                    }
                    i {
                        position: relative;
                        top: -1px;
                        left: 2px;
                    }
                }
                .info-icon {
                    margin: 2px 0 0 2px;
                    color: #c4c6cc;
                    &:hover {
                        color: #3a84ff;
                    }
                }
            }
            .sub-title {
                margin-top:10px;
                margin-left:10px;
                font-size:14px;
                color: #979ba5;
            .number {
                font-weight: 600;
        }
    }
        }
            .info-wrapper {
                display: flex;
                justify-content: space-between;
                margin-top: 16px;
                line-height: 24px;
                .tips,
                .text {
                    line-height: 20px;
                    font-size: 12px;
                }
            }
            .resource-instance-wrapper {
                min-height: 200px;
            }
            .loading-resource-instance-cls {
                border: 1px solid #c4c6cc;
            }
        }
    .horizontal-item .label {
        width: 130px;
    }
    }
    .iam-edit-rate-manager-reason-dialog {
        .content-wrapper {
            display: flex;
            justify-content: flex-start;
            label {
                display: block;
                width: 70px;
                span {
                    color: #ea3636;
                }
            }
        }
    }
</style>
