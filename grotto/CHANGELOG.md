# CHANGELOG

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