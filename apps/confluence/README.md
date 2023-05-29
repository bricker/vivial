## Forge Tunnel complications

As of May 2023, the default `forge tunnel` does not support local NPM dependencies outside of the project directory, not even with symlinks, because of the following:

1. `forge tunnel` starts a Docker container and copies only the files from this directory into the container, which excludes the shared local packages.
2. Docker doesn't follow symlinks on copy.

Because of that, we're using a modified setup in which the forge tunnel runs on the "host" machine (i.e., your workspace) instead of a Docker container. See `bin/setup` for more details.

Running the Forge app inside of a Docker container for development will not work out of the box. If you need to develop that way, you can use Yalc to copy the local dependencies into this directory before starting the tunnel.

### Forge bundler

Currently the bundling step fails because of the `.js` extensions in the import specifiers, which aren't supported by Forge's Webpack configuration. This is a Webpack (ts-loader) problem, not a Forge problem. The solution to this is to use the `resolve.extensionAlias` configuration in the webpack config. However, the webpack configuration for the Forge bundler is built-in to the @forge/bundler package. So to make the bundle step work, you need to do a hack. I'm not bothering to automate this because it's very temporary.

Update this file: `(path/to/node/install)/lib/node_modules/@forge/sandbox-tunnel/node_modules/@forge/bundler/out/config/common.js`. On my machine, for example, the full path is `$HOME/.local/share/nvm/v18.16.0/lib/node_modules/@forge/sandbox-tunnel/node_modules/@forge/bundler/out/config/common.js`

Add the following into the `resolve` property (next to `extensions`):

```js
extensionAlias: {
    '.js': ['.js', '.ts'],
},
```

While you're in there, add the following into the `output` property:

```js
publicPath: '',
```

This fixes some error talking about `auto publicPath not supported in this browser`, idk, just do it.