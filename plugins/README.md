# plugins
VoTT-train plugins are simple command line tools that should respond to the following command line arguments:

```
myplugin/plugin.py --annotations=https://somehost/path/to/annotations.csv \
                   --model=https://somehost/path/to/container_or_bucket \
                   --status=https://somehost/path/to/status_endpoint
```

# annotations
The `annotations` argument will point to a csv file that follows the following pattern:

```
https://somehost/path/to/file01.jpg,x,y,width,height,class01
https://somehost/path/to/file01.jpg,x,y,width,height,class02
https://somehost/path/to/file02.jpg,x,y,width,height,class01
https://somehost/path/to/file03.jpg,x,y,width,height,class02
```

# model
The `model` argument will reference an Azure Blob Container or AWS S3 bucket where the output of the plugin is to be uploaded. This may include *.h5 or *.model files as well as any other files that are needed during prediction.

# status
The `status` argument will reference a callback URL that takes the following POST JSON (application/json) payload:

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
