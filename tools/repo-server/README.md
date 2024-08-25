# Create a memories repo server

```console
$ docker run --rm -v $(pwd)/memorybox_repo:/usr/share/nginx/html:ro -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro -p 8080:8080 nginx
```

```console
$ tar -cf memorybox_repo/$(uuid).tar path_to_picture...
```