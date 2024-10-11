# Changelog

## Version 0.0.46 (2024-10-11)
- **Added heartbeats**: Implemented heartbeat functionality for monitoring.
- **Added CORS support**: Enabled Cross-Origin Resource Sharing for better API accessibility.

## Version 0.0.45 (2024-10-05)
- **Added Sphinx Documentation**: Integrated Sphinx documentation for improved API reference.

## Version 0.0.44 (2024-09-29)
- **Added cache erase**: Introduced a router to clear all cached data in the Redis cache.
- **Added OpenAPI tags**: Introduced descriptions for OpenAPI tags to enhance API documentation clarity.
- **Refactoring**: Extracted various actions into hooks for improved modularity and maintainability.

## Version 0.0.43 (2024-09-28)
- **Fixed bug**: Resolved a bug related to the relationship between datafiles and revisions.
- **Renamed models**: Updated the SQLAlchemy model names from `document` to `datafile` and from `upload` to `revision` for improved clarity and accuracy.

## Version 0.0.42 (2024-09-24)
- **Added constants**: Introduced a dedicated module for constants, improving code organization and maintainability.
- **Added custom router**: Enhanced routing capabilities with a custom execution router for more flexible request handling.

## Version 0.0.41 (2024-09-18)
- **Added telemetry**: Introduced a new endpoint for system telemetry, providing insights into application metrics and status.
- **Added raw query execution**: Enabled raw SQL query execution in the entity manager for more flexible database interactions.
- **Updated unit tests**: Revised unit tests to align with the new changes and ensure better coverage.

## Version 0.0.40 (2024-09-15)
- **Added lock mechanism**: Implemented a decorator to enforce execution locks based on a lock file’s presence, raising HTTP 503 errors if the file exists. This helps manage service availability and prevent concurrent access during maintenance or restricted states.

## Version 0.0.39 (2024-09-12)
- **Added random sorting**: Implemented a new random sorting option in the EntityManager to enhance the diversity of query results. This feature improves the randomness and variability of data retrieval, making query outcomes less predictable and more robust.

## Version 0.0.38 (2024-09-10)
- Added user deletion functionality, allowing administrators to delete
  user accounts with checks to prevent self-deletion and robust error
  handling for various failure scenarios.

## Version 0.0.37 (2024-09-06)
- Added management functionality for options, including creation,
  retrieval, updating, and deletion.

## Version 0.0.36 (2024-09-05)
- Added an app scheduler for periodic task execution.
- Added pre-processing events to the hooks system.

## Version 0.0.35 (2024-09-01)
- Refactored comment routers and improved validation logic.
- Added routers for managing revisions, including retrieving details of
  a specific revision, downloading the associated file, and listing
  revisions based on query parameters.
- Added routers for managing download entities, including endpoints for
  retrieving details of a specific download and listing downloads based
  on query parameters.

## Version 0.0.34 (2024-08-31)
- Added revisions for uploaded files, enhancing the capability to manage
  and track different versions of files throughout their lifecycle.

## Version 0.0.33 (2024-08-31)
- Added a locking mechanism to prevent concurrent modifications of
  records. This feature ensures that all records of a specified model
  class are locked during critical operations, enhancing data integrity
  and consistency in multi-user environments.

## Version 0.0.31 (2024-08-29)
- Added filters for datafile count and datafile size in the collections
  list router.

## Version 0.0.30 (2024-08-27)
- Added external application description to Markdown (.md) file for
  improved documentation and user understanding.
- Added minor fixes to Pydantic schemas to enhance data validation and
  consistency.

## Version 0.0.29 (2024-08-25)
- Added an example extension for managing application hooks.
- Added lifecycle hooks for user actions, collection operations, and
  datafile management.

## Version 0.0.28 (2024-08-25)
- Added an editable field for user signatures, allowing users to input
  and update their signature information.
- Added tracking for the date when users last signed in.
- Added the ability for each user to define their own token expiration
  date upon login, providing flexibility in managing token validity.

## Version 0.0.27 (2024-08-25)
- Added favorites feature with endpoints for creating, retrieving,
  deleting, and listing favorites.

## Version 0.0.26 (2024-08-24)
- Added download tracking functionality, including a counter for
  datafile downloads and detailed record-keeping for each download event.
- Added endpoints and functionality to retrieve and manage download
  events, including listing and viewing individual downloads.

## Version 0.0.25 (2024-08-24)
- Added SQLAlchemy model and Pydantic schemas for comment management,
  including validation.
- Added full set of CRUD operations for comments, encompassing creation,
  retrieval, updating, and deletion functionalities.

## Version 0.0.24 (2024-08-24)
- Introduced subquery functionality in the entity manager for more
  complex querying capabilities.

## Version 0.0.23 (2024-08-23)
- Improved error handling to enhance the management and response to
  exceptions, including more precise logging and informative responses.
- Enhanced logging for requests and responses, including method, URL,
  headers, and status details.
- Improved extension initialization for more reliable loading and
  registration of hooks from extension modules.

## Version 0.0.22 (2024-08-23)
- Enhanced error handling across authentication and permission functions
  to provide more detailed and accurate error messages.

## Version 0.0.21 (2024-08-21)
- Added libraries to improve accessibility and streamline imports across
  the application.
- Refactored helper functions to be standalone and classless,
  simplifying their usage.
- Enhanced the E class by refining its structure and functionality.

## Version 0.0.20 (2024-08-18)
- Introduced the capability to add and manage tags associated with
  documents, enhancing metadata and search functionality.
- Enhanced cache management to prevent the storage of entities with
  broken relationships, ensuring data integrity.

## Version 0.0.19 (2024-08-18)
- Added a static endpoint for retrieving datafile thumbnails.
- Refactored code structure and organization for better maintainability
  and performance.

## Version 0.0.18 (2024-08-18)
- Implemented a route to retrieve datafile details by ID with access
  level checks and post-retrieval actions via a hook.

## Version 0.0.17 (2024-08-18)
- Added asynchronous file copying functionality to the FileManager
  class for efficient large file operations.
- Introduced methods for determining file types based on MIME types and
  added a VideoHelper class for video processing.
- Implemented automatic thumbnail generation for images and videos.
- Updated unit tests for new features and applied various minor fixes
  and improvements.

## Version 0.0.16 (2024-08-17)
- Upgraded docstrings for the EntityManager and FileManager classes to
  provide more detailed descriptions.

## Version 0.0.15 (2024-08-17)
- Enhanced Sphinx documentation generation scripts for more accurate and
  comprehensive outputs.
- Upgraded docstrings in the EntityManager class.
