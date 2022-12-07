import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CommandsView from '../views/CommandsView.vue'
import TeamView from '../views/TeamView.vue'
import LostView from '../views/LostView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/commands',
    name: 'Commands',
    component: CommandsView,
  },
  {
    path: '/team',
    name: 'Team',
    component: TeamView,
  },
  {
    path: '/invite',
    name: 'Invite',
    component: () =>
      (window.location.href =
        'https://discord.com/api/oauth2/authorize?client_id=737236600878137363&permissions=18432&scope=bot%20applications.commands'),
  },
  {
    path: '/support',
    name: 'Support',
    component: () => (window.location.href = 'https://discord.gg/Bv94yQYZM8'),
  },
  {
    path: '/github',
    name: 'Github',
    component: () =>
      (window.location.href =
        'https://github.com/IchBinLeoon/anisearch-discord-bot'),
  },
  {
    path: '/:pathName(.*)*',
    name: 'Lost',
    component: LostView,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  document.title = String(to.name) + ' | AniSearch Bot'
  next()
})

export default router
