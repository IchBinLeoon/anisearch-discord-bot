<template>
  <div class="card">
    <img :src="image" class="image" />
    <h1><slot /></h1>
    <div class="socials">
      <a v-for="social in socials" :key="social" :href="social.link">
        <img :src="social.image" />
      </a>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'InviteButton',
  props: {
    image: String,
    socials: {
      type: Array,
    },
  },
})
</script>

<style scoped lang="scss">
.card {
  text-align: center;

  width: 350px;

  border-radius: 15px;
  box-shadow: 0 10px 15px 0 rgba($color: #000000, $alpha: 0.2);

  background-color: $secondary-background-color;

  &:hover {
    position: relative;
    top: -5px;
  }

  .image {
    max-width: 60%;
    border-radius: 50%;

    margin: 2rem 0 1rem 0;
  }

  h1 {
    color: $tertiary-text-color;
    font-size: 2rem;
    font-weight: 500;
    margin: 0;
  }

  .socials {
    display: flex;
    justify-content: center;
    align-items: center;

    margin: 1rem 0;

    a {
      display: inline-block;
      padding: 1rem;
    }

    img {
      width: 2rem;
    }
  }

  @media screen and (max-width: 450px) {
    width: 245px;

    h1 {
      font-size: 1.4rem;
    }

    .socials {
      img {
        width: 1.4rem;
      }
    }
  }

  @media screen and (max-width: 350px) {
    width: 210px;

    h1 {
      font-size: 1.2rem;
    }

    .socials {
      img {
        width: 1.2rem;
      }
    }
  }
}
</style>
