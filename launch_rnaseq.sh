#!/bin/bash

function print_usage {
    progname=`basename $0`
    cat << END
usage: $progname -i </path/to/input/directory>
END
    exit 1
}

while getopts "i:" opt
do
    case $opt in
        i) input_source=$OPTARG;;
    esac
done

if [ -z "$input_source" ]; then
    echo "Must provide 'input_source' option."
    print_usage
fi

#########################
# MAIN
#########################

unamestr=$(uname)
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

# Create the docker-machine.  This assumes the user has AWS credentials at $HOME/.aws/credentials
printf "Now creating 'aws-grotto' Docker machine...\n"
$(docker-machine create --driver amazonec2 --amazonec2-instance-type t3.medium --amazonec2-ssh-keypath ~/.ssh/id_rsa --amazonec2-open-port 5000 --amazonec2-open-port 8080 aws-grotto)

# Source environment variables
eval $(docker-machine env aws-grotto)

# Copy input source data to the EC2 instance
printf "Now copying files to the machine\n"
$(docker-machine scp -r $input_source aws-grotto:/home/ubuntu/input_data)

ip_host=$(docker-machine ip aws-grotto)

perl -i -pe "s|###INPUT_SOURCE###|/home/ubuntu/input_data|" $docker_compose
perl -i -pe "s|###IP_HOST###|$ip_host|" $docker_compose

# Remove leftover template ### lines from compose file
perl -i -ne 'print unless /###/;' $docker_compose

# Default docker_templates/docker-compose.yml was written to so no need to specify -f
printf  "\nGoing to build and run the Docker containers now.....\n"
dc=$(which docker-compose)
$dc up -d

printf "Docker container is done building!\n"
printf "In order to start using the Grotto UI, please point your browser to http://${ip_host}:5000\n"
printf "To monitor pipelines, please point your browser to http://${ip_host}:8080/ergatis\n"

exit 0
