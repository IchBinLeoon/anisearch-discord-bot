<template>
  <NavigationBar />
  <router-view />
  <CopyrightFooter />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import NavigationBar from '@/components/NavigationBar.vue'
import CopyrightFooter from '@/components/CopyrightFooter.vue'

export default defineComponent({
  name: 'App',
  components: {
    NavigationBar,
    CopyrightFooter,
  },
})
</script>

<style lang="scss">
* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  background-color: $primary-background-color;
}

#app {
  width: 100%;
  font-family: $primary-font-family;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
