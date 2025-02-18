<template>
    <div id="app" :class="systemCls">
        <iam-guide
            v-if="groupGuideShow"
            type="create_group"
            direction="left"
            :style="groupGuideStyle"
            :flag="groupGuideShow"
            :content="$t(`m.guide['创建用户组']`)" />
        <iam-guide
            v-if="processGuideShow"
            type="set_group_approval_process"
            direction="left"
            :style="processGuideStyle"
            :flag="processGuideShow"
            :content="$t(`m.guide['创建审批流程']`)" />
        <the-header @reload-page="handleRefreshPage"
            :route-name="routeName"
            :user-group-name="userGroupName"
            :user-group-id="userGroupId"
            v-if="isRouterAlive">
        </the-header>
        <the-nav class="nav-layout" @reload-page="reloadCurPage"></the-nav>
        <main class="main-layout" :class="layoutCls"
            v-bkloading="{ isLoading: mainContentLoading, opacity: 1, zIndex: 1000 }">
            <div ref="mainScroller" class="main-scroller" v-if="isShowPage">
                <router-view class="views-layout" :key="routerKey" v-show="!mainContentLoading"></router-view>
            </div>
        </main>
        <app-auth ref="bkAuth"></app-auth>
    </div>
</template>
<script>
    import theHeader from '@/components/header'
    import theNav from '@/components/nav'
    import IamGuide from '@/components/iam-guide'
    import { bus } from '@/common/bus'
    import { mapGetters } from 'vuex'
    import { afterEach } from '@/router'
    import { kebabCase } from 'lodash'
    export default {
        name: 'app',
        provide () {
            return {
                reload: this.reload
            }
        },
        components: {
            IamGuide,
            theHeader,
            theNav
        },
        data () {
            return {
                routerKey: +new Date(),
                systemCls: 'mac',
                timer: null,
                layoutCls: '',
                isShowPage: true,
                groupGuideStyle: {
                    top: '140px',
                    left: '270px'
                },
                processGuideStyle: {
                    top: '342px',
                    left: '270px'
                },
                processGuideShow: false,
                groupGuideShow: false,
                routeName: '',
                userGroupId: '',
                userGroupName: '',
                isRouterAlive: true
            }
        },
        computed: {
            ...mapGetters(['mainContentLoading', 'user'])
        },
        watch: {
            '$route' (to, from) {
                this.layoutCls = kebabCase(to.name) + '-container'
                this.routeName = to.name
                this.userGroupId = to.params.id
                this.$store.commit('updateRoute', from.name)
            },
            user: {
                handler (value) {
                    if (['rating_manager', 'system_manager'].includes(value.role.type)) {
                        this.processGuideStyle.top = '220px'
                    }
                    if (value.role.type === 'super_manager') {
                        this.processGuideStyle.top = '342px'
                    }
                },
                immediate: true,
                deep: true
            }
        },
        created () {
            const platform = window.navigator.platform.toLowerCase()
            if (platform.indexOf('win') === 0) {
                this.systemCls = 'win'
            }
            this.fetchVersionLog()
            this.fetchNoviceGuide()
            const isPoll = window.localStorage.getItem('isPoll')
            if (isPoll) {
                this.$store.commit('updateSync', true)
                this.timer = setInterval(() => {
                    this.fetchSyncStatus()
                }, 15000)
            }
            this.$once('hook:beforeDestroy', () => {
                bus.$off('show-login-modal')
                bus.$off('close-login-modal')
                bus.$off('updatePoll')
                bus.$off('nav-resize')
                bus.$off('show-guide')
            })
        },
        mounted () {
            const self = this
            bus.$on('show-login-modal', (payload) => {
                self.$refs.bkAuth.showLoginModal(payload)
            })
            bus.$on('close-login-modal', () => {
                self.$refs.bkAuth.hideLoginModal()
                setTimeout(() => {
                    window.location.reload()
                }, 0)
            })
            bus.$on('updatePoll', () => {
                clearInterval(this.timer)
                this.timer = setInterval(() => {
                    this.fetchSyncStatus()
                }, 15000)
            })
            bus.$on('nav-resize', flag => {
                this.groupGuideStyle.left = flag ? '270px' : '90px'
                this.processGuideStyle.left = flag ? '270px' : '90px'
            })
            bus.$on('show-guide', payload => {
                if (payload === 'group') {
                    this.groupGuideShow = true
                }
                if (payload === 'process') {
                    this.processGuideShow = true
                }
            })
        },
        methods: {
            reload () {
                this.isRouterAlive = false
                this.$nextTick(() => {
                    this.isRouterAlive = true
                })
            },
            /**
             * 刷新当前 route，这个刷新和 window.location.reload 不同，这个刷新会保持 route.params
             *
             * @param {Object} route 要刷新的 route
             */
            reloadCurPage (route) {
                this.routerKey = +new Date()
                afterEach(route)
            },

            handleRefreshPage (route) {
                this.isShowPage = false
                this.$nextTick(() => {
                    this.isShowPage = true
                    this.routerKey = +new Date()
                    afterEach(route)
                })
            },
            async fetchVersionLog () {
                try {
                    await this.$store.dispatch('versionLogInfo')
                } catch (e) {
                    console.error(e)
                }
            },

            async fetchNoviceGuide () {
                try {
                    await this.$store.dispatch('getNoviceGuide')
                } catch (e) {
                    console.error(e)
                }
            },

            async fetchSyncStatus () {
                try {
                    const res = await this.$store.dispatch('organization/getOrganizationsSyncTask')
                    const status = res.data.status
                    if (status === 'Succeed' || status === 'Failed') {
                        if (status === 'Succeed') {
                            bus.$emit('sync-success')
                        }
                        window.localStorage.removeItem('isPoll')
                        this.$store.commit('updateSync', false)
                        clearInterval(this.timer)
                        this.bkMessageInstance = this.$bkMessage({
                            limit: 1,
                            theme: status === 'Succeed' ? 'success' : 'error',
                            message: status === 'Succeed' ? this.$t(`m.permTemplate['同步组织架构成功']`) : this.$t(`m.permTemplate['同步组织架构失败']`)
                        })
                    }
                } catch (e) {
                    console.error(e)
                    window.localStorage.removeItem('isPoll')
                    this.$store.commit('updateSync', false)
                    clearInterval(this.timer)
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
    @import './css/index';

    .nav-layout {
        position: relative;
        float: left;
        height: 100%;
        margin: -61px 0 0 0;
    }

    .main-layout {
        position: relative;
        height: calc(100% - 61px);
        background-color: #f5f6fa;
        overflow: hidden;
    }

    .main-scroller {
        height: 100%;
        overflow: auto;
    }

    .views-layout {
        min-height: 100%;
        min-width: 1120px;
        padding: 24px;
    }
</style>
