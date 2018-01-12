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
