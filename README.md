# portfolio_tracker
simple app to track stock portfolio
The application has two parts:
1) Download daily data
The application downloads daily bhav files from BSE and NSE and updates a mysql data base with its pricing information.This part of the application is designed to run as a batch and should be scheduled as a cronjob or a scheduled task (in windows).
2) Visualize data
There is a small dashboard built using bokeh. This dashboard visualizes data from mysql. The stocks in the portfolio are read from the portfolio table. A lot of work can be done here e.g. this dashboard can be merged with a Django app...

The database scripts provide the table definition
