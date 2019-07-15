# Cortex Bot
Cortex Bot is a Mattermost integration that allowd you to query Cortex requests and run jobs directly from the Mattermost Interface. It is used by calling the ´/cortex´ command from Mattermost's chat window. 
# Features
With Cortex Bot you can:
 - Find all enabled analyzers
 - Find all enabled analyzers by data type
 - Find information on a specific enabled analyzer
 - Find all existing jobs
 - Find all existing jobs by data type or analyzer
 - Find information on a specific existing job
 - Get the report and artifacts of an existing job
 - Run a job by analyzer name (in which you can input the data type, data, tlp and cache bypassing parameter)
 - Run all jobs by specific data types
 
All this from your Mattermost instance!

# Required

- Apache HTTP Server (httpd)
- Python v3.5+
- mod_wsgi Python v3.5+
- Cortex4py (please refer to cortex4py [documentation](https://github.com/TheHive-Project/Cortex4py) for installation)

# Set Up

For the correct set up of Cortex Bot, it is crucial that httpd is installed and running. The scripts are written in python3 and communicate with Cortex instances via cortex4py. In order to execute the scripts from cgi, the python Apache Server module mod_wsgi is required. This will provide a WSGI inteface for Python and and allows the integration with cgi. Both cortex_bot.py and cortex_bot_helper.py should be placed in cgi-bin directory under /var/www/cgi-bin. Note that cortex_bot.py will need execute privileges. Once the aforementioned configurations and installations are done, proceed by placing both cortex_bot.py and cortex_bot_helper.py in the /var/www/cgi-bin directory. 

**Note**: cortex_bot.py will need execute privileges.



