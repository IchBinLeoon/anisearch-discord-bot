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
              description:
                'Displays a random anime or manga of the specified genre',
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
              name: 'addprofile',
              usage: '/addprofile',
              description: 'Adds an AniList, MyAnimeList or Kitsu profile',
            },
            {
              name: 'removeprofile',
              usage: '/removeprofile',
              description:
                'Removes the added AniList, MyAnimeList or Kitsu profile',
            },
            {
              name: 'profiles',
              usage: '/profiles',
              description:
                'Displays the added profiles of you, or the specified user',
            },
          ],
        },
        {
          name: 'Notification',
          commands: [
            {
              name: 'watchlist',
              usage: '/watchlist',
              description: 'Displays the anime watchlist of the server',
            },
            {
              name: 'watch',
              usage: '/watch ',
              description:
                'Adds an anime you want to receive episode notifications from to the server watchlist by AniList ID',
            },
            {
              name: 'unwatch',
              usage: '/unwatch',
              description:
                'Removes an anime from the server watchlist by AniList ID',
            },
            {
              name: 'clearlist',
              usage: '/clearlist',
              description: 'Removes all anime from the server watchlist',
            },
            {
              name: 'set channel',
              usage: '/set channel',
              description: 'Sets the channel for anime episode notifications',
            },
            {
              name: 'set role',
              usage: '/set role',
              description: 'Sets the role for notification mentions',
            },
            {
              name: 'remove channel',
              usage: '/remove channel',
              description: 'Removes the set channel',
            },
            {
              name: 'remove role',
              usage: '/remove role',
              description: 'Removes the set role',
            },
          ],
        },
        {
          name: 'Image',
          commands: [
            {
              name: 'trace url',
              usage: '/trace url',
              description:
                'Tries to find the anime the image is from through the image url',
            },
            {
              name: 'trace attachment',
              usage: '/trace attachment',
              description:
                'Tries to find the anime the image is from through the image as attachment',
            },
            {
              name: 'source url',
              usage: '/source url',
              description:
                'Tries to find the source of an image through the image url',
            },
            {
              name: 'source attachment',
              usage: '/source attachment',
              description:
                'Tries to find the source of an image through the image as attachment',
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
                'Searches for the openings and endings of the given anime and displays them',
            },
            {
              name: 'theme',
              usage: '/theme',
              description:
                'Displays a specific opening or ending of the given anime',
            },
          ],
        },
        {
          name: 'News',
          commands: [
            {
              name: 'next',
              usage: '/next',
              description: 'Displays the next airing anime episodes',
            },
            {
              name: 'last',
              usage: '/last',
              description: 'Displays the most recently aired anime episodes',
            },
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
            {
              name: 'trending',
              usage: '/trending',
              description:
                'Displays the current trending anime or manga on AniList',
            },
          ],
        },
        {
          name: 'Help',
          commands: [
            {
              name: 'help',
              usage: '/help',
              description: 'Shows help or displays information about a command',
            },
            {
              name: 'commands',
              usage: '/commands',
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
      return items
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
