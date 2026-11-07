# How-to guides

- [How to enable TLS for S3 and WebGUI](#how-to-enable-tls-for-s3-and-webgui)

## How to enable TLS for S3 and WebGUI

To enable TLS for both the S3 API and WebGUI, place a PEM certificate
and private key in the project before running `make install`:

```sh
cp /path/to/fullchain.pem ./cert.pem
cp /path/to/private-key.pem ./key.pem
```

Configure their paths and the WebGUI URLs in `.env` (leave `localhost`
when opening the WebGUI at `https://localhost:8080`; otherwise use the
certificate hostname in both URLs and open the WebGUI at that hostname):

```dotenv
VGW_CERT=/opt/hidden/cert.pem
VGW_KEY=/opt/hidden/key.pem
VERSITY_WEBGUI_GATEWAY=https://localhost:9000
VERSITY_WEBGUI_CORS_ALLOW_ORIGIN=https://localhost:8080
```

Then build and run the container:

```sh
make install
```

Because the private key is copied into the Docker image, keep the image
and build context private. For shared images, terminate TLS externally
or mount the certificate and key at runtime instead.
