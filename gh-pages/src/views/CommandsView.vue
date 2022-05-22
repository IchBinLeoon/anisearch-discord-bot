<template>
  <main>
    <div class="commands">
      <div class="headline">
        <h1>Commands</h1>
        <p>Command Prefix: <code>as! | @AniSearch | Customizable</code></p>
        <p>
          Parameters: <code>&lt;&gt;</code> - required, <code>[]</code> -
          optional, <code>|</code> - either/or
        </p>
        <p>
          Do not include <code>&lt;&gt;</code> , <code>[]</code> or
          <code>|</code> when executing the command.
        </p>
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
              usage: 'anime <title>',
              description:
                'Searches for an anime with the given title and displays information about the search results such as type, status, episodes, description, and more!',
            },
            {
              name: 'manga',
              usage: 'manga <title>',
              description:
                'Searches for a manga with the given title and displays information about the search results such as type, status, chapters, description, and more!',
            },
            {
              name: 'character',
              usage: 'character <name>',
              description:
                'Searches for a character with the given name and displays information about the search results such as description, synonyms, and appearances!',
            },
            {
              name: 'staff',
              usage: 'staff <name>',
              description:
                'Searches for a staff with the given name and displays information about the search results such as description, staff roles, and character roles!',
            },
            {
              name: 'studio',
              usage: 'studio <name>',
              description:
                'Searches for a studio with the given name and displays information about the search results such as the studio productions!',
            },
            {
              name: 'random',
              usage: 'random <anime|manga> <genre>',
              description:
                'Displays a random anime or manga of the specified genre.',
            },
          ],
        },
        {
          name: 'Profile',
          commands: [
            {
              name: 'anilist',
              usage: 'anilist [username|@member]',
              description:
                'Displays information about the given AniList profile such as anime stats, manga stats and favorites.',
            },
            {
              name: 'myanimelist',
              usage: 'myanimelist [username|@member]',
              description:
                'Displays information about the given MyAnimeList profile such as anime stats, manga stats and favorites.',
            },
            {
              name: 'kitsu',
              usage: 'kitsu [username|@member]',
              description:
                'Displays information about the given Kitsu profile such as anime stats, manga stats and favorites!',
            },
            {
              name: 'addprofile',
              usage: 'addprofile <al|mal|kitsu> <username>',
              description: 'Adds an AniList, MyAnimeList or Kitsu profile.',
            },
            {
              name: 'profiles',
              usage: 'profiles [@member]',
              description:
                'Displays the added profiles of you, or the specified user.',
            },
            {
              name: 'removeprofile',
              usage: 'removeprofile <al|mal|kitsu|all>',
              description:
                'Removes the added AniList, MyAnimeList or Kitsu profile.',
            },
          ],
        },
        {
          name: 'Notification',
          commands: [
            {
              name: 'watchlist',
              usage: 'watchlist',
              description:
                'Displays the anime watchlist of the server. If no anime has been added to the watchlist, the server will receive a notification for every new episode, provided the channel has been set.',
            },
            {
              name: 'watch',
              usage: 'watch <anilist-id>',
              description:
                'Adds an anime you want to receive episode notifications from to the server watchlist by AniList ID. Can only be used by a server administrator.',
            },
            {
              name: 'unwatch',
              usage: 'unwatch <anilist-id>',
              description:
                'Removes an anime from the server watchlist by AniList ID. Can only be used by a server administrator.',
            },
            {
              name: 'clearlist',
              usage: 'clearlist',
              description:
                'Removes all anime from the server watchlist. Can only be used by a server administrator.',
            },
            {
              name: 'set',
              usage: 'set <channel|role> <#channel|@role>',
              description:
                'Sets the channel for anime episode notifications, or the role for notification mentions. Can only be used by a server administrator.',
            },
            {
              name: 'remove',
              usage: 'remove <channel|role>',
              description:
                'Removes the set channel or role. Can only be used by a server administrator.',
            },
          ],
        },
        {
          name: 'Image',
          commands: [
            {
              name: 'trace',
              usage: 'trace <image-url|with image as attachment>',
              description:
                'Tries to find the anime the image is from through the image url or the image as attachment.',
            },
            {
              name: 'source',
              usage: 'source <image-url|with image as attachment>',
              description:
                'Tries to find the source of an image through the image url or the image as attachment.',
            },
            {
              name: 'waifu',
              usage: 'waifu',
              description: 'Posts a random image of a waifu.',
            },
            {
              name: 'neko',
              usage: 'neko',
              description: 'Posts a random image of a catgirl.',
            },
          ],
        },
        {
          name: 'Themes',
          commands: [
            {
              name: 'themes',
              usage: 'themes <anime>',
              description:
                'Searches for the openings and endings of the given anime and displays them.',
            },
            {
              name: 'theme',
              usage: 'theme <OP|ED> <anime>',
              description:
                'Displays a specific opening or ending of the given anime.',
            },
          ],
        },
        {
          name: 'News',
          commands: [
            {
              name: 'next',
              usage: 'next',
              description: 'Displays the next airing anime episodes.',
            },
            {
              name: 'last',
              usage: 'last',
              description: 'Displays the most recently aired anime episodes.',
            },
            {
              name: 'aninews',
              usage: 'aninews',
              description:
                'Displays the latest anime news from Anime News Network.',
            },
            {
              name: 'crunchynews',
              usage: 'crunchynews',
              description: 'Displays the latest anime news from Crunchyroll.',
            },
            {
              name: 'trending',
              usage: 'trending <anime|manga>',
              description:
                'Displays the current trending anime or manga on AniList.',
            },
          ],
        },
        {
          name: 'Help',
          commands: [
            {
              name: 'help',
              usage: 'help [command]',
              description:
                'Shows help or displays information about a command.',
            },
            {
              name: 'commands',
              usage: 'commands',
              description: 'Displays all commands.',
            },
            {
              name: 'about',
              usage: 'about',
              description: 'Displays information about the bot.',
            },
            {
              name: 'stats',
              usage: 'stats',
              description: 'Displays statistics about the bot.',
            },
            {
              name: 'github',
              usage: 'github',
              description: 'Displays information about the GitHub repository.',
            },
            {
              name: 'ping',
              usage: 'ping',
              description: 'Checks the latency of the bot.',
            },
          ],
        },
        {
          name: 'Settings',
          commands: [
            {
              name: 'setprefix',
              usage: 'setprefix <prefix>',
              description:
                'Changes the server prefix. Can only be used by a server administrator.',
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

  p {
    color: $primary-text-color;
    font-size: 1.3rem;
    margin: 1rem 5%;

    code {
      background-color: darken($primary-background-color, $amount: 10);
    }
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
