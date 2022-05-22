<template>
  <div class="bar">
    <input
      type="text"
      v-model="search"
      @input="onInput()"
      placeholder="Search a command..."
    />
    <ul v-show="isOpen">
      <li v-for="result in results" :key="result">
        <a @click="scrollToItem(result)"> {{ result }}</a>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CommandsSearchBar',
  data() {
    return {
      search: '',
      results: [] as unknown[],
      isOpen: false,
    }
  },
  props: {
    items: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    onInput() {
      this.filterResults()
      this.isOpen = this.search === '' ? false : true
    },
    filterResults() {
      this.results = this.items.filter((item) =>
        String(item).toLowerCase().includes(this.search.toLowerCase())
      )
    },
    scrollToItem(command: string) {
      this.search = ''
      this.isOpen = false
      document.getElementById(command)?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'center',
      })
    },
  },
})
</script>

<style scoped lang="scss">
.bar {
  position: relative;

  input {
    width: 100%;
    padding: 1rem;

    color: $primary-text-color;
    font-size: 1rem;

    outline: none;
    border: none;

    border: $primary-text-color 1px solid;
    border-radius: 5px;
  }

  ul {
    padding: 0.5rem 0;
    margin: 0;

    position: absolute;
    z-index: 1;
    width: 100%;

    background-color: $primary-background-color;
    border-radius: 5px;

    box-shadow: 0 10px 15px 0 rgba($color: #000000, $alpha: 0.2);

    li {
      list-style: none;
      text-align: left;
      padding: 0 0.5rem;
      width: 100%;

      a {
        display: block;
        width: 100%;
        padding: 1rem;

        border-radius: 5px;

        color: $primary-text-color;
        font-size: 1rem;
        cursor: pointer;

        &:hover {
          background-color: darken($primary-background-color, $amount: 10);
        }
      }
    }
  }
}
</style>
