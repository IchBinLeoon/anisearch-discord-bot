<template>
  <router-link to="/support">
    <button>Support Server</button>
  </router-link>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SupportButton',
})
</script>

<style scoped lang="scss">
button {
  width: 230px;
  height: 60px;

  border: 2px solid $brand-color;
  border-radius: 5px;

  color: $brand-color;
  background-color: $primary-background-color;

  font-size: 1.2rem;
  font-family: $primary-font-family;
  cursor: pointer;

  transition: 0.3s ease-out;

  &:hover {
    color: $tertiary-text-color;
    background-color: $brand-color;
  }
}
</style>
