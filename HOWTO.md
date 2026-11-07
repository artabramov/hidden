# How-to guides

- [How to enable TLS for S3 and WebGUI](#how-to-enable-tls-for-s3-and-webgui)
- [How to mount cipherdir directly with gocryptfs](#how-to-mount-cipherdir-directly-with-gocryptfs)

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

## How to mount cipherdir directly with gocryptfs

Hidden S3 stores S3 objects as regular POSIX files and directories in an
encrypted `gocryptfs` filesystem, which can be mounted independently of
the application.

Retrieve the `gocryptfs` passphrase using `POST /api/v1/gocryptfs/reveal`
in the [management API](http://localhost:8081/docs).

Stop the container:

```sh
docker stop hidden
```

Locate the encrypted volume:

```sh
docker volume inspect hidden-cipherdir
```

Create a mountpoint and mount the filesystem using the volume's
`Mountpoint` path:

```sh
sudo mkdir -p /mnt/recovered
sudo gocryptfs /var/lib/docker/volumes/hidden-cipherdir/_data /mnt/recovered
```

Enter the retrieved passphrase when prompted. The decrypted files are
now accessible at `/mnt/recovered`.

Unmount when finished:

```sh
sudo fusermount3 -u /mnt/recovered
```
