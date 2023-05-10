As of May 2023, `forge tunnel` does not support local NPM dependencies outside of the project directory, not even with symlinks, because of the following:

1. `forge tunnel` starts a Docker container and copies only the files from this directory into the container, which excludes the shared local packages.
2. Docker doesn't follow symlinks on copy.

So, we're using this project called [yalc](https://github.com/wclr/yalc) to hard copy the local packages into this directory. This is _not_ a long-term solution and is only necessary due to the Docker issue described above. Although the `yalc` project is convenient to work around this issue, we should stop using it as soon as we reasonably can.

Because of this setup, changes to the local dependencies won't automatically propagate to this app. See the `yalc` documentation for more information, but usually after you make a change to a local package, run `yalc publish --push` to update the apps using that package.