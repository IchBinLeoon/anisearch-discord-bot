<template>
  <router-link :to="path" class="link">
    <slot />
    <font-awesome-icon v-if="icon" :icon="icon" />
  </router-link>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'NavigationLink',
  props: {
    path: String,
    icon: {
      type: Array,
    },
  },
})
</script>

<style scoped lang="scss">
.link {
  display: block;

  font-size: 1rem;
  font-weight: 500;
  color: $primary-text-color;
  text-decoration: none;

  transition: 0.3s ease-out;

  padding: 0 1.5rem;

  &:hover {
    color: $brand-color;
  }

  svg {
    margin-left: 10px;
  }

  @media screen and (max-width: 850px) {
    padding: 0.5rem 0;
  }
}
</style>
