# Form filling application

This template provides a flexible pattern for collecting form responses. 
The survey questions are stored in a dictionary instead of being directly included in the UI. 
The UI is generated based on that survey object which means that adding additional accordion_panels is as easy as adding another element to the dictionary. 

The applciation implements some basic data validation by only showing the submit button when all of the empty mandatory fields have been filled out.
When the user submits a form it is appended to a csv file. 