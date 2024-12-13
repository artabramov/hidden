# Hidden

## How to install
Execute the command in the console:  
```
make install
```

The application is available on:  
```
http://localhost
```

The Swagger docs are available on:  
```
http://localhost/docs
```

The Sphinx docs are available on:  
```
http://localhost/sphinx/
```

## Core mechanics
The main entity handler used across all application routers is the Repository. A concrete instance of the Repository is created for each specific entity type. It handles interactions with a PostgreSQL database through an encapsulated Entity Manager and Redis cache via a Cache Manager. The primary application entities are SQLAlchemy models, and Pydantic validation schemas are used for validation across the application.
```mermaid
graph LR
    AUTH[Auth<br>Decorator]
    LOCK[Lock<br>Decorator]
    PYDANTIC[Pydantic<br>Schemas]
    ROUTER[FastAPI<br>Routers]
    HOOK[Hooks]
    REPOSITORY[Repository]
    EM[Entity<br>Manager]
    CM[Cache<br>Manager]
    FM[File<br>Manager]
    POSTGRES[PostgreSQL<br>Database]
    REDIS[Redis<br>Cache]
    BINARY[File<br>System]
    ROUTER --> REPOSITORY
    REPOSITORY --> EM
    REPOSITORY --> CM
    ROUTER --> FM
    FM --> BINARY
    EM --> POSTGRES
    CM --> REDIS
    PYDANTIC --> ROUTER
    AUTH --> ROUTER
    LOCK --> ROUTER
    ROUTER --> HOOK

```

## Resources
Official website:  
[http://joinhidden.com](http://joinhidden.com)

Docker Hub image:  
[https://hub.docker.com/r/artabramov/hidden](http://www.joinhidden.com/)

## License
[Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
