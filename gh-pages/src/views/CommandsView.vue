<template>
  <main>
    <div class="commands">
      <div class="headline">
        <h1>Commands</h1>
        <div class="search">
          <div class="bar-wrapper">
            <CommandsSearchBar :items="getSearchBarItems()" />
          </div>
        </div>
      </div>
      <div v-for="category in categories" :key="category" class="table-wrapper">
        <h1>{{ category.name }}</h1>
        <CommandsTable :commands="category.commands" />
      </div>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import CommandsSearchBar from '@/components/CommandsSearchBar.vue'
import CommandsTable from '@/components/CommandsTable.vue'

export default defineComponent({
  name: 'CommandsView',
  components: {
    CommandsSearchBar,
    CommandsTable,
  },
  data() {
    return {
      categories: [
        {
          name: 'Search',
          commands: [
            {
              name: 'anime',
              usage: '/anime',
              description:
                'Searches for an anime with the given title and displays information about the search results',
            },
            {
              name: 'manga',
              usage: '/manga',
              description:
                'Searches for a manga with the given title and displays information about the search results',
            },
            {
              name: 'character',
              usage: '/character',
              description:
                'Searches for a character with the given name and displays information about the search results',
            },
            {
              name: 'staff',
              usage: '/staff',
              description:
                'Searches for a staff with the given name and displays information about the search results',
            },
            {
              name: 'studio',
              usage: '/studio',
              description:
                'Searches for a studio with the given name and displays information about the search results',
            },
            {
              name: 'random',
              usage: '/random',
              description: 'Displays a random anime or manga',
            },
            {
              name: 'trending',
              usage: '/trending',
              description: 'Displays the current trending anime or manga',
            },
            {
              name: 'seasonal',
              usage: '/seasonal',
              description: 'Displays the currently airing anime',
            },
          ],
        },
        {
          name: 'Profile',
          commands: [
            {
              name: 'anilist',
              usage: '/anilist',
              description:
                'Displays information about the given AniList profile such as stats and favorites',
            },
            {
              name: 'myanimelist',
              usage: '/myanimelist',
              description:
                'Displays information about the given MyAnimeList profile such as stats and favorites',
            },
            {
              name: 'kitsu',
              usage: '/kitsu',
              description:
                'Displays information about the given Kitsu profile such as stats and favorites',
            },
            {
              name: 'profile add',
              usage: '/profile add',
              description:
                'Adds an AniList, MyAnimeList or Kitsu profile to your account',
            },
            {
              name: 'profile remove',
              usage: '/profile remove',
              description:
                'Removes an added AniList, MyAnimeList or Kitsu profile from your account',
            },
            {
              name: '/profile info',
              usage: '/profile info',
              description:
                'Displays the added profiles of you or a server member',
            },
          ],
        },
        {
          name: 'Notification',
          commands: [
            {
              name: 'notification add',
              usage: '/notification add',
              description: 'Adds an anime to your server notification list',
            },
            {
              name: 'notification remove',
              usage: '/notification remove ',
              description:
                'Removes an anime from your server notification list',
            },
            {
              name: 'notification list',
              usage: '/notification list',
              description: 'Displays your server notification list',
            },
            {
              name: 'notification clear',
              usage: '/notification clear',
              description:
                'Removes all anime from your server notification list',
            },
            {
              name: 'notification setchannel',
              usage: '/notification setchannel',
              description: 'Sets the channel for episode notifications',
            },
            {
              name: 'notification removechannel',
              usage: '/notification removechannel',
              description: 'Removes the set channel',
            },
            {
              name: 'notification setrole',
              usage: '/notification setrole',
              description: 'Sets the role for episode notification pings',
            },
            {
              name: 'notification removerole',
              usage: '/notification removerole',
              description: 'Removes the set role',
            },
          ],
        },
        {
          name: 'Image',
          commands: [
            {
              name: 'trace',
              usage: '/trace',
              description:
                'Tries to find the anime the image is from through the image url or the image as attachment',
            },
            {
              name: 'source',
              usage: '/source',
              description:
                'Tries to find the source of an image through the image url or the image as attachment',
            },
            {
              name: 'waifu',
              usage: '/waifu',
              description: 'Posts a random image of a waifu',
            },
            {
              name: 'neko',
              usage: '/neko',
              description: 'Posts a random image of a catgirl',
            },
          ],
        },
        {
          name: 'Themes',
          commands: [
            {
              name: 'themes',
              usage: '/themes',
              description:
                'Searches for the opening and ending themes of an anime',
            },
            {
              name: 'theme',
              usage: '/theme',
              description: 'Displays a specific anime opening or ending theme',
            },
          ],
        },
        {
          name: 'News',
          commands: [
            {
              name: 'aninews',
              usage: '/aninews',
              description:
                'Displays the latest anime news from Anime News Network',
            },
            {
              name: 'crunchynews',
              usage: '/crunchynews',
              description: 'Displays the latest anime news from Crunchyroll',
            },
          ],
        },
        {
          name: 'Utility',
          commands: [
            {
              name: 'avatar',
              usage: '/avatar',
              description: 'Displays the avatar of a server member',
            },
            {
              name: 'userinfo',
              usage: '/userinfo',
              description: 'Displays information about a server member',
            },
            {
              name: 'serverinfo',
              usage: '/serverinfo',
              description: 'Displays information about the current server',
            },
          ],
        },
        {
          name: 'Help',
          commands: [
            {
              name: 'help',
              usage: '/help',
              description: 'Browse all commands of the bot',
            },
            {
              name: 'stats',
              usage: '/stats',
              description: 'Displays information and statistics about the bot',
            },
            {
              name: 'github',
              usage: '/github',
              description: 'Displays information about the GitHub repository',
            },
            {
              name: 'ping',
              usage: '/ping',
              description: 'Checks the latency of the bot',
            },
            {
              name: 'invite',
              usage: '/invite',
              description: 'Invite the bot to your server',
            },
            {
              name: 'support',
              usage: '/support',
              description: 'Join the bot support server',
            },
          ],
        },
      ],
    }
  },
  methods: {
    getSearchBarItems(): string[] {
      let items = []
      for (let category of this.categories) {
        for (let command of category.commands) {
          items.push(command.name)
        }
      }
      return items.sort()
    },
  },
})
</script>

<style scoped lang="scss">
.commands {
  background-color: $primary-background-color;
  padding: 5rem 0 0 0;
}

.headline {
  text-align: center;

  h1 {
    color: $primary-text-color;
    font-size: 3rem;
  }

  .search {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem 5%;
  }
}

.bar-wrapper {
  width: 700px;
}

.table-wrapper {
  margin: 7.5rem 12.5%;

  h1 {
    color: $primary-text-color;
    font-size: 2rem;
    margin: 0.5rem 0;
  }
}
</style>
