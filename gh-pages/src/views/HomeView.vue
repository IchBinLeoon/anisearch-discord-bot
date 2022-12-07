<template>
  <main>
    <div class="home">
      <img src="@/assets/logo.png" />
      <h1>AniSearch Bot</h1>
      <p>
        🔍 Search for anime, manga and much more! 👤 View user profiles from
        AniList, MyAnimeList or Kitsu! 🔔 Receive anime episode notifications!
      </p>
      <div class="button-wrapper"><InviteButton /></div>
      <div class="button-wrapper"><SupportButton /></div>
    </div>
    <div class="waves">
      <svg viewBox="0 0 1440 400" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M 0,400 C 0,400 0,200 0,200 C 74.97607655502392,213.83732057416267 149.95215311004785,227.67464114832538 246,215 C 342.04784688995215,202.32535885167462 459.16746411483257,163.13875598086125 569,171 C 678.8325358851674,178.86124401913875 781.3779904306218,233.77033492822966 871,230 C 960.6220095693782,226.22966507177034 1037.3205741626796,163.7799043062201 1130,149 C 1222.6794258373204,134.2200956937799 1331.33971291866,167.11004784688996 1440,200 C 1440,200 1440,400 1440,400 Z"
          stroke="none"
          stroke-width="0"
          fill="#4169e1ff"
        ></path>
      </svg>
      <div class="stats">
        <div v-for="stat in stats" :key="stat" class="box-wrapper">
          <StatsBox :name="stat.name" :value="stat.value" />
        </div>
      </div>
      <svg viewBox="0 0 1440 400" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M 0,400 C 0,400 0,200 0,200 C 134.75,204.46428571428572 269.5,208.92857142857142 374,230 C 478.5,251.07142857142858 552.7499999999999,288.75 674,266 C 795.2500000000001,243.25 963.5,160.07142857142856 1099,139 C 1234.5,117.92857142857143 1337.25,158.96428571428572 1440,200 C 1440,200 1440,400 1440,400 Z"
          stroke="none"
          stroke-width="0"
          fill="#4169e1ff"
          transform="rotate(-180 720 200)"
        ></path>
      </svg>
    </div>
    <div class="features">
      <div v-for="(feature, index) in features" :key="feature" class="feature">
        <div v-if="index % 2 === 0" class="row">
          <div class="image">
            <img :src="feature.image" />
          </div>
          <div class="text">
            <h1>
              {{ feature.text }}
            </h1>
          </div>
        </div>
        <div v-else class="row">
          <div class="text">
            <h1>
              {{ feature.text }}
            </h1>
          </div>
          <div class="image">
            <img :src="feature.image" />
          </div>
        </div>
      </div>
    </div>
    <div class="checkout">
      <div class="column">
        <div class="text">
          <h1>Check out all commands!</h1>
          <div class="button">
            <CommandsButton />
          </div>
        </div>
        <div class="image">
          <img src="@/assets/zero-two.png" />
        </div>
      </div>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import InviteButton from '@/components/InviteButton.vue'
import SupportButton from '@/components/SupportButton.vue'
import StatsBox from '@/components/StatsBox.vue'
import CommandsButton from '@/components/CommandsButton.vue'

export default defineComponent({
  name: 'HomeView',
  components: {
    InviteButton,
    SupportButton,
    StatsBox,
    CommandsButton,
  },
  data() {
    return {
      stats: [
        {
          name: 'Servers',
          value: '2.5K+',
        },
        {
          name: 'Users',
          value: '500K+',
        },
        {
          name: 'Commands',
          value: '35+',
        },
      ],
      features: [
        {
          text: '🔍 Search for your favorite anime and manga!',
          image: require('@/assets/example-one.png'),
        },
        {
          text: '🎥 Look up characters, staff and studios!',
          image: require('@/assets/example-two.png'),
        },
        {
          text: '👤 View user profiles with anime and manga stats from AniList, MyAnimeList or Kitsu!',
          image: require('@/assets/example-three.png'),
        },
        {
          text: '🔔 Receive a notification when a new anime episode airs in Japan!',
          image: require('@/assets/example-four.png'),
        },
        {
          text: '🖼️ Search for the anime or the source of an image!',
          image: require('@/assets/example-five.png'),
        },
        {
          text: '🎬 View the opening and ending themes of an anime!',
          image: require('@/assets/example-six.png'),
        },
      ],
    }
  },
})
</script>

<style scoped lang="scss">
.home {
  text-align: center;
  background-color: $primary-background-color;
  padding: 7.5rem 0 3rem 0;

  img {
    width: 17.5rem;
    border-radius: 50%;
  }

  h1 {
    color: $primary-text-color;
    font-size: 3rem;
    margin: 0.5rem 1rem;
  }

  p {
    color: $secondary-text-color;
    font-size: 1.5rem;
    margin: 0.5rem 25%;
  }

  .button-wrapper {
    margin: 2rem 0;
  }
}

.waves {
  font-size: 0;
}

.stats {
  text-align: center;

  background-color: $brand-color;
  padding: 1.5rem 0;

  .box-wrapper {
    display: inline-flex;
    flex-wrap: wrap;
    margin: 1rem 5rem;

    @media screen and (max-width: 450px) {
      margin: 1rem 2rem;
    }
  }
}

.features {
  margin: 0 0 5rem 0;
  background-color: $primary-background-color;

  .feature {
    display: flex;
    justify-content: center;
    align-items: center;

    .row {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      margin: 1rem;
      width: 100%;

      .image {
        width: 700px;

        img {
          width: 100%;
        }

        @media screen and (max-width: 850px) {
          width: 500px;
        }

        @media screen and (max-width: 550px) {
          width: 300px;
        }
      }

      .text {
        text-align: center;
        color: $primary-text-color;
        width: 700px;
        font-size: 1.5rem;
        padding: 1rem;

        @media screen and (max-width: 850px) {
          width: 500px;
        }

        @media screen and (max-width: 550px) {
          width: 300px;
        }
      }
    }
  }

  .feature + .feature {
    margin-top: 5rem;
  }
}

.checkout {
  margin: 0 0 7rem 0;
  background-color: $tertiary-background-color;

  .column {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    width: 100%;

    .image {
      text-align: center;
      width: 700px;
      font-size: 0;

      img {
        width: 75%;
      }

      @media screen and (max-width: 850px) {
        width: 500px;
      }

      @media screen and (max-width: 550px) {
        width: 300px;
      }
    }

    .text {
      text-align: center;
      color: $primary-text-color;
      width: 700px;
      font-size: 2rem;

      .button {
        margin: 3rem 0;
      }

      @media screen and (max-width: 850px) {
        width: 500px;
        font-size: 1.75rem;
      }

      @media screen and (max-width: 550px) {
        width: 300px;
        font-size: 1.5rem;
      }
    }
  }
}
</style>
