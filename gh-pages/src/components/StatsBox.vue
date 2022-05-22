<template>
  <div class="box">
    <h1>{{ value }}</h1>
    <h2>{{ name }}</h2>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'StatsBox',
  props: {
    name: String,
    value: String,
  },
})
</script>

<style scoped lang="scss">
.box {
  text-align: center;
  padding: 2rem 0;

  width: 250px;

  background-color: $primary-background-color;

  border-radius: 15px;
  box-shadow: 0 10px 15px 0 rgba($color: #000000, $alpha: 0.2);

  h1 {
    color: $primary-text-color;
    font-size: 3rem;
  }

  h2 {
    color: $primary-text-color;
    font-size: 2rem;
  }
}
</style>
