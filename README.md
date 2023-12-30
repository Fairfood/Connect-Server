# Trace Connect Backend

This application, built with Django(with django-rest-framework), simplifies the collection process for remote farmland transactions. Designed for collectors, it serves two main functions: enrolling farmers and recording on-site transactions. Collectors use NFC/QR code-based cards provided to farmers during enrollment, streamlining product delivery and facilitating farmer-verified payments. The app ensures a straightforward and efficient experience for both collectors and farmers in the agricultural ecosystem.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Authentication and Authorization](#authentication-and-authorization)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information)
- [Acknowledgments](#acknowledgments)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/your-project.git
    ```

2. Navigate to the project directory:

    ```bash
    cd your-project
    ```

3. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source venv/bin/activate
        ```

5. Install dependencies:

    ```bash
    pip install -r requirements/local.ext
    ```

## Configuration

1. Create a `.env` file in the project root and configure environment variables:

    ```env
    [app]
    ENVIRONMENT=local
    DEPLOYMENT=local
    ROOT_URL=http://localhost:8000
    FRONTEND_ROOT_URL=http://localhost:3000

    [dajngo]
    SECRET_KEY=**************************
    HASHID_SALT=**************************

    [database]
    DB_NAME=**************************
    DB_USER=**************************
    DB_PASSWORD=**************************
    DB_HOST=**************************
    DB_PORT=**************************

    REDIS_URL=redis://localhost
    REDIS_PORT=6379

    [email]
    EMAIL_HOST=smtp.gmail.com
    EMAIL_HOST_USER=**************************
    EMAIL_HOST_PASSWORD=**************************

    [lib]
    AWS_ACCESS_KEY_ID=**************************
    AWS_SECRET_ACCESS_KEY=**************************
    AWS_STORAGE_BUCKET_NAME=**************************
    ```

2. Apply migrations:

    ```bash
    python manage.py migrate
    ```

## Database Setup

1. Create super user with email as username and password.

    ```bash
    # for creating superuser
    python manage.py createsuperuser
    ```

2. Load currency details

    ```bash
    # for loading currency details
    python manage.py runsript load_currencies
    ```

## Usage

For running server locally

    ```bash
    python manage.py runserver

 Access the Django admin interface by navigating to [http://localhost:8000/connect/admin/](http://localhost:8000/connect/admin/) and log in with the superuser credentials created earlier.

## API Endpoints

- Open your browser and go to [http://localhost:8000/connect/v1](http://localhost:8000/connect/v1) to view the available API endpoints.
- Use tools like [curl](https://curl.se/) or [Postman](https://www.postman.com/) to make HTTP requests to the API endpoints.

## Authentication and Authorization

### Authentication

This Django DRF project uses token-based authentication. Follow these steps to obtain an authentication token:

1. **Create a User Account:**

    Make a POST request to the `/api/auth/register/` endpoint with the required user registration data.

    Example using `curl`:

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "your_username", "password": "your_password"}' http://localhost:8000/api/auth/register/
    ```

2. **Obtain an Authentication Token:**

    Make a POST request to the `/api/auth/token/` endpoint with the registered user credentials to obtain an authentication token.

    Example using `curl`:

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "your_username", "password": "your_password"}' http://localhost:8000/api/auth/token/
    ```

    Save the received token for subsequent requests.

### Authorization

This project implements role-based access control:

- **Admin Users:**
  - Admin users have full access to all resources and endpoints.

- **Authenticated Users:**
  - Authenticated users (users with a valid token) have limited access based on their roles.

- **Anonymous Users:**
  - Anonymous users have limited or no access to certain resources.

### Using the Authentication Token

Include the obtained token in the `Authorization` header of your requests:

```bash
curl -H "Authorization: Token your_token_here" http://localhost:8000/api/some-protected-endpoint/
```

## Testing

To run tests for the Django DRF project, use the following command:

```bash
python manage.py test
```

Running Specific Tests
```bash
python manage.py test <app_name>.tests.test_module
```
### Coverage

Then run the tests with coverage:
```bash
coverage run manage.py test
```
And generate a coverage report:
```bash
coverage report -m
```

## Contributing

We welcome contributions from the community! If you would like to contribute to this Django DRF project, please follow the guidelines below:

### Issues

- Before submitting a new issue, please check the [issue tracker](https://github.com/your-username/your-project/issues) to see if the issue has already been reported or discussed.
- When creating a new issue, provide a clear and detailed description, including steps to reproduce if applicable.
- If you're reporting a bug, include information about your environment (Django and DRF versions, database, operating system, etc.).

### Pull Requests

1. Fork the repository:

    ```bash
    git clone https://github.com/your-username/your-project.git
    cd your-project
    git fork
    ```

2. Create a new branch:

    ```bash
    git checkout -b feature-branch
    ```

3. Make your changes and commit:

    ```bash
    git add .
    git commit -m "Your descriptive commit message"
    ```

4. Push to the branch:

    ```bash
    git push origin feature-branch
    ```

5. Submit a pull request:

    - Go to the [Pull Requests](https://github.com/your-username/your-project/pulls) tab in the repository.
    - Click on "New Pull Request" and select the branch you just pushed.

6. Follow the pull request template and provide necessary details.

### Coding Standards

- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
- Write meaningful commit messages and keep the commit history clean.

### Testing

- Ensure that your changes do not break existing tests.
- If you're adding a new feature, include relevant tests.
- Run the test suite locally before submitting a pull request.

### Code of Conduct

Please note that this project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Report any unacceptable behavior to [maintainer email].

### Review Process

- The project maintainers will review your pull request and may provide feedback or request changes.
- Once the changes are approved, the pull request will be merged.

Thank you for contributing to our Django DRF project! If you have any questions or need further assistance, feel free to reach out to [maintainer email].

[contributing-image]: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
[contributing-url]: https://github.com/your-username/your-project/blob/main/CONTRIBUTING.md

## License

## Contact Information

If you have any questions, suggestions, or feedback, feel free to reach out:

- **Maintainer:** [Your Name]
- **Email:** [your.email@example.com]

You can also open an issue on the [issue tracker](https://github.com/your-username/your-project/issues) for bug reports, feature requests, or general discussions related to the project.

Follow us on Twitter: [@your_project_handle](https://twitter.com/your_project_handle)

We appreciate your interest and contributions to our Django DRF project!
