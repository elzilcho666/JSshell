JSshell
=======

Two way javascript communication

Originally built as a test bed for web application security classes at University,
I use this to explore and demonstrate the dangers of xss, csrf and cookie stealing.

File Listing
=======
shellserv.py - Twisted Web application written in Python 2.7, handles communication
between the admin web interface and injected sessions.

x.js - Javascript file that get injected, uses jQuery

web_adminUI/index.html - Admin web interface, send javascript payloads, receive replies. Uses jQuery

Usage
=======

JSshell only has one part of it facing the internet, the shellserv.py webapp, x.js connects to the web
app, registers its vital statistics and waits for commands from the webapp. This project uses asyncronous
long polling to maximize compatibility, preserve bandwidth and maintain stealth.

ToDO
=======
* Move away from jQuery to native JS or, create a jQuery bootstrapper that provides a jQuery environment
to the new code
* Sort out live status of connected sessions
* Find a more unique way of identify computer/browser instances without cooke rather than IP + " " + User Agent