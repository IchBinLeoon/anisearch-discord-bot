<template>
  <main>
    <div class="team">
      <div class="headline">
        <h1>Team</h1>
      </div>
      <div v-for="group in groups" :key="group" class="group">
        <div class="name">
          <h1>{{ group.name }}</h1>
        </div>
        <div class="cards">
          <div
            v-for="member in group.members"
            :key="member"
            class="card-wrapper"
          >
            <TeamCard :image="member.image" :socials="member.socials">{{
              member.name
            }}</TeamCard>
          </div>
        </div>
        <div v-if="group.name === 'Contributor'" class="github">
          <h1>Want to become a contributor?</h1>
          <GitHubButton />
        </div>
      </div>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import TeamCard from '@/components/TeamCard.vue'
import GitHubButton from '@/components/GitHubButton.vue'

export default defineComponent({
  name: 'TeamView',
  components: {
    TeamCard,
    GitHubButton,
  },
  data() {
    return {
      groups: [
        {
          name: 'Owner & Lead Developer',
          members: [
            {
              name: 'IchBinLeoon',
              image: require('@/assets/ichbinleoon.gif'),
              socials: [
                {
                  image: require('@/assets/github.png'),
                  link: 'https://github.com/IchBinLeoon',
                },
                {
                  image: require('@/assets/discord.png'),
                  link: 'https://discordapp.com/users/223871059068321793',
                },
                {
                  image: require('@/assets/twitter.png'),
                  link: 'https://twitter.com/IchBinLeoon',
                },
                {
                  image: require('@/assets/myanimelist.png'),
                  link: 'https://myanimelist.net/profile/IchBinLeoon',
                },
              ],
            },
          ],
        },
        {
          name: 'Contributor',
          members: [
            {
              name: 'ByteDream',
              image: require('@/assets/bytedream.jpg'),
              socials: [
                {
                  image: require('@/assets/github.png'),
                  link: 'https://github.com/ByteDream',
                },
              ],
            },
          ],
        },
      ],
    }
  },
})
</script>

<style scoped lang="scss">
.team {
  background-color: $primary-background-color;
  padding: 5rem 0;
}

.headline {
  text-align: center;

  h1 {
    color: $primary-text-color;
    font-size: 3rem;
  }
}

.group {
  .name {
    text-align: center;

    h1 {
      color: $primary-text-color;
      font-size: 2rem;
      margin: 1rem 1rem;
    }
  }

  .cards {
    text-align: center;
    padding: 1rem 0;

    .card-wrapper {
      display: inline-flex;
      flex-wrap: wrap;
      margin: 1rem 3rem;
    }
  }
}

.group + .group {
  margin-top: 5rem;
}

.github {
  text-align: center;
  padding: 1rem;

  h1 {
    color: $primary-text-color;
    font-size: 1.5rem;
  }
}
</style>
