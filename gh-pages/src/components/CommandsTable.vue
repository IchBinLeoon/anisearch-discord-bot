<template>
  <table cellspacing="0" cellpadding="0">
    <tr class="head">
      <th>Usage</th>
      <th>Description</th>
    </tr>
    <tr
      v-for="command in commands"
      :key="command"
      class="command"
      :id="command.name"
    >
      <td class="usage">
        <code>{{ command.usage }}</code>
      </td>
      <td class="description">{{ command.description }}</td>
    </tr>
  </table>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'CommandsTable',
  props: {
    commands: {
      type: Array,
    },
  },
})
</script>

<style scoped lang="scss">
table {
  width: 100%;

  box-shadow: 0 10px 15px 0 rgba($color: #000000, $alpha: 0.2);

  .head {
    background-color: $secondary-background-color;
  }

  .command {
    background-color: $primary-background-color;

    &:hover {
      background-color: darken($primary-background-color, $amount: 10);
    }
  }

  th {
    color: $tertiary-text-color;
    font-size: 1rem;
    padding: 1rem 0.5rem;
    text-align: left;
  }

  td {
    color: $primary-text-color;
    font-size: 0.9rem;
    padding: 0.7rem 0.5rem;
  }

  .usage {
    width: 25%;
  }

  .description {
    width: 75%;
  }
}
</style>
