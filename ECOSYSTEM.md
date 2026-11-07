# Hidden S3 ecosystem

A curated list of open-source projects that support S3-compatible object
storage. Not all projects listed here have been tested with Hidden S3.
Compatibility may depend on configuration and supported S3 API features.

Projects released under OSI-approved open-source licenses are preferred,
but projects with proprietary or commercial licenses are also welcome.

Contributions to this list are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Table of contents

- [Backup, recovery & synchronization](#backup-recovery--synchronization) `22`
- [Storage clients & tools](#storage-clients--tools) `21`
- [Security & testing](#security--testing) `5`
- [Proxies & gateways](#proxies--gateways) `6`
- [Development & integrations](#development--integrations) `23`
- [Automation & deployment](#automation--deployment) `6`
- [Data processing & monitoring](#data-processing--monitoring) `5`
- [Other projects](#other-projects) `1`

## Backup, recovery & synchronization

Backup, data recovery, archiving, and file synchronization.

| Project | Description |
|---------|-------------|
| [marckohlbrugge/rclown](https://github.com/marckohlbrugge/rclown) `O'Saasy` | Friendly web UI for backing up your object storage buckets |
| [istepanov/docker-backup-to-s3](https://github.com/istepanov/docker-backup-to-s3) `MIT` | Docker container that periodically backups files to Amazon S3 using s3cmd and cron |
| [pothi/backup-wordpress](https://github.com/pothi/backup-wordpress) `MIT` | Shell scripts to take remote backups of WordPress to S3 compatible cloud storages via server cron |
| [nidor1998/s3sync](https://github.com/nidor1998/s3sync) `Apache-2.0` | A reliable, flexible, and fast synchronization tool for S3 |
| [PhantomPhoton/S3-Compatible](https://github.com/PhantomPhoton/S3-Compatible) `Apache-2.0` | A custom component to enable using S3 compatible endpoints for home assistant backups |
| [peter-evans/s3-backup](https://github.com/peter-evans/s3-backup) `MIT` | A GitHub action to mirror a repository to S3 compatible object storage |
| [petergtz/g2s3](https://github.com/petergtz/g2s3) `MIT` | G2S3 is a solution to regularly back up your Google data by copying it over to S3 |
| [famzah/encrypted-s3-backup](https://github.com/famzah/encrypted-s3-backup) `MIT` | Back up your data securely to AWS S3 |
| [tomcz/s3backup](https://github.com/tomcz/s3backup) `MIT` | No more custom backup scripts please |
| [futurevision/docker-aws-s3-sync](https://github.com/futurevision/docker-aws-s3-sync) `MIT` | Docker container to sync a folder to Amazon S3 |
| [databasus/databasus](https://github.com/databasus/databasus) `Apache-2.0` | PostgreSQL backup tool with point-in-time-recovery and restore verification |
| [eduardolat/pgbackweb](https://github.com/eduardolat/pgbackweb) `AGPL-3.0` | Effortless PostgreSQL backups with a user-friendly web interface |
| [eeshugerman/postgres-backup-s3](https://github.com/eeshugerman/postgres-backup-s3) `MIT` | A handy Docker container to periodically backup PostgreSQL to S3 |
| [maxisam/mgob](https://github.com/maxisam/mgob) `MIT` | MongoDB dockerized backup agent; runs schedule backups with retention, S3 & SFTP upload, notifications |
| [ishanjain28/s3-mongo-backup](https://github.com/ishanjain28/s3-mongo-backup) `MIT` | Mongodb backups to S3 |
| [seanvm/s3-sync-tool](https://github.com/seanvm/s3-sync-tool) | Electron app for syncing AWS s3 buckets |
| [willdady/go-watch-s3](https://github.com/willdady/go-watch-s3) | A program which will recursively watch a directory for new files and upload them to S3 |
| [xtream1101/s3-tar](https://github.com/xtream1101/s3-tar) `MIT` | Stream s3 data into a tar file in s3 |
| [oguzhan-yilmaz/argocd-backup-s3](https://github.com/oguzhan-yilmaz/argocd-backup-s3) `Apache-2.0` | Kubernetes CronJob to backup ArgoCD with "argocd admin export" cmd and upload to S3 compatible storage |
| [timothystewart6/mongo-to-s3](https://github.com/timothystewart6/mongo-to-s3) | Backup mongodb databases to an s3 bucket |
| [oliverfarrell/ubuntu-amazon-s3-backup](https://github.com/oliverfarrell/ubuntu-amazon-s3-backup) | A process for backing up folders and databases on a Ubuntu server |
| [javierarce/icloud-to-s3](https://github.com/javierarce/icloud-to-s3) `GPL-3.0` | Move photos from a shared iCloud album to an S3 bucket |

[↑ Back to top](#table-of-contents)

## Storage clients & tools

S3 browsers, command-line tools, file management, object transfers, and bucket administration.

| Project | Description |
|---------|-------------|
| [mickael-kerjean/filestash](https://github.com/mickael-kerjean/filestash) `AGPL-3.0` | Universal file management platform (for humans and agents) |
| [lusingander/stu](https://github.com/lusingander/stu) `MIT` | TUI explorer application for Amazon S3 |
| [mishudark/s3-parallel-put](https://github.com/mishudark/s3-parallel-put) `MIT` | Parallel uploads to Amazon AWS S3 |
| [koblas/s3-cli](https://github.com/koblas/s3-cli) `MIT` | Go version of s3cmd |
| [tsub/s3-edit](https://github.com/tsub/s3-edit) `MIT` | Edit directly a file on Amazon S3 in CLI |
| [lmammino/s3st](https://github.com/lmammino/s3st) `MIT` | A command line utility that allows you to stream data from multiple S3 objects directly into your terminal |
| [shvc/s3cli](https://github.com/shvc/s3cli) `MIT` | Command line tool for S3 |
| [ashwathstephen/sairo](https://github.com/ashwathstephen/sairo) `Apache-2.0` | Self-hosted S3 storage browser with cost intelligence, optimization recommendations, and AI-powered analytics. Works with AWS, MinIO, R2, Wasabi, and any S3-compatible endpoint |
| [indece-official/s3-explorer](https://github.com/indece-official/s3-explorer) `GPL-3.0` | Lightweight GUI/Desktop S3-Explorer for Windows and Linux |
| [sethkor/s3kor](https://github.com/sethkor/s3kor) `GPL-3.0` | Fast S3 Tools built in GoLang Using Multiparts and Concurrency |
| [boyter/aws-s3-bucket-purger](https://github.com/boyter/aws-s3-bucket-purger) `MIT` | A program that will purge any AWS S3 Bucket of objects and versions quickly |
| [joegiralt/ex-s3-edit](https://github.com/joegiralt/ex-s3-edit) `MIT` | Edit files directly on Amazon S3 in CLI |
| [jdevelop/s3kit](https://github.com/jdevelop/s3kit) `MIT` | AWS S3 CLI tooklit |
| [jamesmcm/s3rename](https://github.com/jamesmcm/s3rename) `Apache-2.0` `MIT` | Tool to mass-rename S3 keys |
| [killcod3/temps3](https://github.com/killcod3/temps3) `MIT` | A secure CLI application for temporary file storage using AWS S3 with automatic expiration, intelligent chunking, and local history tracking. |
| [romanzdk/s3-commander](https://github.com/romanzdk/s3-commander) `MIT` | S3 Commander – Total Commander-style dual-pane S3 browser with server-side move/copy |
| [mhausenblas/s3-echoer](https://github.com/mhausenblas/s3-echoer) `Apache-2.0` | Reads input from stdin and uploads it to an existing S3 bucket |
| [paololazzari/s3-fuzzy-viewer](https://github.com/paololazzari/s3-fuzzy-viewer) `Apache-2.0` | tmux based cli tool for searching s3 objects using fuzzy search |
| [juntaki/bucketsync](https://github.com/juntaki/bucketsync) `MIT` | S3 backed FUSE Filesystem written in Go with dedup and encryption |
| [half-6/cloud-storage-client](https://github.com/half-6/cloud-storage-client) `MIT` | Cloud Storage Desktop Application |
| [marmos91/cubbit-ds3-drive](https://github.com/marmos91/cubbit-ds3-drive) `GPL-3.0` | Cubbit DS3 Drive - macOS File Provider client for S3-compatible storage |

[↑ Back to top](#table-of-contents)

## Security & testing

Security auditing, bucket permissions, vulnerability scanning, and S3 compatibility testing.

| Project | Description |
|---------|-------------|
| [jordanpotti/AWSBucketDump](https://github.com/jordanpotti/AWSBucketDump) `MIT` | Security tool to look for interesting files in S3 buckets |
| [sa7mon/S3Scanner](https://github.com/sa7mon/S3Scanner) `MIT` | Scan for misconfigured S3 buckets across S3-compatible APIs |
| [pbnj/s3-fuzzer](https://github.com/pbnj/s3-fuzzer) `MIT` | A concurrent, command-line AWS S3 Fuzzer written in Go |
| [richarvey/s3-permission-checker](https://github.com/richarvey/s3-permission-checker) | Check read, write permissions on S3 buckets in your account |
| [gaul/are-we-consistent-yet](https://github.com/gaul/are-we-consistent-yet) `Apache-2.0` | Compare eventual consistency of object stores |

[↑ Back to top](#table-of-contents)

## Proxies & gateways

S3-compatible gateways, reverse proxies, authentication, and caching.

| Project | Description |
|---------|-------------|
| [gaul/s3proxy](https://github.com/gaul/s3proxy) `Apache-2.0` | Access other storage backends via the S3 API |
| [oxyno-zeta/s3-proxy](https://github.com/oxyno-zeta/s3-proxy) `Apache-2.0` | S3 Reverse Proxy with GET, PUT and DELETE methods and authentication (OpenID Connect and Basic Auth) |
| [axl89/s3cr3t](https://github.com/axl89/s3cr3t) `GPL-3.0` | A supercharged S3 reverse proxy |
| [fsouza/s3-upload-proxy](https://github.com/fsouza/s3-upload-proxy) `BSD-2-Clause` | Tool for proxying HTTP uploads to S3 and Elemental MediaStore, designed for video live streaming |
| [i5heu/bonito-cache](https://github.com/i5heu/bonito-cache) `AGPL-3.0` | Just hook it in front of your public S3 bucket and enjoy reduction in bandwidth costs from your bucket |
| [emmekappa/sftp-to-s3](https://github.com/emmekappa/sftp-to-s3) `Apache-2.0` | Docker image which provides an SFTP access mounting a specified S3 bucket |

[↑ Back to top](#table-of-contents)

## Development & integrations

S3 client libraries, SDKs, framework integrations, and application plugins.

| Project | Description |
|---------|-------------|
| [piskvorky/smart_open](https://github.com/piskvorky/smart_open) `MIT` | Utils for streaming large files (S3, HDFS, gzip, bz2, etc.) |
| [bradleyg/django-s3direct](https://github.com/bradleyg/django-s3direct) `MIT` | Directly upload files to S3 compatible services with Django |
| [jpetrucciani/bucketstore](https://github.com/jpetrucciani/bucketstore) `MIT` | A simple library for interacting with Amazon S3 |
| [bradenmacdonald/s3-lite-client](https://github.com/bradenmacdonald/s3-lite-client) `MIT` | A lightweight but powerful JavaScript S3 client |
| [taylorfinnell/awscr-s3](https://github.com/taylorfinnell/awscr-s3) `MIT` | A Crystal shard for S3 |
| [svtslv/nestjs-s3](https://github.com/svtslv/nestjs-s3) `MIT` | S3 module for NestJS |
| [thaiphan/magento-s3](https://github.com/thaiphan/magento-s3) `MIT` | Use Amazon S3 as the file storage solution for your Magento store |
| [thaiphan/magento2-s3](https://github.com/thaiphan/magento2-s3) `MIT` | Use Amazon S3 as the file storage solution for your Magento 2 application |
| [ttax00/obsidian-s3](https://github.com/ttax00/obsidian-s3) `MIT` | An Obsidian plugin for storage and retrieval of media attachments on S3 compatible services |
| [algoflows/zig-s3](https://github.com/algoflows/zig-s3) `MIT` | A simple and efficient Zig native S3 client library, supporting AWS S3 and S3-compatible services like MINIO |
| [sburkett/laravel-s3-tools](https://github.com/sburkett/laravel-s3-tools) `MIT` | This Laravel package contains additional functionality not currently in Laravel for interfacing with Amazon's S3 service |
| [dmjio/s3-signer](https://github.com/dmjio/s3-signer) `BSD-2-Clause` | Presigned S3 URLs for Haskell |
| [becem-gharbi/nuxt-s3](https://github.com/becem-gharbi/nuxt-s3) `MIT` | Edge compatible S3 client for Nuxt |
| [shaypal5/s3bp](https://github.com/shaypal5/s3bp) `MIT` | Read and write Python objects to S3, caching them on your hard drive to avoid unnecessary IO |
| [iamirmasoud/bulkboto3](https://github.com/iamirmasoud/bulkboto3) `MIT` | Python package for fast and parallel transferring a bulk of files to S3 based on boto3 |
| [samuraikun/aws-s3-mcp](https://github.com/samuraikun/aws-s3-mcp) `MIT` | MCP server to integrate AWS S3 and LLM |
| [DSchau/gatsby-source-s3](https://github.com/DSchau/gatsby-source-s3) | A Gatsby source plugin to query against an S3 bucket (including images) |
| [HQarroum/inquirer-s3](https://github.com/HQarroum/inquirer-s3) `MIT` | An S3 object selector for Inquirer |
| [notmeta/flameshot-s3-uploader](https://github.com/notmeta/flameshot-s3-uploader) `GPL-3.0` | Capture and upload flameshot screenshots to an S3 bucket |
| [abhay-ramesh/next-s3-uploader](https://github.com/abhay-ramesh/next-s3-uploader) `MIT` | A simple way to upload files to S3 from a Next.js app directory (aws s3, minio, or any s3 compatible service) |
| [hidekuma/flask-s3-viewer](https://github.com/hidekuma/flask-s3-viewer) `MIT` | Flask S3Viewer is a powerful extension that makes it easy to browse S3 in any Flask application. (Python S3 Uploader / Flask S3 Uploader) |
| [joeyism/s3-as-a-datastore](https://github.com/joeyism/s3-as-a-datastore) `Apache-2.0` | A way to use S3 as a key-value datastore instead of a real datastore |
| [rodneylab/sveltekit-s3-multipart-upload](https://github.com/rodneylab/sveltekit-s3-multipart-upload) `BSD-3-Clause` | How you can upload large files, such as video to your S3 compatible storage provider using presigned URLs |

[↑ Back to top](#table-of-contents)

## Automation & deployment

CI/CD pipelines, automated deployments, Git integrations, and build caching.

| Project | Description |
|---------|-------------|
| [bgahagan/git-remote-s3](https://github.com/bgahagan/git-remote-s3) `MIT` | Push and pull git repos to/from an s3 bucket, encrypted using gpg |
| [dmfutcher/git-s3-push](https://github.com/dmfutcher/git-s3-push) `MIT` | Deploy your git repo to an S3 bucket |
| [robinpellegrims/nx-remotecache-s3](https://github.com/robinpellegrims/nx-remotecache-s3) `MIT` | A task runner for Nx that uses S3 storage as a remote cache to share computation results across teams and CI |
| [jonelantha/gatsby-s3-action](https://github.com/jonelantha/gatsby-s3-action) `MIT` | Deploy a Gatsby Project to an AWS S3 bucket (optional Cloudfront support) |
| [berlam/github-bucket](https://github.com/berlam/github-bucket) `ISC` | Deploy public or private GitHub repositories automatically to S3 buckets using Git and deploy keys |
| [acifani/turborepo-s3-remote-cache](https://github.com/acifani/turborepo-s3-remote-cache) `Apache-2.0` | Store Turborepo remote cache in your S3 bucket |

[↑ Back to top](#table-of-contents)

## Data processing & monitoring

Data transformation, file processing, logging, and storage metrics.

| Project | Description |
|---------|-------------|
| [ribbybibby/s3_exporter](https://github.com/ribbybibby/s3_exporter) `Apache-2.0` | Exports Prometheus metrics about S3 buckets and objects |
| [simonw/s3-ocr](https://github.com/simonw/s3-ocr) `Apache-2.0` | Tools for running OCR against files stored in S3 |
| [bluedenim/log4j-s3-search](https://github.com/bluedenim/log4j-s3-search) `MIT` | Log4j appender with S3, Azure, Google Cloud, and search publishing |
| [xtream1101/s3-concat](https://github.com/xtream1101/s3-concat) `MIT` | Concat multiple files in s3 |
| [polakowo/yelp-3nf](https://github.com/polakowo/yelp-3nf) | 3NF-normalize Yelp data on S3 with Spark and load it into Redshift - automate the whole thing with Apache Airflow |

[↑ Back to top](#table-of-contents)

## Other projects

Other S3-compatible tools, utilities, and integrations that do not fit into the categories above.

| Project | Description |
|---------|-------------|
| [simonw/s3-credentials](https://github.com/simonw/s3-credentials) `Apache-2.0` | A tool for creating credentials for accessing S3 buckets |

[↑ Back to top](#table-of-contents)
