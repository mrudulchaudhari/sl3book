# sl3book
# Bookstore Management System (Assignment 1)

## Project Overview

This project is a simple Bookstore Management System built using the Django framework (Python). It allows users to browse books, add them to a shopping cart (using sessions), and includes a custom administration panel for managing the book inventory. The project is fully containerized using Docker and includes a basic Jenkins pipeline definition for CI/CD.

## Features Implemented

* **User Authentication:**
    * User Registration
    * User Login / Logout
    * Restricted access based on login status.
* **User Interface:**
    * View a list of all available books.
    * View detailed information for a single book.
    * Add books to a persistent shopping cart (using Django Sessions).
    * View the shopping cart contents and total price.
* **Custom Admin Panel (`/custom-admin/`):**
    * Accessible only to staff users (`is_staff=True`).
    * List all books in the inventory.
    * Add new books (including optional cover image upload).
    * Edit existing book details (including image).
    * Delete books from the inventory.
    * *Note: Uses Class-Based Views and manual HTML forms (No Django Admin, No Django Forms).*
* **DevOps:**
    * Dockerized environment using `Dockerfile` and `docker-compose.yml`.
    * Basic CI/CD pipeline defined in `Jenkinsfile`.

## Tech Stack

* **Backend:** Python 3.11+, Django 4.x
* **Frontend:** HTML5, CSS3 (Bootstrap 5 used for styling)
* **Database:** SQLite (Default development DB)
* **WSGI Server:** Gunicorn (used in Dockerfile)
* **Image Handling:** Pillow
* **Containerization:** Docker, Docker Compose
* **CI/CD:** Jenkins (via `Jenkinsfile`)

## Setup & Run Instructions (Using Docker Compose)

These instructions assume you have **Docker** and **Docker Compose** installed and running on your system.

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd bookstore_project # Or your repository's root folder name
    ```

2.  **Build the Docker Image:**
    (Ensure Docker Desktop is running)
    ```bash
    docker-compose build
    ```

3.  **Apply Database Migrations:**
    This creates the necessary database tables inside the container.
    ```bash
    docker-compose run --rm web python manage.py migrate
    ```
    *(The `--rm` flag removes the temporary container after the command finishes)*

4.  **Create a Superuser (for Admin Access):**
    Follow the prompts to create an admin account. Remember the username and password. Make sure this user has `is_staff=True`.
    ```bash
    docker-compose run --rm web python manage.py createsuperuser
    ```

5.  **Start the Application:**
    ```bash
    docker-compose up
    ```
    *(Leave this terminal running. To run in the background, use `docker-compose up -d`)*

6.  **Access the Application:**
    * Open your web browser and go to: `http://localhost:8000`
    * **Custom Admin Panel:** Access it at `http://localhost:8000/custom-admin/` (Log in using the superuser credentials created in step 4).

7.  **Stop the Application:**
    * If running in the foreground, press `Ctrl+C` in the terminal.
    * If running in detached mode (`-d`), use: `docker-compose down`

## Docker Usage Notes

* The application runs inside a Docker container defined by the `Dockerfile`.
* `docker-compose.yml` is used to manage the application's service (`web`).
* `docker-compose build` builds the image.
* `docker-compose up` starts the service. The `command` in `docker-compose.yml` uses `python manage.py runserver` for development, enabling auto-reloading.
* The `volumes: .:/app` line syncs your local code changes into the running container.
* Port `8000` on your host machine is mapped to port `8000` inside the container.
* The `media/` directory (for uploaded images) and `db.sqlite3` are stored locally but are accessible inside the container via the volume mount. For more robust data persistence, named volumes could be used (commented out in `docker-compose.yml`).

## Jenkins Usage Notes

* A `Jenkinsfile` is included in the root of the repository.
* It defines a basic declarative pipeline with stages for:
    * Checking out code (Placeholder)
    * Building the Docker image (`docker build ...`)
    * Running Django tests (`python manage.py test ...` inside the container)
    * Deploying the application (Placeholder)
* Executing this pipeline requires a configured Jenkins server instance with Docker capabilities. This file serves to define the CI/CD process as required by the assignment.
