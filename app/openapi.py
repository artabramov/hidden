# app/openapi.py
# SPDX-License-Identifier: GPL-3.0-only

TAGS_METADATA = [
    {
        "name": "Initialization",
        "description": (
            "Cipherdir management, lockdown mode control, "
            "and runtime state retrieval."
        ),
    },
    {
        "name": "Authentication",
        "description": (
            "User registration; two-step sign-in; token issue and logout."
        ),
    },
    {
        "name": "Users",
        "description": (
            "User management and listing."
        ),
    },
    {
        "name": "Folders",
        "description": (
            "Folder creation, hierarchy management, and navigation."
        ),
    },
    {
        "name": "Files",
        "description": (
            "File upload, download, and other operations."
        ),
    },
    {
        "name": "Tags",
        "description": (
            "Tag usage statistics."
        ),
    },
    {
        "name": "Comments",
        "description": (
            "Comment creation, update, and deletion."
        ),
    },
    {
        "name": "Variables",
        "description": (
            "Application-level namespaced key-value storage."
        ),
    },
    {
        "name": "Services",
        "description": (
            "Application metrics and audit log."
        ),
    },
]
