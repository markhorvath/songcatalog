# To the Reviewer:
I put the client_secrets file in gitignore.  I *think* you can still run it as long as its in there, but if not I can either
push the client_secrets.json file up publicly, or send you the whole thing as a zip.

# Song Catalog Project for Udacity Full Stack Nanodegree
This is a catalog of music categories and numerous old songs.
It provides info on the individual songs such as their key, time signature, beats per minute,
year they were created, and eventually will have more info for academic and other purposes.

## Installation
1. Fork the repo!
2. In your Mac terminal (or other shell), navigate to the 'songcatalog' directory.
3. Change directory into 'vagrant'
4. Run 'vagrant up'.  This will load the dependencies and create the virtual machine.
5. Once this is installed, type in 'vagrant ssh' to load the virtual environment.
6. Run 'cd /vagrant', then 'cd catalog'
7. Run 'python songpopulator.py' to generate the database the project will use.  It should notify you when complete.
8. Run 'python application.py' to get the localhost up and running on port :8000
9. In your browser go to the url 'localhost:8000' to view the page.
