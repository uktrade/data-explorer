const path = require("path")
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const glob = require("glob");
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  context: __dirname,
  entry: {
    index: './explorer/static/js/index', // entry point of our app. static/js/index.js should require other js modules and dependencies it needs
    query: './explorer/static/js/query',
    schema: './explorer/static/js/schema',
    defaultVueApp: './explorer/static/js/vue/apps/default-app',
  },
  output: {
      path: path.resolve(__dirname, 'assets/bundles'),
      filename: "[name]-[hash].js",
  },
  module: {
    rules: [
      { test: /\.vue$/, loader: 'vue-loader'},
      { test: /\.js?$/, exclude: /node_modules/, loader: 'babel-loader'},
      { test: /\.css$/, use: ['vue-style-loader', 'css-loader']},
    ],
  },
  plugins: [
    new BundleTracker({filename: './explorer/webpack-stats.json'}),
    new VueLoaderPlugin(),
    new CopyPlugin({
        patterns: [
            { from: path.resolve(__dirname, './node_modules/govuk-frontend/govuk/all.js'), to: path.resolve(__dirname, './assets/js/') }
        ]
    }),
    new webpack.ProvidePlugin({
       $: "jquery",
       jQuery: "jquery"
   })
  ],
  resolve: {
    modules: ['node_modules', 'bower_components'],
    extensions: ['.js'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    }
  },
}
