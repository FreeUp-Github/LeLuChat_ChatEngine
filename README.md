# LeLuChat
LeLuChat provides REST API and Websocket to enable admin users of website to chat with their customers. LeLuChat flow can
be seen [here](https://github.com/FreeUp-Github/LeLuChat_ChatEngine/blob/develop/docs/software/LeLuChat_Flow.md).  
## Development Environment
### Build Docker Image
`docker compose build`

### Test API
`docker compose run web python manage.py test`

### Run Development Server
`docker compose up`

## Documentation
### Database Model Design
Database Schema Can be seen on below link:  
[Database Schema](https://github.com/FreeUp-Github/LeLuChat_ChatEngine/blob/develop/docs/software/database_schema.md)

### REST API Design
Rest API design and urls can be seen by Swagger UI on below link:  
[Swagger UI](https://freeup-github.github.io/LeLuChat_ChatEngine/)
