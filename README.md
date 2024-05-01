# Arxiv Search and Summary Prototype

This is a prototype interface for a search and summary tool for arXiv papers. The tool allows users to search create and maintain a set of searches for papers by author, title or keyword and then select particular papers to generate a summary. 

## Usage
When running on a server, the user registers and id and password, logins in and is directed to a search page.

On the search page, all previous searches for the user id are listed, along with a 'New Search' button to create a search. Adjacent to exist existing search are button allowing updates to the search or to delete it.

### Acknowledgements
Code for login and resgistration is based on the Flask tutorial in the Flask documentation.
The search code is modeled after the blog posts code in the same tutorial.
