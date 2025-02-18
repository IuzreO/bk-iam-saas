<template>
    <smart-action class="iam-add-group-perm-wrapper">
        <render-horizontal-block
            :label="$t(`m.userGroup['组权限']`)">
            <div class="grade-admin-select-wrapper">
                <div class="action">
                    <section class="action-wrapper" @click.stop="handleAddPerm">
                        <Icon bk type="plus-circle-shape" />
                        <span>{{ $t(`m.userGroup['添加组权限']`) }}</span>
                    </section>
                </div>
                <div class="info-wrapper">
                    <section style="min-width: 108px; position: relative;">
                        <bk-switcher
                            v-model="isAllExpanded"
                            :disabled="isAggregateDisabled"
                            size="small"
                            theme="primary"
                            @change="handleAggregateAction" />
                        <span class="text">{{ expandedText }}</span>
                    </section>
                </div>
                <resource-instance-table
                    is-edit
                    mode="create"
                    ref="resInstanceTableRef"
                    :list="tableList"
                    :authorization="curAuthorizationData"
                    :original-list="tableListBackup"
                    :is-show-error-tips="isShowErrorTips"
                    @on-select="handleAttrValueSelected"
                    @on-resource-select="handleResSelect" />
            </div>
        </render-horizontal-block>
        <div slot="action">
            <bk-button theme="primary" type="button" :loading="submitLoading" @click="handleSubmit">
                {{ $t(`m.common['提交']`) }}
            </bk-button>
            <bk-button style="margin-left: 10px;" @click="handleCancel">{{ $t(`m.common['取消']`) }}</bk-button>
        </div>

        <add-perm-sideslider
            :is-show.sync="isShowAddSideslider"
            :custom-perm="originalList"
            :template="tempalteDetailList"
            :aggregation="aggregationData"
            :authorization="authorizationData"
            :group-id="$route.params.id"
            @on-view="handleViewDetail"
            @on-add-custom="handleAddCustom"
            @on-edit-custom="handleEditCustom"
            @on-cancel="handleAddCancel"
            @on-submit="handleSubmitPerm" />

        <add-action-sideslider
            :is-show.sync="isShowAddActionSideslider"
            :default-value="curActionValue"
            :default-data="defaultValue"
            :group-id="$route.params.id"
            :aggregation="aggregationDataByCustom"
            :authorization="authorizationDataByCustom"
            @on-submit="handleSelectSubmit" />

        <render-template-sideslider
            :is-show.sync="templateDetailSideslider.isShow"
            :id="templateDetailSideslider.id" />
    </smart-action>
