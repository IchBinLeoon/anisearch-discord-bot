<template>
  <router-link to="/github">
    <button><font-awesome-icon :icon="['fab', 'github']" />GitHub</button>
  </router-link>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'InviteButton',
})
</script>

<style scoped lang="scss">
button {
  width: 175px;
  height: 60px;

  border: 2px solid $github-color;
  border-radius: 5px;

  color: $github-color;
  background-color: $primary-background-color;

  font-size: 1.5rem;
  font-family: $primary-font-family;
  cursor: pointer;

  transition: 0.3s ease-out;

  svg {
    margin-right: 15px;
  }

  &:hover {
    color: $tertiary-text-color;
    background-color: $github-color;
  }
}
</style>
