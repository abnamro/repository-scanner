import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import vue from '@vitejs/plugin-vue';
import Components from 'unplugin-vue-components/vite';
import { BootstrapVueNextResolver } from 'unplugin-vue-components/resolvers';
import postcssNesting from 'postcss-nesting';

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 8080,
    cors: false,
  },
  css: {
    postcss: {
      plugins: [postcssNesting],
    },
  },
  plugins: [
    vue(),
    Components({
      resolvers: [BootstrapVueNextResolver()],
    }),
    nodePolyfills({
      // To add only specific polyfills, add them here. If no option is passed, adds all polyfills
      include: ['buffer', 'crypto', 'stream', 'util'],
      // To exclude specific polyfills, add them to this list. Note: if include is provided, this has no effect
      exclude: [
        // 'http', // Excludes the polyfill for `http` and `node:http`.
      ],
      // Whether to polyfill specific globals.
      globals: {
        Buffer: true, // can also be 'build', 'dev', or false
        // global: true,
        // process: true,
      },
      // Override the default polyfills for specific modules.
      overrides: {
        // Since `fs` is not supported in browsers, we can use the `memfs` package to polyfill it.
        // fs: 'memfs',
      },
      // Whether to polyfill `node:` protocol imports.
      // protocolImports: true,
    }),
  ],
  define: {
    global: 'window',
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      crypto: 'crypto-browserify',
      stream: 'stream-browserify',
      util: '@browsery/util',
    },
  },
});
