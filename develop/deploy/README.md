This directory contains Dockerfiles for custom images to be used in Cloud Build.

To push an image to Artifact Registry, run `bin/gcloud-build IMAGE_NAME`, where `IMAGE_NAME` is the name of the directory containing the Dockerfile (which is also the name of the image that will be pushed).

The image will be pushed to the Artifact Registry for your currently active project in the gcloud CLI.

```sh
bin/push eave-builder-gcloudsdk
```