</template>
<script>
    import _ from 'lodash'
    import { guid } from '@/common/util'
    import { CUSTOM_PERM_TEMPLATE_ID } from '@/common/constants'
    import { leavePageConfirm } from '@/common/leave-page-confirm'
    import AddPermSideslider from '../components/add-group-perm-sideslider'
    import AddActionSideslider from '../components/add-action-sideslider'
    import ResourceInstanceTable from '../components/render-instance-table'
    import RenderTemplateSideslider from '../components/render-template-detail-sideslider'
    import GroupPolicy from '@/model/group-policy'
    import GroupAggregationPolicy from '@/model/group-aggregation-policy'
    import Condition from '@/model/condition'

    export default {
        name: '',
        components: {
            AddPermSideslider,
            AddActionSideslider,
            ResourceInstanceTable,
            RenderTemplateSideslider
        },
        data () {
            return {
                submitLoading: false,
                isShowAddSideslider: false,
                isShowAddActionSideslider: false,
                curActionValue: [],
                originalList: [],

                tableList: [],
                tableListBackup: [],
                tempalteDetailList: [],
                aggregationData: {},
                authorizationData: {},
                aggregationDataByCustom: {},
                authorizationDataByCustom: {},
                allAggregationData: {},
                isAllExpanded: false,

                hasDeleteCustomList: [],
                hasAddCustomList: [],
                templateDetailSideslider: {
                    isShow: false,
                    id: ''
                },
                curMap: null,
                isShowErrorTips: false
            }
        },
        computed: {
            isAggregateDisabled () {
                const aggregationIds = this.tableList.reduce((counter, item) => {
                    return item.aggregationId !== '' ? counter.concat(item.aggregationId) : counter
                }, [])
                const temps = []
                aggregationIds.forEach(item => {
                    if (!temps.some(sub => sub.includes(item))) {
                        temps.push([item])
                    } else {
                        const tempObj = temps.find(sub => sub.includes(item))
                        tempObj.push(item)
                    }
                })
                return !temps.some(item => item.length > 1) && !this.isAllExpanded
            },
            expandedText () {
                return this.isAllExpanded ? this.$t(`m.grading['逐项编辑']`) : this.$t(`m.grading['批量编辑']`)
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
            curAuthorizationData () {
                const data = Object.assign(this.authorizationData, this.authorizationDataByCustom)
                return data
            }
        },
        beforeRouteEnter (to, from, next) {
            window.FROM_ROUTER_NAME = from.name
            next()
        },
        methods: {
            handleAddCancel () {
                this.isShowAddSideslider = false
            },

            handleAddCustom () {
                this.isShowAddActionSideslider = true
            },

            handleViewDetail ({ id }) {
                this.templateDetailSideslider.id = id
                this.templateDetailSideslider.isShow = true
            },

            handleSubmitPerm (templates, aggregation, authorization) {
                // debugger
                this.isShowErrorTips = false

                if (this.isAllExpanded) {
                    this.isAllExpanded = false
                    this.handleAggregateAction(false)
                }

                this.aggregationData = aggregation
                this.authorizationData = authorization

                let hasDeleteTemplateList = []
                let hasAddTemplateList = []
                if (this.tempalteDetailList.length > 0) {
                    const intersection = templates.filter(
                        item => this.tempalteDetailList.map(sub => sub.id).includes(item.id)
                    )
                    hasDeleteTemplateList = this.tempalteDetailList.filter(
                        item => !intersection.map(sub => sub.id).includes(item.id)
                    )
                    hasAddTemplateList = templates.filter(item => !intersection.map(sub => sub.id).includes(item.id))
                } else {
                    hasAddTemplateList = templates
                }
                this.tempalteDetailList = _.cloneDeep(templates)

                if (hasDeleteTemplateList.length > 0) {
                    this.tableList = this.tableList.filter(
                        item => !hasDeleteTemplateList.map(sub => sub.id).includes(item.detail.id)
                    )
                }

                if (this.hasDeleteCustomList.length > 0) {
                    this.tableList = this.tableList.filter(item => {
                        return item.detail.id === CUSTOM_PERM_TEMPLATE_ID && !this.hasDeleteCustomList.map(sub => sub.$id).includes(`${item.detail.system.id}&${item.id}`)
                    })
                }

                const tempList = []
                hasAddTemplateList.forEach(item => {
                    const temp = _.cloneDeep(item)
                    delete temp.actions
                    item.actions.forEach(sub => {
                        tempList.push(new GroupPolicy(sub, 'add', 'template', temp))
                    })
                })

                const temps = []
                this.tableList.forEach(item => {
                    if (item.detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                        if (item.isAggregate) {
                            temps.push(item.actions.map(_ => `${_.detail.system.id}&${_.id}`))
                        } else {
                            temps.push(`${item.detail.system.id}&${item.id}`)
                        }
                    }
                })

                const addCustomList = this.hasAddCustomList.filter(item => !temps.includes(item.$id))
                addCustomList.forEach(item => {
                    tempList.push(new GroupPolicy(item, 'add', 'custom', {
                        system: {
                            id: item.system_id,
                            name: item.system_name
                        },
                        id: CUSTOM_PERM_TEMPLATE_ID
                    }))
                })

                this.tableList.push(...tempList)
                this.tableListBackup = _.cloneDeep(this.tableList)

                // 处理聚合的数据，将表格数据按照相同的聚合id分配好
                this.handleAggregateData()

                this.$nextTick(() => {
                    if (hasDeleteTemplateList.length > 0 || this.hasDeleteCustomList.length > 0) {
                        this.setCurMapData(hasDeleteTemplateList)
                    }
                })
            },

            handleResSelect (index, resIndex, condition) {
                if (this.curMap.size > 0) {
                    const item = this.tableList[index]
                    const actions = this.curMap.get(item.aggregationId) || []
                    const len = actions.length
                    if (len > 0) {
                        for (let i = 0; i < len; i++) {
                            if (actions[i].id === item.id) {
                                actions[i].related_resource_types[resIndex].condition = _.cloneDeep(condition)
                                break
                            }
                        }
                    }
                }
            },

            handleAttrValueSelected (payload) {
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
                if (instances.length > 0) {
                    const actions = this.curMap.get(payload.aggregationId)
                    actions.forEach(item => {
                        item.related_resource_types.forEach(subItem => {
                            subItem.condition = [new Condition({ instances }, '', 'add')]
                        })
                    })
                }
            },

            handleAggregateData () {
                this.allAggregationData = Object.assign(this.aggregationData, this.aggregationDataByCustom)
                const keys = Object.keys(this.allAggregationData)
                const data = {}
                keys.forEach(item => {
                    if (this.allAggregationData[item] && this.allAggregationData[item].length > 0) {
                        data[item] = this.allAggregationData[item]
                    }
                })
                this.allAggregationData = data
                this.tableList.forEach(item => {
                    if (this.allAggregationData[item.detail.system.id]) {
                        const aggregationData = this.allAggregationData[item.detail.system.id]
                        aggregationData.forEach(aggItem => {
                            if (aggItem.actions.map(act => act.id).includes(item.id)) {
                                // const existDatas = this.tableList.filter(sub => sub.judgeId === item.judgeId)
                                const existDatas = this.tableList.filter(
                                    sub => aggItem.actions.find(act => act.id === sub.id)
                                        && sub.judgeId === item.judgeId
                                )
                                if (existDatas.length > 1) {
                                    const temp = existDatas.find(sub => sub.aggregationId !== '') || {}
                                    item.aggregationId = temp.aggregationId || guid()
                                    item.aggregateResourceType = aggItem.aggregate_resource_type
                                }
                            }
                        })
                    }
                })
                const aggregationIds = this.tableList.reduce((counter, item) => {
                    return item.aggregationId !== '' ? counter.concat(item.aggregationId) : counter
                }, [])
                console.warn('aggregationIds:')
                console.warn([...new Set(aggregationIds)])
                if (!this.curMap) {
                    this.curMap = new Map()
                }
                this.tableList.forEach(item => {
                    if (item.aggregationId !== '') {
                        if (!this.curMap.has(item.aggregationId)) {
                            this.curMap.set(item.aggregationId, [item])
                        } else {
                            const temps = this.curMap.get(item.aggregationId)
                            if (!temps.map(sub => sub.id).includes(item.id)) {
                                temps.push(item)
                            }
                        }
                    }
                })
            },

            setCurMapData (payload = []) {
                const flag = String(Number(payload.length > 0)) + String(Number(this.hasDeleteCustomList.length > 0))
                const hasDeleteIds = payload.map(item => item.id)
                const hasDeleteIdsTemp = this.hasDeleteCustomList.map(_ => _.$id)
                const tempData = {}
                for (const [key, value] of this.curMap.entries()) {
                    tempData[key] = value
                }
                const tempDataBackup = {}
                switch (flag) {
                    case '11':
                        for (const key in tempData) {
                            const value = tempData[key]
                            if (value[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID) {
                                const tempValue = _.cloneDeep(value)
                                if (!value.every(item => hasDeleteIds.includes(item.detail.id))) {
                                    tempDataBackup[key] = tempValue
                                }
                            }
                        }
                        for (const key in tempData) {
                            const value = tempData[key]
                            if (value[0].detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                                let tempValue = _.cloneDeep(value)
                                tempValue = tempValue.filter(item => !hasDeleteIdsTemp.includes(`${item.detail.system.id}&${item.id}`))
                                if (tempValue.length > 0) {
                                    tempDataBackup[key] = tempValue
                                }
                            }
                        }
                        break
                    case '10':
                        for (const key in tempData) {
                            const value = tempData[key]
                            if (value[0].detail.id !== CUSTOM_PERM_TEMPLATE_ID) {
                                if (!value.every(item => hasDeleteIds.includes(item.detail.id))) {
                                    tempDataBackup[key] = value
                                }
                            } else {
                                tempDataBackup[key] = value
                            }
                        }
                        break
                    case '01':
                        for (const key in tempData) {
                            const value = tempData[key]
                            if (value[0].detail.id === CUSTOM_PERM_TEMPLATE_ID) {
                                let tempValue = _.cloneDeep(value)
                                tempValue = tempValue.filter(item => !hasDeleteIdsTemp.includes(`${item.detail.system.id}&${item.id}`))
                                if (tempValue.length > 0) {
                                    tempDataBackup[key] = tempValue
                                }
                            } else {
                                tempDataBackup[key] = value
                            }
                        }
                        break
                }
                this.curMap.clear()
                for (const key in tempDataBackup) {
                    this.curMap.set(key, _.cloneDeep(tempDataBackup[key]))
                }

                console.warn('curMap: ')
                console.warn(this.curMap)
                console.warn(this.tableList)
            },

            handleAggregateAction (payload) {
                const tempData = []
                let templateIds = []
                if (payload) {
                    this.tableList.forEach(item => {
                        if (!item.aggregationId) {
                            tempData.push(item)
                            templateIds.push(item.detail.id)
                        }
                    })
                    for (const [key, value] of this.curMap.entries()) {
                        if (value.length === 1) {
                            tempData.push(...value)
                        } else {
                            let curInstances = []
                            const conditions = value.map(subItem => subItem.related_resource_types[0].condition)
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
                                    curInstances = instanceData.path.map(pathItem => {
                                        return {
                                            id: pathItem[0].id,
                                            name: pathItem[0].name
                                        }
                                    })
                                } else {
                                    curInstances = []
                                }
                            } else {
                                curInstances = []
                            }
                            tempData.push(new GroupAggregationPolicy({
                                aggregationId: key,
                                aggregate_resource_type: value[0].aggregateResourceType,
                                actions: value,
                                instances: curInstances
                            }))
                        }
                        templateIds.push(value[0].detail.id)
                    }
                } else {
                    this.tableList.forEach(item => {
                        if (item.hasOwnProperty('isAggregate') && item.isAggregate) {
                            const actions = this.curMap.get(item.aggregationId)
                            tempData.push(...actions)
                            templateIds.push(actions[0].detail.id)
                        } else {
                            tempData.push(item)
                            templateIds.push(item.detail.id)
                        }
                    })
                }
                // 为了合并单元格的计算，需将再次展开后的数据按照相同模板id重新排序组装一下
                const tempList = []
                templateIds = [...new Set(templateIds)]
                templateIds.forEach(item => {
                    const list = tempData.filter(subItem => subItem.detail.id === item)
                    tempList.push(...list)
                })
                this.tableList = _.cloneDeep(tempList)
            },

            handleEditCustom () {
                this.curActionValue = this.originalList.map(item => item.$id)
                this.isShowAddActionSideslider = true
            },

            // 添加系统和操作 侧边栏确定按钮回调
            handleSelectSubmit (payload, aggregation, authorization) {
                // debugger
                this.isShowErrorTips = false
                const hasAddCustomList = []
                hasAddCustomList.splice(0, 0, ...this.hasAddCustomList)
                if (this.originalList.length > 0) {
                    const intersection = payload.filter(
                        item => this.originalList.map(sub => sub.$id).includes(item.$id)
                    )
                    this.hasDeleteCustomList = this.originalList.filter(
                        item => !intersection.map(sub => sub.$id).includes(item.$id)
                    )
                    hasAddCustomList.push(
                        ...payload.filter(item => !intersection.map(sub => sub.$id).includes(item.$id))
                    )
                } else {
                    hasAddCustomList.push(...payload)
                }

                this.hasAddCustomList.splice(0, this.hasAddCustomList.length, ...hasAddCustomList)

                this.originalList = _.cloneDeep(payload)
                this.aggregationDataByCustom = _.cloneDeep(aggregation)
                this.authorizationDataByCustom = _.cloneDeep(authorization)
            },

            async handleSubmit () {
                // debugger
                const { flag, templates } = this.$refs.resInstanceTableRef.getData()
                if (flag) {
                    this.isShowErrorTips = true
                    return
                }
                this.submitLoading = true
                window.changeDialog = false
                const params = {
                    id: this.$route.params.id,
                    data: {
                        templates
                    }
                }
                try {
                    await this.$store.dispatch('userGroup/addUserGroupPolicy', params)
                    this.messageSuccess(this.$t(`m.info['用户组添加权限成功']`), 1000)
                    this.setBackRouter()
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

            setBackRouter () {
                if (window.FROM_ROUTER_NAME === 'userGroupDetail') {
                    this.$router.push({
                        name: 'userGroupDetail',
                        params: {
                            id: this.$route.params.id
                        }
                    })
                } else {
                    this.$router.push({
                        name: 'userGroup'
                    })
                }
                delete window.FROM_ROUTER_NAME
            },

            handleCancel () {
                let cancelHandler = Promise.resolve()
                if (window.changeDialog) {
                    cancelHandler = leavePageConfirm()
                }
                cancelHandler.then(() => {
                    this.setBackRouter()
                }, _ => _)
            },

            handleAddPerm () {
                this.isShowAddSideslider = true
            }
        }
    }
</script>
<style lang="postcss" scoped>
    .iam-add-group-perm-wrapper {
        .grade-admin-select-wrapper {
            .action {
                position: relative;
                display: flex;
                justify-content: flex-start;
                .action-wrapper {
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
            .info-wrapper {
                display: flex;
                justify-content: flex-end;
                margin-top: 16px;
                line-height: 24px;
                .tips,
                .text {
                    line-height: 20px;
                    font-size: 12px;
                }
            }
        }
    }
</style>
