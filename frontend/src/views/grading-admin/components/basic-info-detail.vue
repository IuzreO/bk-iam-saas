<template>
    <div class="iam-grading-admin-basic-info-wrapper">
        <detail-layout mode="see">
            <render-layout>
                <detail-item :label="$t(`m.gradingDetail['分级管理员名称']`)">
                    <iam-edit-input
                        field="name"
                        :placeholder="$t(`m.verify['请输入']`)"
                        :rules="rules"
                        :value="formData.name"
                        :remote-hander="handleUpdateRatingManager" />
                </detail-item>
                <detail-item :label="$t(`m.gradingDetail['成员列表']`)">
                    <iam-edit-member
                        field="members"
                        :value="formData.members"
                        :remote-hander="handleUpdateRatingManager" />
                </detail-item>
                <detail-item :label="$t(`m.userGroupDetail['描述']`)">
                    <iam-edit-textarea
                        field="description"
                        width="600px"
                        :value="formData.description"
                        :remote-hander="handleUpdateRatingManager" />
                </detail-item>
            </render-layout>
        </detail-layout>
    </div>
</template>
<script>
    import DetailLayout from '@/components/detail-layout'
    import DetailItem from '@/components/detail-layout/item'
    import IamEditInput from '@/components/iam-edit/input'
    import IamEditTextarea from '@/components/iam-edit/textarea'
    import IamEditMember from './member-edit'
    import RenderLayout from '../../group/common/render-layout'

    export default {
        name: '',
        components: {
            DetailLayout,
            DetailItem,
            IamEditInput,
            IamEditTextarea,
            RenderLayout,
            IamEditMember
        },
        props: {
            data: {
                type: Object,
                default () {
                    return {}
                }
            },
            id: {
                type: [String, Number],
                default: ''
            }
        },
        data () {
            return {
                formData: {
                    name: '',
                    description: '',
                    members: []
                }
            }
        },
        watch: {
            data: {
                handler (value) {
                    if (Object.keys(value).length) {
                        this.formData = Object.assign({}, value)
                    }
                },
                immediate: true
            }
        },
        created () {
            this.rules = [
                {
                    required: true,
                    message: this.$t(`m.verify['分级管理员名称必填']`),
                    trigger: 'blur'
                },
                {
                    validator: (value) => {
                        return value.length <= 32
                    },
                    message: this.$t(`m.verify['分级管理员名称最长不超过32个字符']`),
                    trigger: 'blur'
                },
                {
                    validator: (value) => {
                        return /^[^\s]*$/g.test(value)
                    },
                    message: this.$t(`m.verify['分级管理员名称不允许空格']`),
                    trigger: 'blur'
                }
            ]
        },
        methods: {
            handleUpdateRatingManager (payload) {
                const { name, members, description } = this.formData
                const params = {
                    name,
                    description,
                    members,
                    ...payload,
                    id: this.id
                }
                return this.$store.dispatch('role/updateRatingManager', params)
                    .then(async () => {
                        this.messageSuccess(this.$t(`m.info['编辑成功']`), 2000)
                        this.formData.name = params.name
                        this.formData.description = params.description
                        this.formData.members = [...params.members]
                        const headerTitle = params.name
                        this.$store.commit('setHeaderTitle', headerTitle)
                        await this.$store.dispatch('roleList')
                    }, (e) => {
                        console.warn('error')
                        this.bkMessageInstance = this.$bkMessage({
                            limit: 1,
                            theme: 'error',
                            message: e.message || e.data.msg || e.statusText
                        })
                    })
            }
        }
    }
</script>
<style lang="postcss">
    .iam-grading-admin-basic-info-wrapper {
        position: relative;
        top: -6px;
    }
</style>
