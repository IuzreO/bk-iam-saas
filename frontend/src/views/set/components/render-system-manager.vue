<template>
    <div class="iam-set-system-manager-wrapper">
        <render-item
            :sub-title="subTitle"
            expanded>
            <bk-table
                :data="systemUserList"
                size="small"
                ext-cls="system-user-table-cls"
                :outer-border="false"
                :header-border="false"
                @row-mouse-enter="handleSysRowMouseEnter"
                @row-mouse-leave="handleSysRowMouseLeave">
                <bk-table-column :label="$t(`m.set['系统名称']`)" prop="name"></bk-table-column>
                <bk-table-column :label="$t(`m.set['成员列表']`)">
                    <template slot-scope="{ row, $index }">
                        <template v-if="row.isEdit">
                            <bk-user-selector
                                :value="row.members"
                                :ref="`sysRef${$index}`"
                                :api="userApi"
                                :class="row.isError ? 'is-member-empty-cls' : ''"
                                :placeholder="$t(`m.verify['请输入']`)"
                                style="width: 100%;"
                                @blur="handleSystemRtxBlur(row)"
                                @change="handleSystemRtxChange(...arguments, row)"
                                @keydown="handleSystemRtxEnter(...arguments, row)">
                            </bk-user-selector>
                        </template>
                        <template v-else>
                            <div
                                :class="['user-wrapper', { 'is-hover': row.canEdit }]"
                                @click.stop="handleOpenSysEdit(row, $index)">
                                {{ row.members | memberFilter }}
                            </div>
                        </template>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t(`m.set['更多权限设置']`)">
                    <template slot-scope="{ row }">
                        <bk-checkbox
                            :true-value="true"
                            :false-value="false"
                            :value="row.system_permission_global_enabled"
                            @change="handleSystemEnabledChange(...arguments, row)">
                            {{ $t(`m.set['拥有该系统的所有操作权限']`) }}
                        </bk-checkbox>
                    </template>
                </bk-table-column>
            </bk-table>
        </render-item>
    </div>
</template>
<script>
    import _ from 'lodash'
    import BkUserSelector from '@blueking/user-selector'
    import RenderItem from '../common/render-item'
    export default {
        name: '',
        components: {
            BkUserSelector,
            RenderItem
        },
        filters: {
            memberFilter (value) {
                if (value.length > 0) {
                    return value.join('；')
                }
                return '--'
            }
        },
        data () {
            return {
                subTitle: this.$t(`m.set['系统管理员提示']`),
                systemUserList: [],
                userApi: window.BK_USER_API
            }
        },
        created () {
            this.fetchSystemManager()
        },
        methods: {
            async fetchSystemManager () {
                this.$emit('data-ready', false)
                try {
                    const res = await this.$store.dispatch('role/getSystemManager')
                    const tempArr = []
                    res.data.forEach(item => {
                        tempArr.push({
                            ...item,
                            memberBackup: _.cloneDeep(item.members),
                            isEdit: false,
                            isError: false
                        })
                    })
                    this.systemUserList.splice(0, this.systemUserList.length, ...tempArr)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                } finally {
                    this.$emit('data-ready', true)
                }
            },

            handleSystemRtxChange (payload, row) {
                row.isError = false
                row.members = [...payload]
            },

            handleSystemRtxEnter (event, payload) {
                if (event.keyCode === 13) {
                    event.stopPropagation()
                    this.handleSystemRtxBlur(payload)
                }
            },

            handleSysRowMouseEnter (index) {
                this.$set(this.systemUserList[index], 'canEdit', true)
            },

            handleSysRowMouseLeave (index) {
                this.$delete(this.systemUserList[index], 'canEdit')
            },

            handleOpenSysEdit (payload, index) {
                if (!payload.canEdit) {
                    return
                }
                payload.isEdit = true
                this.$nextTick(() => {
                    this.$refs[`sysRef${index}`].focus()
                })
            },

            async handleSystemRtxBlur (payload) {
                const ms = JSON.parse(JSON.stringify(payload.members))
                const mbs = JSON.parse(JSON.stringify(payload.memberBackup))
                if (_.isEqual(ms.sort(), mbs.sort())) {
                    setTimeout(() => {
                        payload.isEdit = false
                    }, 10)
                    return
                }
                if (payload.members.length < 1) {
                    payload.isError = true
                    return
                }
                const { id, members } = payload
                try {
                    this.$store.dispatch('role/editSystemManagerMember', {
                        id,
                        members
                    })
                    setTimeout(() => {
                        payload.isEdit = false
                        payload.memberBackup = _.cloneDeep(members)
                        this.messageSuccess(this.$t(`m.common['操作成功']`))
                    }, 10)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            },

            async handleSystemEnabledChange (newVal, oldVal, val, payload) {
                try {
                    await this.$store.dispatch('role/editSystemManagerPerm', {
                        id: payload.id,
                        system_permission_global_enabled: newVal
                    })
                    payload.system_permission_global_enabled = newVal
                    const message = newVal ? this.$t(`m.set['设置成功']`) : this.$t(`m.set['取消设置成功']`)
                    this.messageSuccess(message)
                } catch (e) {
                    console.error(e)
                    this.bkMessageInstance = this.$bkMessage({
                        limit: 1,
                        theme: 'error',
                        message: e.message || e.data.msg || e.statusText
                    })
                }
            }
        }
    }
</script>
<style lang="postcss">
    .iam-set-system-manager-wrapper {
        .system-user-table-cls {
            border: none;
            tr {
                &:hover {
                    background-color: transparent;
                    & > td {
                        background-color: transparent;
                    }
                }
            }
            .user-wrapper {
                padding: 0 8px;
                width: 100%;
                height: 32px;
                line-height: 32px;
                border-radius: 2px;
                &.is-hover {
                    background: #f0f1f5;
                    cursor: pointer;
                }
            }
            .is-member-empty-cls {
                .user-selector-container {
                    border-color: #ff4d4d;
                }
            }
        }
    }
</style>
