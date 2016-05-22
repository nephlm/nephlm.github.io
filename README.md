# demondice
WOD Demon (Fallen) dice probability calculator and roller.

This was built to solve the problem of having no idea what the basic probabilities of a WoD, specifically Demon: The Fallen, dice pool were.  The dice roller is thrown in gratis.

It uses a webpage as a ui and is a python 3.5.1 wsgi app developed on ubuntu 14.04.  If requirements.txt has been satisfied in your environment, you should be able to go to the ``<repo>/src`` directory and run `python app.py``

This will start the development webserver which should be accessible at ``http://localhost:5000``

The ui should be mobile friendly and can be used as a die roller while at the table.  If that's the case you might want to run the webserver in the cloud, which I haven't tried yet.

``src/wodDice.py`` contains all the dice rolling smarts if you want to make a command line tool or make your own ui.  Everything else is my own ui.  ``src/app.py`` is the flask app and specifies the api the front end uses.

Since no one else in th whole world will ever read this, that's about it.

