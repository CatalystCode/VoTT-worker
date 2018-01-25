# VoTT-train
VoTT training queue consumer

# Setup
Clone this repository. Then, download the required submodules:

```
git submodule init
git submodule update
```

Set environment variables needed for dispatching with either Azure Storage Queues or Azure Service Bus. (Creating a `.env` file containing these credentials is recommended.)

For Azure Storage Queues:

```
AZURE_STORAGE_ACCOUNT_NAME=accountnamefromazure
AZURE_STORAGE_KEY=storagekeyfromazure
```

For Azure Service Bus:

```
AZURE_SERVICE_BUS_NAMESPACE=somenamespace
AZURE_SERVICE_BUS_ACCESS_KEY_NAME=someaccesskeyname
AZURE_SERVICE_BUS_ACCESS_KEY_VALUE=someaccesskeyvalue
```

Other environment variables may be necessary if using a different implementation.

# Running
Starting the training daemon should be as simple as:

## For CPU-only =(

```
docker-compose up
```

## For GPU

```
docker build -f Dockerfile-gpu .
```

and

```
nvidia-docker run --rm -it \
  -e AZURE_STORAGE_ACCOUNT_NAME=$AZURE_STORAGE_ACCOUNT_NAME \
  -e AZURE_STORAGE_KEY=$AZURE_STORAGE_KEY \
  hashfromdockerbuild traind.py
```
where `hashfromdockerbuild` is the docker build hash from the previous step.

# Messaging
The `traind.py` daemon expects to see JSON messages like the following:

```
{
  "plugin_name":"retinanet",
  "annotations":"https://somehost/path/to/annotations.csv",
  "model":"https://somehost/path/to/container_or_bucket",
  "status":"https://somehost/path/to/status/callback"
}
```

## Annotations
The `annotations` property is meant to be a reference to the annotated images. It is, of course, up to the plugin to determine how this is formated, but a suggested implementation follows the following pattern:

```
https://somehost/path/to/file01.jpg,x1,y1,x2,x2,class01
https://somehost/path/to/file01.jpg,x1,y1,x2,x2,class02
https://somehost/path/to/file02.jpg,x1,y1,x2,x2,class01
https://somehost/path/to/file03.jpg,x1,y1,x2,x2,class02
```

## Model
The `model` property is meant to be a reference to an Azure Storage Container/Blob or AWS S3 Bucket/Object where the results of the training session are to be uploaded by the plugin. It is suggested that a single file is output by the plugin, *e.g.,* model.tgz.

## Status
The `status` property is meant to be a reference to an https endpoint that can receive the status of training results. The format of this data is up to the plugin to decide, but a suggested implementation would POST JSON payloads like the following. Progress should be present so the user can at least get an idea of how far along the training has gone.

```
{
    progress: 0.0, /* percentage represented by a value between 0.0 to 1.0 */
    epoch_current: 1, /* epoch number that the training is on */
    epoch_total: 100, /* total number of epochs to be run during training */
    step_current: 1, /* step/minibatch number that the training is on within the current epoch */
    steps_per_epoch: 1000, /* total number of steps/minibatches to be run within the current epoch */
    classification_loss: 0.25, /* Classification loss for the current epoch */
}
```

# Manual queueing for testing

If you need to test the response to incoming queue messages, you may create messages manually from the Azure Portal. The image below demonstrates how to queue a message from an Azure Storage resource.

![Dashboard Screenshot](https://user-images.githubusercontent.com/1117904/35071643-0ce9d354-fba7-11e7-9939-a075ef71431b.png)
