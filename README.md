# twitter clone
## a simple CRUD app built using Python, HTML, CSS, Jinja2, and SQL

### Why?

This project was a part of [CMC's CS040 class](https://github.com/mikeizbicki/cmc-csci040). This project consisted of a series of required tasks, including:
- creating a home page
- creating a log in system
- creating a log out system
- creating a system for adding new user accounts
- creating a system for adding and posting messages

The specific criterea for each of the mandatory tasks, as well as the optional ones outlined below, can be found [here](https://github.com/mikeizbicki/cmc-csci040/tree/2021fall/hw_05).

Numerous optional tasks were also completed, including:
- nice styling with CSS
- URLs in messages converted to actual links with the `<a>` tag
- add the ability to delete user accounts and their messages
- automatically log in and redirect to home when someone creates a new user
- allow password changing
- assign each user a unique image using [robohash](https://robohash.org/)
- allow markdown formatting of posted messages (and prevent HTML injection using the [bleach library](https://bleach.readthedocs.io/en/latest/index.html))

### How?

The procedure for running the app locally is relatively simple:
1. make sure you have flask and bleach installed
1. from the terminal, run the `db_create.py` file to create the database (populated with a few accounts and messages)
1. from the terminal, run the `app.py` file
1. copy the address it outputs into your browser
1. all functions will work as intended as long as all the templates are downloaded correctly

###### not bad for only half a year of learning to code
