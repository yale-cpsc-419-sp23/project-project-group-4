# project-project-group-4

## 🗓 Updates Timeline

- February 19: Skeleton code done
    - We have a code skeleton
        - the `website` folder contains the backend. That is, models (`models.py`), controllers (`views.py`), and routes (`views.py`) for the backend
        - the `templates` folder (inside the `website` folder) contains the frontend code
        - the `static` folder (inside the `website` folder) contains the static files (images, css, js, etc.)
- March 10: MVP done
    - Additional Features:
        - Get, Post, and delete/recover/found lost items: Enable users to post a description of a lost item they are searching for, which is viewable by other users, 
        and remove it once found. The same feature applies to people who have found items.
        - UML diagram for database - see DatabaseUML.pdf
        - Database design for storing lost and found objects and information about users
        - Basic UI design of being able to scroll through main page and see items and descriptions
        - Note: Update lost items was not completed, however, we will complete it over the next iteration - We let Matthew know about this.
- March 26: Alpha done
    - Additional Features:
        - Basic search functionality based on keywords
        - Item category search based on tags
        - Keyword suggestions
        - Date range search based on dates of when items were lost or found
        - UI improvements to make website more user friendly
        - Note: The update lost items feature proposed for the MVP was completed in this iteration ✅

## 🤔 How to run?

1. Install the dependencies
    - `pip install -r requirements.txt`
2. Run the app with `python main.py --port 8000` in the main directory with an optional --port argument

