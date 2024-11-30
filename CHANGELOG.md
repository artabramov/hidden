# Changelog

## Version 0.1.0 (2024-12-01)
- **Refactored the codebase** to improve readability, maintainability, and overall structure of the application.
- **Updated and expanded unit tests** to enhance test coverage, ensuring better stability and error detection.
- **Revised and improved docstrings and comments** throughout the application, providing clearer explanations for future developers.

## Version 0.0.36 (2024-11-24)
- **Removed favorite entities** and eliminated the related code to streamline the application and reduce complexity.
- **Added functionality to flag or unflag documents**, along with the ability to filter documents based on their flag status, enhancing document management.

## Version 0.0.35 (2024-11-17)
- **Extracted the secret key** into a separate configuration file for improved security, easier management, and better environment isolation.
- **Added triggers and removed SQLAlchemy locks** to improve database performance, allowing more efficient data operations.

## Version 0.0.34 (2024-11-10)
- **Added routers for locking and unlocking collections**, providing better control over document actions within collections.

## Version 0.0.33 (2024-10-27)
- **Added a locked date for the collection**, enabling the tracking of when a collection was locked, improving the transparency of collection management.

## Version 0.0.32 (2024-10-20)
- **Added a plugin for logging user login activities**, enabling detailed tracking and auditing of user access events, improving system security and user activity monitoring.

## Version 0.0.31 (2024-10-13)
- **Removed heartbeats and enhanced telemetry** to improve system monitoring and performance tracking.
- **Added partner images**, enabling the display and management of images associated with partner entities.

## Version 0.0.30 (2024-10-06)
- **Added partner entities**, enabling the management and integration of partner-specific data, which facilitates smoother collaboration and data sharing.

## Version 0.0.29 (2024-09-29)
- **Added heartbeat functionality** for improved monitoring of the system’s health and performance.
- **Enabled Cross-Origin Resource Sharing (CORS)** to allow secure resource sharing between different origins.

## Version 0.0.28 (2024-09-22)
- **Added auto-generation of Sphinx documentation**, streamlining the creation of technical documentation.

## Version 0.0.27 (2024-09-15)
- **Added OpenAPI tags** to enhance the clarity and usability of the API documentation.
- **Extracted various actions into hooks**, improving the modularity and maintainability of the application.

## Version 0.0.26 (2024-09-08)
- **Refactored SQLAlchemy models** for improved structure and readability.

## Version 0.0.25 (2024-09-01)
- **Extracted constants into a separate file**, centralizing the configuration and making the application easier to maintain.
- **Added router for executing custom actions**, providing flexibility for custom logic.

## Version 0.0.24 (2024-08-25)
- **Added telemetry for application metrics and status**, providing valuable insights into the system’s health.
- **Added raw SQL query execution**, enabling the execution of custom SQL queries.

## Version 0.0.23 (2024-08-18)
- **Added application locking mechanism**, ensuring the integrity of critical operations by preventing race conditions.

## Version 0.0.22 (2024-08-11)
- **Added random sorting for SQLAlchemy models**, enabling randomized results when querying models.

## Version 0.0.21 (2024-08-04)
- **Added user deletion functionality**, allowing the removal of users from the application.

## Version 0.0.20 (2024-07-28)
- **Added management functionality for options**, enabling better control and configuration of application settings.

## Version 0.0.19 (2024-07-21)
- **Added app scheduler for periodic task execution**, automating recurring tasks within the application.
- **Added pre-processing events to the hooks system**, providing more flexibility for handling application logic.

## Version 0.0.18 (2024-07-14)
- **Refactored comment routers and improved validation logic**, enhancing the handling of comment-related requests.
- **Added routers for managing revisions and downloads**, offering better control over document revisions and downloads.

## Version 0.0.17 (2024-07-07)
- **Added revisions for uploaded files**, enabling versioning for files to track changes over time.

## Version 0.0.16 (2024-06-30)
- **Added SQLAlchemy locking mechanism**, preventing race conditions when working with database records.

## Version 0.0.15 (2024-06-23)
- **Added filters for document count and document size**, providing enhanced query capabilities for document management.
- **Fixed minor issues in Pydantic schemas**, ensuring proper validation and error handling.

## Version 0.0.14 (2024-06-16)
- **Added an example plugin for managing application hooks**, showcasing how to extend the application’s behavior.
- **Added lifecycle hooks for all actions**, improving control over actions performed in the application.

## Version 0.0.13 (2024-06-09)
- **Added caption for the user SQLAlchemy model**, allowing better customization and clarity in user-related queries.
- **Added tracking for the date when users last signed in**, providing useful information for user activity tracking.

## Version 0.0.12 (2024-06-02)
- **Added favorites feature** with corresponding endpoints, enabling users to mark and manage their favorite documents.

## Version 0.0.11 (2024-05-26)
- **Added document download tracking functionality**, providing insights into how often documents are downloaded.
- **Added endpoints for managing downloads**, making it easier to track and control file download activities.

## Version 0.0.10 (2024-05-19)
- **Added comment management for documents**, allowing users to add, edit, and delete comments on documents.

## Version 0.0.9 (2024-05-12)
- **Added subquery functionality in the entity manager**, improving the ability to perform complex queries in the entity manager.

## Version 0.0.8 (2024-05-05)
- **Improved error handling**, making the application more robust by properly managing exceptions.
- **Added logging for requests and responses**, providing better insight into the system’s interactions.

## Version 0.0.7 (2024-04-28)
- **Refactored helper functions**, improving the reusability and clarity of shared code.
- **Added custom error class**, enabling more structured and descriptive error messages.

## Version 0.0.6 (2024-04-21)
- **Added cache management**, improving performance by caching frequently accessed data.

## Version 0.0.5 (2024-04-14)
- **Added static endpoint for retrieving files**, making it easier to serve static files within the application.

## Version 0.0.4 (2024-04-07)
- **Added asynchronous file actions**, improving the efficiency of file-related operations.
- **Updated unit tests**, ensuring that all features are properly tested and verified.

## Version 0.0.3 (2024-03-31)
- **Updated docstrings and comments**, providing better documentation and clarity within the codebase.

## Version 0.0.2 (2024-03-24)
- **Added Sphinx documentation**, enabling automatic generation of technical documentation for the project.

## Version 0.0.1 (2024-03-17)
- **Created the application structure**, laying the foundation for scalable and maintainable development with organized modules and components.
- **Added the entity manager** for working with SQLAlchemy, simplifying interactions with the database and enhancing the management of entities across the application.
