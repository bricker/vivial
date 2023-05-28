As of May 2023, the default `forge tunnel` does not support local NPM dependencies outside of the project directory, not even with symlinks, because of the following:

1. `forge tunnel` starts a Docker container and copies only the files from this directory into the container, which excludes the shared local packages.
2. Docker doesn't follow symlinks on copy.

Because of that, we're using a modified setup in which the forge tunnel runs on the "host" machine (i.e., your workspace) instead of a Docker container.

Running the Forge app inside of a Docker container for development will not work out of the box. If you need to develop that way, you can use Yalc to copy the local dependencies into this directory before starting the tunnel.