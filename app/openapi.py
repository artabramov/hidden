OPENAPI_PREFIX = "/api/v1"

OPENAPI_TAGS = [
    {
        "name": "Authentication",
        "description": "Authentication flow: login, token issuance and logout."
    },
    {
        "name": "Users",
        "description": "User management: register and retrieve users."
    },
]

OPENAPI_DESCRIPTION = """
[![Website](https://img.shields.io/badge/Website-joinhidden.com-2ea44f)](https://joinhidden.com)
[![Telegram](https://img.shields.io/badge/Telegram-@hiddenupdates-2CA5E0?logo=telegram&logoColor=white)](https://t.me/hiddenupdates)
[![Mastodon](https://img.shields.io/badge/Mastodon-%40artabramov-6364FF?logo=mastodon&logoColor=white)](https://mastodon.social/@artabramov)
[![GitHub stars](https://img.shields.io/github/stars/artabramov/hidden?style=flat&label=GitHub%20Stars&logo=github&logoColor=white)](https://github.com/artabramov/hidden)
[![Docker Hub pulls](https://img.shields.io/docker/pulls/artabramov/hidden?logo=docker&label=Docker%20Hub%20pulls&logoColor=white)](https://hub.docker.com/r/artabramov/hidden)
[![License](https://img.shields.io/badge/License-Non--Commercial-c0392b)](https://github.com/artabramov/hidden/blob/master/LICENSE)

## What is it and how does it work
A **RESTful** service that wraps a **gocryptfs**-encrypted directory inside
a container: the encrypted cipher directory is mapped to a host volume
(so everything persisted outside the container remains encrypted at
rest), while a decrypted mount exists only inside the container for
the API. It adds application-level controls such as role-based access
(Reader, Writer, Editor, Admin) and MFA with one-time codes for auth,
and exposes endpoints to upload/download files, create internal flat
directories (no nesting), attach tags, add comments, with predictable
JSON responses. The core is extensible via a hook system and plug-in
add-ons, so new capabilities can be introduced without modifying the
application code. On copy-on-write filesystems and on standard HDDs,
file deletion is irreversible.


## Roles and permissions
The first user who registers after installation is automatically
activated and granted the Admin role. All subsequent users are created
inactive and must be activated by an Admin before they can use the
system. Admin privileges are transferable: the system may have multiple
Admins, but it must always have at least one (i.e., the last remaining
Admin cannot be deactivated or demoted).

`Reader` — Can view anydata and download files.  
`Writer` — Can view anydata and download files, upload files and create collections.  
`Editor` — Can view anydata and download files, upload files and create collections, as well as modify them.  
`Admin` — Can view anydata and download files, upload files and create collections, as well as change and delete them. In addition, can manage other users and change application settings.  
"""
