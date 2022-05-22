<template>
  <router-link to="/commands">
    <button>
      Commands<font-awesome-icon :icon="['fas', 'circle-arrow-right']" />
    </button>
  </router-link>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CommandsButton',
})
</script>

<style scoped lang="scss">
button {
  width: 275px;
  height: 100px;

  border: none;
  border-radius: 5px;

  color: $primary-text-color;
  background-color: $primary-background-color;

  font-size: 2.2rem;
  font-family: $primary-font-family;
  cursor: pointer;

  transition: 0.3s ease-out;
  box-shadow: 0 5px 15px 0 rgba($color: #000000, $alpha: 0.2);

  svg {
    margin-left: 15px;
  }

  &:hover {
    filter: brightness(80%);
  }
}
</style>
