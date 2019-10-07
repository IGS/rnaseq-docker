#!/bin/bash

function print_usage {
    progname=`basename $0`
    cat << END
usage: $progname -i </path/to/input/dir> -p <HOST_IP>
END
    exit 1
}

# Resolve relative directory path
function abspath {
    if [[ -d "$1" ]]
    then
        pushd "$1" >/dev/null
        pwd
        popd >/dev/null
    else
        if [[ -e $1 ]]
        then
            echo "$1" needs to be a directory! >&2
        else
            echo "$1" does not exist! >&2
        fi
        exit 127
    fi
}

while getopts "i:p:" opt
do
    case $opt in
        i) input_source=$OPTARG;;
        p) ip_host=$OPTARG;;
    esac
done

if [ -z "$ip_host" ]; then
    echo "Setting IP to 'localhost'"
    ip_host="localhost"
fi

if [ -z "$input_source" ]; then
    echo "Must provide 'input_source' option."
    print_usage
fi

#########################
# MAIN
#########################

unamestr=`uname`
# Directory name of current script
if [[ "$unamestr" == 'Darwin' ]]; then
  DIR="$(dirname "$(stat -f "$0")")"
else
  DIR="$(dirname "$(readlink -f "$0")")"
fi

# Copy the template over to a production version of the docker-compose file
docker_compose_tmpl=${DIR}/docker_templates/docker-compose.yml.tmpl
docker_compose=${DIR}/docker-compose.yml
cp $docker_compose_tmpl $docker_compose

abs_input_source=$(abspath $input_source)

perl -i -pe "s|###INPUT_SOURCE###|$abs_input_source|" $docker_compose
perl -i -pe "s|###IP_HOST###|$ip_host|" $docker_compose

# Remove leftover template ### lines from compose file
perl -i -ne 'print unless /###/;' $docker_compose

# Default docker_templates/docker-compose.yml was written to so no need to specify -f
printf  "\nGoing to build and run the Docker containers now.....\n"
dc=`which docker-compose`
$dc up -d

printf  "Docker container is done building!\n"
printf  "In order to start using the Grotto UI, please point your browser to http://${ip_host}:5000\n"
printf  "To monitor pipelines, please point your browser to http://${ip_host}:8080/ergatis\n"

exit 0
