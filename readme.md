# Setting up Virtual Environment

### This project requires **Python 3.12**.

> To ensure compatibility and proper functionality, please make sure you
> have Python 3.12  installed. You can verify your
> Python version by running the following command in your terminal: 
> ```bash   python --version  ```

### Create the Virtual Environment
In the root directory of your project, create a virtual environment named `env`:
```bash
virtualenv env
```
### Activate the Virtual Environment

 - **For Windows:**
 ```bash
 .\env\Scripts\activate
 ```
 - **For macOS/Linux**:
 ```bash
 source env/bin/activate
 ```
 
 ### Install Dependencies
 With the virtual environment activated, install all required Python dependencies:
 ```bash
 pip install -r requirements.txt
 ```


> ### Recommendation
> For handling multiple Python versions on your device, we recommend
> using **pyenv**. Pyenv is a simple tool that lets you install, manage,
> and switch between multiple Python versions easily, without
> interfering with the system Python. This can be especially useful if
> you work on projects requiring different Python versions.
> To install `pyenv`, follow the instructions on the [pyenv GitHub
> page](https://github.com/pyenv/pyenv).

# Docker Setup
### Build and Start Docker Containers

In the root directory of the project, use the following command to build and start the containers in detached mode:

```bash
docker-compose up --build -d
```

### View Running Containers
Confirm that all containers are running by listing them:
```bash
docker ps
```

### Stop Docker Containers
To stop the containers without removing them, use:
```bash
docker-compose stop
```

### Shut Down Docker Containers
To stop and remove the containers, use:
```bash
docker-compose down
```

# Writing Commit Messages
A good commit message should be clear and concise, summarizing what changes were made and why. Use the following format:

type(scope): subject
body
footer

### Commit Message Components

1.  **Type**: The type of change you are committing. Common types include:
    
    -   `feat`: A new feature
    -   `fix`: A bug fix
    -   `refactor`: Code change that neither fixes a bug nor adds a feature
    -   `docs`: Documentation only changes
    -   `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
    -   `test`: Adding missing tests or correcting existing tests
    -   `chore`: Other changes that don't modify src or test files
2.  **Scope**: The scope of the change (e.g., component or file names). This is optional but can be helpful.
    
3.  **Subject**: A short, imperative sentence that describes the change.
    
4.  **Body**: (Optional) A more detailed description of the change and its purpose.
    
5.  **Footer**: (Optional) References to tasks or issues, such as task IDs or issue numbers.

### Examples

-   Adding a feature:
    
    ```shell
    feat(auth): add user login functionality
    
    This commit adds a new user login feature with JWT authentication.
    
    Resolves #123
    ```

## Git Branching Rules and Best Practices

### Overview

Branching is a powerful feature in Git that allows you to isolate your work and manage multiple lines of development. Proper use of branches can greatly enhance collaboration and project organization.

### Branch Naming Conventions

1.  **Feature Branches**: Use for new features.

    `feature/<description>` 
    
2.  **Bug Fix Branches**: Use for bug fixes.
  
    `fix/<description>` 
    
3.  **Refactor Branches**: Use for code refactoring.

    `refactor/<description>` 
    
5.  **Hotfix Branches**: Use for critical bug fixes that need immediate attention.

    `hotfix/<description>` 
    
6.  **Release Branches**: Use for preparing a release.
    
    `release/<version>` 
    

### Examples

-   `feature/user-authentication`
-   `fix/login-bug`
-   `refactor/database-queries`
-   `hotfix/security-issue`
-   `release/1.0.0`

### Branching Workflow

#### Main Branches

1.  **`main` or `master`**: The default, stable branch. All production-ready code is merged here.
2.  **`develop`**: Integration branch for features. This is where you integrate feature branches and prepare for the next release.

#### Feature Workflow

1.  **Create a Branch**: Always create a new branch from the `develop` branch.

    `git checkout develop
    git pull origin develop
    git checkout -b feature/your-feature-name` 
    
2.  **Work on Your Branch**: Make your changes and commit them to your branch.
    
    `git add .
    git commit -m "feat(your-feature): add new feature"` 
    
3.  **Push Your Branch**: Push your branch to the remote repository.
    
    `git push origin feature/your-feature-name` 
    
4.  **Create a Pull Request**: Once your feature is complete, create a pull request (PR) to merge your branch into the `develop` branch.
    

#### Bug Fix Workflow

1.  **Create a Branch**: Always create a new branch from the `develop` branch.
    
    `git checkout develop
    git pull origin develop
    git checkout -b fix/your-fix-name` 
    
2.  **Work on Your Branch**: Make your changes and commit them to your branch.
    
    `git add .
    git commit -m "fix(your-fix): fix the issue"` 
    
3.  **Push Your Branch**: Push your branch to the remote repository.
    
    `git push origin fix/your-fix-name` 
    
4.  **Create a Pull Request**: Once your fix is complete, create a pull request to merge your branch into the `develop` branch.
    

#### Hotfix Workflow

1.  **Create a Branch**: Always create a new branch from the `main` branch.

    `git checkout main
    git pull origin main
    git checkout -b hotfix/your-hotfix-name` 
    
2.  **Work on Your Branch**: Make your changes and commit them to your branch.

    `git add .
    git commit -m "hotfix(your-hotfix): fix critical issue"` 
    
3.  **Push Your Branch**: Push your branch to the remote repository.

    `git push origin hotfix/your-hotfix-name` 
    
4.  **Create a Pull Request**: Once your hotfix is complete, create a pull request to merge your branch into the `main` branch.
    

#### Release Workflow

1.  **Create a Branch**: Create a new release branch from the `develop` branch.

    `git checkout develop
    git pull origin develop
    git checkout -b release/1.0.0` 
    
2.  **Prepare the Release**: Perform final checks, updates, and testing.
    
3.  **Push Your Branch**: Push your branch to the remote repository.

    `git push origin release/1.0.0` 
    
4.  **Create Pull Requests**: Once the release is ready, create pull requests to merge your release branch into both `main` and `develop`.
    

### Merging

-   **Feature/Bug Fix to Develop**: Ensure your branch is up to date with `develop` before merging.

    `git checkout develop
    git pull origin develop
    git checkout feature/your-feature-name
    git merge develop` 
    
-   **Hotfix to Main**: Merge hotfix branches directly into `main` and `develop`.
    
    `git checkout main
    git merge hotfix/your-hotfix-name
    git checkout develop
    git merge hotfix/your-hotfix-name` 
    
-   **Release to Main and Develop**: Merge release branches into both `main` and `develop`.

    `git checkout main
    git merge release/1.0.0
    git checkout develop
    git merge release/1.0.0` 
    

### Deleting Branches

-   **Local Branch**: After merging, delete your local branch.

    `git branch -d feature/your-feature-name` 
    
-   **Remote Branch**: Delete the remote branch.
    
    `git push origin --delete feature/your-feature-name` 
    

### Best Practices

1. **Keep Branches Small and Focused**: Each branch should have a single purpose.
2. **Commit Often**: Regular commits help in tracking progress and easing potential conflict resolution.
3. **Regularly Sync with Base Branch**: Frequently update your branch with changes from the base branch to minimize conflicts.
4. **Use Meaningful Names**: Branch names should clearly convey the purpose of the branch.
5. **Review Before Merging**: Use pull requests for code reviews to ensure code quality and team collaboration.
6. **Test Thoroughly**: Ensure all tests pass before merging.

# Postgres Database Issues Help Commands

### Drop the Database
Run the `DROP DATABASE` command for the database you want to remove. Replace `originDB` with the database name.
```sql
DROP DATABASE database_name;
```
If the database name contains uppercase letters, wrap it in double quotes when referencing.
example :
```sql
DROP DATABASE "originDB";
```

### switch to another database
```sql
\c postgres
```

### login 
```sql
psql -U "admin@admin" -d postgres
```

### List the databases
```sql
\l
```

### Recreate the Database
```sql
CREATE DATABASE "originDB" OWNER "admin@admin";
```
### Check `settings.py`
Ensure your Django settings point to the correct database. Look for the `DATABASES` setting in your `settings.py` file
```python
if DEBUG:  
    DATABASES = {  
        'default': {  
            'ENGINE': 'django.db.backends.postgresql',  
  'NAME': os.getenv('ORIGIN_DB_NAME'),  
  'USER': os.getenv('ORIGIN_DB_USER'),  
  'PASSWORD': os.getenv('ORIGIN_DB_PASSWORD'),  
  'HOST': os.getenv('ORIGIN_DB_HOST'),  
  'PORT': os.getenv('ORIGIN_DB_PORT'),  
  },  
  }  
else:  
    DATABASES = {  
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))  
    }
```
### Run Migrations
Once the database is recreated, you need to apply migrations to set up the schema for your Django project
```python
python manage.py migrate
```
