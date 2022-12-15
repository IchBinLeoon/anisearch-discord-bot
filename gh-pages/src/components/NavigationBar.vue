<template>
  <header>
    <nav class="navbar sticky">
      <router-link to="/" class="title"
        ><font-awesome-icon :icon="['fas', 'magnifying-glass']" />AniSearch
        Bot</router-link
      >
      <a @click="showMobileMenu = !showMobileMenu" class="mobile-toggle">
        <font-awesome-icon :icon="['fas', 'bars']" />
      </a>
      <div class="links" :class="{ active: showMobileMenu }">
        <ul>
          <li v-for="link in links" :key="link">
            <NavigationLink :path="link.path" :icon="link.icon">{{
              link.name
            }}</NavigationLink>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import NavigationLink from '@/components/NavigationLink.vue'

export default defineComponent({
  name: 'NavigationBar',
  components: {
    NavigationLink,
  },
  data() {
    return {
      links: [
        {
          name: 'Commands',
          path: '/commands',
          icon: null,
        },
        {
          name: 'Invite',
          path: '/invite',
          icon: ['fas', 'up-right-from-square'],
        },
        {
          name: 'Support',
          path: '/support',
          icon: ['fas', 'up-right-from-square'],
        },
        {
          name: 'GitHub',
          path: '/github',
          icon: ['fab', 'github'],
        },
      ],
      showMobileMenu: false,
    }
  },
})
</script>

<style scoped lang="scss">
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 1.5rem 2rem;
  z-index: 999;

  background-color: $primary-background-color;
  box-shadow: 0 1px 5px 0 rgba($color: #000000, $alpha: 0.1);

  .title {
    font-size: 1.5rem;
    font-weight: 700;
    color: $primary-text-color;
    text-decoration: none;

    svg {
      margin-right: 10px;
    }
  }

  .links {
    ul {
      display: flex;
      margin: 0;
      padding: 0;

      li {
        list-style: none;
      }
    }
  }

  @media screen and (max-width: 850px) {
    flex-direction: column;
    align-items: flex-start;

    .links {
      display: none;
      width: 100%;
      margin-top: 20px;

      &.active {
        display: flex;
      }

      ul {
        flex-direction: column;
        width: 100%;

        li {
          text-align: center;
        }
      }
    }
  }
}

.sticky {
  position: fixed;
  top: 0;
  width: 100%;
}

.mobile-toggle {
  position: absolute;
  right: 1.5rem;

  display: none;
  flex-direction: column;
  justify-content: space-between;

  font-size: 2rem;
  color: $primary-text-color;
  cursor: pointer;

  transition: 0.3s ease-out;

  @media screen and (max-width: 850px) {
    display: flex;
  }
}
</style>
