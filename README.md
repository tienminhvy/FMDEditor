# FMDEditor
A web app for managing Markdown posts using Django. FMDEditor stands for Fast MarkDown Editor.

# Requirement

## Prerequisites
- [Python>=3.12.2](https://www.python.org/downloads/)
- WSL (Or Cmder) is installed
- Redis (Using docker or [laragon](https://laragon.org) WAMP)

# Installation
0. Ensure that you already have all of the items above.
1. Clone this project to your local machine with this command:
```bash
git clone https://github.com/tienminhvy/FMDEditor.git
cd FMDEditor
```
2. Install all requirements:
```bash
pip install -r requirements.txt
```
3. Migrate all changes:
```bash
python manage.py migrate
```
4. Create super user with your provided credentials:
```bash
python manage.py createsuperuser
```
5. Run project:
```bash
python manage.py runserver
```
6. Now enter 127.0.0.1:8000 to your browser's address bar to see the magic.

# Documentation

# Issues, Bugs & Feature Requests

Just create new issue if you found any problems here: https://github.com/tienminhvy/FMDEditor/issues

# Support & Questions

Need assisstance? Do not hesitate to ask for help at: https://github.com/tienminhvy/FMDEditor/discussions
