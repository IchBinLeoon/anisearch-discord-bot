<template>
  <main>
    <div class="terms">
      <div class="text">
        <h1>Terms of Service</h1>
        <p>
          By inviting AniSearch Bot to your server and using its features, you
          agree to the following terms and rules of the bot.
        </p>
        <p>
          Any violation may result in your access to the bot being blocked and
          your data being removed.
        </p>
        <h2>Conditions</h2>
        <p>
          It is strictly prohibited to use AniSearch Bot for any illegal
          activities or those that violate Discord's
          <a href="https://discord.com/terms">Terms of Service</a>.
        </p>
        <p>
          Do not abuse, harm, disrupt or otherwise interfere with AniSearch Bot.
          This includes, but is not limited to, exploiting vulnerabilities
          and/or bugs as well as spamming the bot.
        </p>
        <p>
          AniSearch Bot may not be used by individuals under the minimum age
          described in Discord's
          <a href="https://discord.com/terms">Terms of Service</a>.
        </p>
        <h2>Availability</h2>
        <p>
          AniSearch Bot is provided "as is". There is no guarantee that the bot
          will be available in the future, and its purpose or availability may
          change at any time.
        </p>
        <h2>Affiliation</h2>
        <p>
          AniSearch Bot is not affiliated with, supported or made by
          <a href="https://discord.com/">Discord</a>.
        </p>
        <h2>Copyright</h2>
        <p>
          The source code of AniSearch Bot is freely available under the
          <a
            href="https://github.com/IchBinLeoon/anisearch-discord-bot/blob/main/LICENSE"
            >GNU General Public License v3.0</a
          >
          and may be copied or modified without imitating the bot.
        </p>
        <h2>Contact</h2>
        <p>
          You can get in contact through the
          <router-link to="/support">support server</router-link>.
        </p>
      </div>
      <div class="text">
        <h1>Privacy Policy</h1>
        <p>
          By inviting AniSearch Bot to your server and using its features, you
          agree to the following privacy policy of the bot.
        </p>
        <h2>Data Usage</h2>
        <p>
          AniSearch Bot may use stored data, as defined below, for different
          features including, but not limited to, linking
          <a href="https://anilist.co/">AniList</a>,
          <a href="https://myanimelist.net/">MyAnimeList</a> or
          <a href="https://kitsu.io/">Kitsu</a> profiles, automated anime
          episode notifications as well as command statistics.
        </p>
        <p>No data is sold, provided to or shared with third parties.</p>
        <h2>Data Collection</h2>
        <p>
          AniSearch Bot may automatically store the following data when invited
          to a new server:
        </p>
        <ul>
          <li><code>Guild ID</code></li>
          <li><code>Timestamp</code></li>
        </ul>
        <p>
          AniSearch Bot may automatically store the following data when any of
          its commands are used:
        </p>
        <ul>
          <li><code>Shard ID</code></li>
          <li><code>Guild ID</code></li>
          <li><code>Channel ID</code></li>
          <li><code>User ID</code></li>
          <li><code>Command Name</code></li>
          <li><code>Command Type</code></li>
          <li><code>Timestamp</code></li>
        </ul>
        <p>
          AniSearch Bot may store the following data voluntarily provided by the
          user when certain commands are used:
        </p>
        <ul>
          <li><code>Channel ID</code></li>
          <li><code>Role ID</code></li>
          <li><code>AniList ID</code></li>
          <li><code>MyAnimeList ID</code></li>
          <li><code>Kitsu ID</code></li>
        </ul>
        <h2>Data Storage</h2>
        <p>
          All data is stored in a PostgreSQL database, accessible only by
          AniSearch Bot and the maintainer of this application.
        </p>
        <p>
          The database is secured to prevent unauthorized access, but no
          warranty is provided and the bot maintainer is not liable for any
          unintentional or malicious breaches of data.
        </p>
        <h2>Data Removal</h2>
        <p>
          The removal of data can be requested on the
          <router-link to="/support">support server</router-link>.
        </p>
        <p>
          If you request the removal of data associated with a server, you must
          prove that you are the owner of the server. Only the server owner can
          request the removal of data, and such a request will result in
          AniSearch Bot being removed from the server.
        </p>
      </div>
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TermsView',
})
</script>

<style scoped lang="scss">
.terms {
  background-color: $primary-background-color;
  padding: 7.5rem 15%;

  .text + .text {
    margin: 5rem 0 0 0;
  }

  h1 {
    color: $primary-text-color;
    font-size: 3rem;
    margin: 0 0 0.5rem 0;
  }

  h2 {
    color: $primary-text-color;
    font-size: 2rem;
    margin: 2rem 0 0.5rem 0;
  }

  p,
  li {
    color: $primary-text-color;
    font-size: 1.5rem;
    margin: 0;
  }

  p + p {
    margin: 1rem 0;
  }

  li + li {
    margin: 0.5rem 0;
  }

  ul {
    margin: 1rem 0;
  }

  code {
    background-color: lighten($secondary-text-color, $amount: 50);
    padding: 0 0.5rem;
    border-radius: 5px;
  }
}
</style>
