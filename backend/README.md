# Backend files

## Aurin
### AURIN_environment:
the folder contains the JSON files downloaded from the AURIN platform, which are related to the topic of environment
### AURIN_health:
the folder contains the JSON files downloaded from the AURIN platform, which are related to the topic of health
### couchdb_functions.py
* It is a python file contains functions to do operations in CouchDB, including opening CouchDB, writing data into CouchDB. 
* It is used to write AURIN data to CouchDB.
### couchdb_info.json
contians CouchDB information required when logging in like HTTP addresses, username, and password.
### write_AURIN_couchdb.py
It's the main function to write AURIN data to CouchDB. The program will read all files within two folders containing environment and health data sequentially. After that, function will store each AURIN dataset to corresponding databases in CouchDB.



## Common files used :
### 1. token_and_query.json 
contains information:
* Twitter API information ("API_Key", "API_Key_Secret", "Access_Token", "Access_Token_Secret", "Bearer Token") of 2 Essential access and 2 Elevated access;    
* query sentences of topics for Twitter API version2 and Twitter API version1 respectively;
* common information used for both topics, including Cookie for Twitter API, CouchDB information (addresses, username and password), and keys for searching.

### 2. CouchDB_functions.py
* It is a python file contains functions to do operations in CouchDB, including opening CouchDB, writing data into CouchDB, collecting top ten user ids that posted the most related tweets, adding a view of database, and deleting a database.
* This file is used by the above three .py files to modify CouchDB.


              
## EssentialAPI_process_search+stream.py
Based on Twitter API v2 and Essential access, the file compiles recent search 7 days functions and stream functions simultaneously for two topics to store text information to CouchDB.

## ElevatedAPI_process_search+timeline.py  
The file has functions:
1. Based on Twitter API v1 and Elevated access, compile recent search 7 days functions for two topics simultaneously to store geographical information to CouchDB;
2. compile user timeline v2 functions for two topics to search related tweets of users that have posted the same kind of tweets recently;
3. and use scheduler tool to compile following user timeline v2 once a day and recent search v1 once a week.
     
## historical_tweets.py
* With the historical tweets file 'twitter-melb.json', the file reads records one by one and filter tweets information according to interested keywords in text. 
* Finally, it stores useful tweets with text information to CouchDB text database and useful tweets with coordinates information to CouchDB coordinates database.

