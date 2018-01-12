# plugins
VoTT-train plugins are simple command line tools that should respond to the following command line arguments:

```
myplugin/plugin.py --input-url=https://somehost/path/to/annotations.csv \
                   --output-model=https://somehost/path/to/container_or_bucket \
                   --output-status=https://somehost/path/to/status_endpoint
```

