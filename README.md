# nonogram-ai
## Initial Setup (Django)

1. Clone the repo to your local machine:

> git clone https://github.com/samduwu/nonogram-ai.git

2. Create a Python virtual environment (if you haven't already; only needs to be done once):
   
> python -m venv .venv

3. Activate the virtual environment:
   
> .venv/Scripts/activate

Deactivate the environment via

> deactivate

4. Install dependencies for the project.

> cd nonogram_site \
> pip install -r requirements.txt

If any packages need to be updated, these must be saved to a new file via:

> pip freeze > requirements.txt

Or if you want to install the latest updates from a new file:

> pip install -U -r requirements.txt

5. Start the Django development server via:

> python manage.py runserver
