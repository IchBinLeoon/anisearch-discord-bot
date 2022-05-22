<template>
  <router-link to="/invite">
    <button>Invite</button>
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
  width: 200px;
  height: 75px;

  border: none;
  border-radius: 5px;

  color: $tertiary-text-color;
  background-color: $brand-color;

  font-size: 2rem;
  font-family: $primary-font-family;
  cursor: pointer;

  transition: 0.3s ease-out;
  box-shadow: 0 5px 15px 0 rgba($color: #000000, $alpha: 0.2);

  &:hover {
    filter: brightness(120%);
  }
}
</style>
