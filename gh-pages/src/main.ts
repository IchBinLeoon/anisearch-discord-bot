import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faUpRightFromSquare,
  faBars,
  faHeart,
  faCopyright,
  faMagnifyingGlass,
  faCircleArrowRight,
} from '@fortawesome/free-solid-svg-icons'
import { faGithub } from '@fortawesome/free-brands-svg-icons'

library.add(
  faUpRightFromSquare,
  faBars,
  faHeart,
  faCopyright,
  faMagnifyingGlass,
  faGithub,
  faCircleArrowRight
)

createApp(App)
  .component('font-awesome-icon', FontAwesomeIcon)
  .use(router)
  .mount('#app')
