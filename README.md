A fictional api for employees of medicinal organisation.

Application contains some basic http things, CRUD operations made by orm, sending mails and basic security with
bearer token. I was trying to make something different, that I usually  do in my job, so I used orm. The effects are 
mediocre. I prefer to use stored procedures and raw SQl than orm. Also distinguish domain part with domain services for
business things would be a great idea. This is "main" part of med_app, so I include here a docker-compose file.
Also table definitions from patients_api are made by orm hire. It is some fragile solution, from I not very proud now.
It is messy to deploy, and hard to develop separately patients_api.


Project architecture:

routers - related to HTTP thing, handling requests, adding headers and status code.

services - preparing data, authentication, all other things that are necessary, but not belong to other section 

database - connection to relational database, tables definitions.

data_access_layer - orm related things, adding things to tables, removing, etc.

models - validation input and output by pydantic models.


There is only some tests and all are E2e tests.
i now it's a bad structure, but honestly said I don't like testing and don't enjoy it.
