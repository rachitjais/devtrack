# DevTrack – API Usage & Performance Tracking System

## Overview

DevTrack is a backend system built using Flask that tracks API usage and provides performance analytics such as request count, error rates, and response time.

## Features

* User authentication using JWT
* Project-based API key system
* API request logging
* Performance analytics (request count, error rate, response time)
* Full CRUD operations for project management

## Tech Stack

* Python (Flask)
* SQLite
* SQLAlchemy
* JWT Authentication

## API Endpoints

* POST /register
* POST /login
* POST /create_project
* GET /projects
* PUT /update_project/<id>
* DELETE /delete_project/<id>
* POST /log
* GET /project_analytics/<id>

## How It Works

1. User registers and logs in
2. Creates a project and gets an API key
3. Sends API logs using API key
4. System stores logs and generates analytics

## Author

Rachit Jaiswal
