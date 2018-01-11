# VoTT-train
VoTT training queue consumer

# Setup
Make sure the environment variables for the Azure Storage Queues dispatch implementation are present:

```
AZURE_STORAGE_CONNECTION_STRING=somevaluefromazureportal
```

* Other environment variables may be necessary if using a different implementation.

# Running
Starting the training daemon should be as simple as:

```
docker-compose up
```

or

```
nvidia-docker run --rm -it hashfromdockerbuild traind.py
```

