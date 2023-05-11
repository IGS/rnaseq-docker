# CHANGELOG

#v2.2
* Bump flask from 1.1.2 to 2.2.5 in /grotto (via @dependabot). This was done due to a high security vulnerability in Flask v1

#v2.1
* Removing code that was for internal use only.  This code only supports the Docker-based builds
* Moving this codebase from SVN to Github

#v2.0
* BDBag and report generator Perl scripts were rewritten in Python, so functions within can be directly imported
* Restructuring codebase to look more like a traditional Flask application

#v1.1
* Rewriting Dockerfile
  * Using Alpine-linux to reduce file size
  * Inheriting from Ergatis Docker image to reduce number of shared volumes
* Refactored some of the web code

#v1.0
* Initial release of Grotto
