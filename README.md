# VoTT-train
VoTT training queue consumer

# Setup
Make sure the environment variables are present for dispatching with either Azure Storage Queues:

```
AZURE_STORAGE_ACCOUNT_NAME=accountnamefromazure
AZURE_STORAGE_KEY=storagekeyfromazure
VOTT_TRAIN_PLUGIN=hello-world
```

or with Azure Service Bus:

```
AZURE_SERVICE_BUS_NAMESPACE=somenamespace
AZURE_SERVICE_BUS_ACCESS_KEY_NAME=someaccesskeyname
AZURE_SERVICE_BUS_ACCESS_KEY_VALUE=someaccesskeyvalue
VOTT_TRAIN_PLUGIN=hello-world
```

* Other environment variables may be necessary if using a different implementation.

# Running
Starting the training daemon should be as simple as:

```
nvidia-docker run --rm -it \
  -e AZURE_STORAGE_ACCOUNT_NAME=$AZURE_STORAGE_ACCOUNT_NAME \
  -e AZURE_STORAGE_KEY=$AZURE_STORAGE_KEY \
  -e VOTT_TRAIN_PLUGIN=$VOTT_TRAIN_PLUGIN \
  hashfromdockerbuild traind.py
```

# Messaging
The `traind.py` daemon expects to see JSON messages like the following:

```
{
  "annotations":"https://somehost/path/to/annotations.csv",
  "model":"https://somehost/path/to/container_or_bucket",
  "status":"https://somehost/path/to/status/callback"
}
```

# annotations
The `annotations` property is meant to be a reference to the annotated images. It is, of course, up to the plugin to determine how this is formated, but a suggested implementation follows the following pattern:

```
https://somehost/path/to/file01.jpg,x,y,width,height,class01
https://somehost/path/to/file01.jpg,x,y,width,height,class02
https://somehost/path/to/file02.jpg,x,y,width,height,class01
https://somehost/path/to/file03.jpg,x,y,width,height,class02
```

# model
The `model` property is meant to be a reference to an Azure Storage Container or AWS S3 bucket where the results of the training session are to be uploaded by the plugin.

# status
The `status` property is meant to be a reference to an https endpoint that can receive the status of training results. The format of this data is up to the plugin to decide, but a suggested implementation would POST JSON payloads like the following:

```
{
    progress: 0.0, /* percentage represented by a value between 0.0 to 1.0 */
    epoch_current: 1, /* epoch number that the training is on */
    epoch_total: 100, /* total number of epochs to be run during training */
    step_current: 1, /* step/minibatch number that the training is on within the current epoch */
    step_total: 1000, /* total number of steps/minibatches to be run within the current epoch */
    classification_loss: 0.25, /* Classification loss for the current epoch */
}
```
