<template>
  <main>
    <div class="lost">
      <img src="@/assets/lost.png" />
      <h1>Lost? Pathetic.</h1>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LostView',
})
</script>

<style scoped lang="scss">
.lost {
  text-align: center;
  background-color: $primary-background-color;
  padding: 7.5rem 0 3rem 0;

  h1 {
    color: $primary-text-color;
    font-size: 2rem;
  }

  img {
    max-width: 80%;
  }
}
</style>
