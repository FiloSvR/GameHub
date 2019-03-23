#Instruction to initialize Django project
1. Install python
2. Install pip
3. Install virtualenv -> pip install virtualenvwrapper-win
4. Create virtualenv ->  mkvirtualenv 'projectName'
5. Install all the modules -> pip install -r requirements.txt
7. Complete migration -> python manage.py migrate
8. When the command run before will ask about SECRECT_KEY and other, create a .env file in the root at the same level of manage.py. The file .env contains the variable that will fill gameHub/settings.py
9. Add in .env teh variables DEBUG= ,SOCIAL_AUTH_GOOGLE_OAUTH2_KEY= , SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET= 
10. If ValueError: Unable to configure handler 'filehandler' appears you need to create the folder 'log' in the GameHub directory
11. Run local server -> python manage/py runserever
##### Every time a new prompt is open you need to activate the virtualenv -> workon 'projectName'
##Pycharm on windows
set the python interpreter searching in the env folder (check user -> Envs). There there should be the env folder for the environment you created in the project, in that folder select Script/python.exe. Doing so all the module should be recognized by pycharm
   