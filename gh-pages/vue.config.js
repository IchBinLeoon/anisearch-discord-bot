const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  productionSourceMap: false,

  css: {
    loaderOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`,
      },
    },
  },

  publicPath:
    process.env.NODE_ENV === 'production' ? '/anisearch-discord-bot/' : '/',
})
