# UMAMI

[![Join the chat at https://gitter.im/AIE-Guild/umami](https://badges.gitter.im/AIE-Guild/umami.svg)](https://gitter.im/AIE-Guild/umami?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Universal Multigame AIE Membership Interface

[![Build Status](https://travis-ci.org/AIE-Guild/umami.svg?branch=develop)](https://travis-ci.org/AIE-Guild/umami)
[![Coverage Status](https://coveralls.io/repos/github/AIE-Guild/umami/badge.svg?branch=develop)](https://coveralls.io/github/AIE-Guild/umami?branch=develop)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/223ee6c21dab4d828912fd733a68541d)](https://www.codacy.com/app/mrogaski/umami?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=AIE-Guild/umami&amp;utm_campaign=Badge_Grade)
[![Codebeat Badge](https://codebeat.co/badges/8ec3519e-9b4d-4717-aabb-7d448fd8628c)](https://codebeat.co/projects/github-com-aie-guild-umami-develop)
[![Known Vulnerabilities](https://snyk.io/test/github/aie-guild/umami/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/aie-guild/umami?targetFile=requirements.txt)

## Overview

UMAMI is a Django-based web application for managing guild membership for gaming guilds that span multiple
massively multiplayer online role playing games (MMORPGs).  This is a rewrite of an application that I first implemented
in Django 1.5, a project which taught me much.

I am not developing the application with any intention of generalization, however I am building out each component
in a way that it will not be difficult to pull out parts you may find useful and drop into another Django project.


## Installation


TBD


## Development

This describes how to set up a local development environment for working on UMAMI.

1.  Clone the repository.

    git clone git@github.com:AIE-Guild/umami.git


1.  Set up a virtual environment.

  * Linux

    cd umami
    virtualenv -p python3.6 env
    source env/bin/activate

  * Windows

    cd umami
    virtualenv -p python3.6 env
    env\Scripts\activate

  * Anaconda

    cd umami
    conda create -p .\env python=3.6
    activate .\env

1.  Install the dependencies.

    pip install -r requirements-dev.txt


1.  Test the installation.

    python manage.py check


1.  Create an environment file for configuration.

```
SECRET_KEY=...
DEBUG=true
INTERNAL_IPS=127.0.0.1
ALLOWED_HOSTS=*
DJANGO_LOG_LEVEL=DEBUG
OAUTHLIB_INSECURE_TRANSPORT=true
EMAIL_HOST=mail.example.net
EMAIL_PORT=587
EMAIL_HOST_USER=someuser
EMAIL_HOST_PASSWORD=p@ssw0rd
EMAIL_USE_TLS=true
SERVER_EMAIL=someuser@example.net
DEFAULT_FROM_EMAIL=someuser@example.net
LOCALDEV=true
```


1.  Build the database schema.

    python manage.py migrate


1.  Add a superuser.

    python manage.py createsuperuser


1.  Create a [Discord app](https://discordapp.com/developers/applications/me) for OAuth2 authentication.  You will need
    the **client_id** and **client_secret** credentials, and you will need to specify
    `http://127.0.0.1:8000/accounts/discord/login/callback/` as a **redirect_uri**.

1.  Start the local server.

    python mange.py runserver


1.  Log in with the superuser account and navigate to the [admin panel](http://127.0.0.1:8000/admin/).


1.  Update the entry in the **Sites** table to specify `127.0.0.1`.


1.  Add a **Social Application** entry for Discord with the client credentials you obtained from Discord.




