<template>
  <footer>
    <div class="footer">
      <p>
        <b>© 2022 AniSearch Bot.</b> Made with
        <font-awesome-icon :icon="['fas', 'heart']" /> by
        <a href="https://github.com/IchBinLeoon" target="_blank">IchBinLeoon</a>
      </p>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CopyrightFooter',
})
</script>

<style scoped lang="scss">
.footer {
  margin: 0 15%;
  padding: 3rem 0;
  text-align: center;
  border-top: 1px solid $divider-color;

  p {
    font-size: 1rem;
    color: $secondary-text-color;

    a {
      color: $brand-color;

      &:hover {
        color: darken($brand-color, $amount: 20);
      }
    }
  }
}
</style>
