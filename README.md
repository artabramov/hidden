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

## Resources
Official website:  
```
http://www.joinhidden.com/
```

Docker Hub image:  
```
https://hub.docker.com/r/artabramov/hidden
```

## Core
```mermaid
graph LR
    AUTH[Auth<br>Decorator]
    LOCK[Lock<br>Decorator]
    PYDANTIC[Pydantic<br>Schemas]
    ROUTER[FastAPI<br>Routers]
    HOOK[Hook<br>Triggers]
    MODEL[SQLAlchemy<br>Models]
    REPOSITORY[Repository]
    EM[Entity<br>Manager]
    CM[Cache<br>Manager]
    FM[File<br>Manager]
    BINARY[Binary<br>Data]
    POSTGRES[PostgreSQL<br>Database]
    REDIS[Redis<br>Cache]
    ROUTER --> MODEL
    MODEL --> REPOSITORY
    REPOSITORY --> EM
    REPOSITORY --> CM
    ROUTER --> BINARY
    BINARY --> FM
    EM --> POSTGRES
    CM --> REDIS
    PYDANTIC --> ROUTER
    AUTH --> ROUTER
    LOCK --> ROUTER
    ROUTER --> HOOK
```

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
