# Docker Machine notes

This document is tracking the process of running GROTTO on Amazon EC2 using Docker Machine to establish the "ec2" driver

Tutorial: <https://docs.docker.com/machine/examples/aws/>

## Setting up Docker Machine

* To create the virtual machine:
  * `docker-machine create --driver amazonec2 --amazonec2-open-port 5000 --amazonec2-open-port 8080 aws-sandbox`
  * "aws-sandbox" is the name of the machine created.
  * If you have a ~/.aws/credentials file, you do not need to specify options for the AWS access and secret keys
  * Other EC2 options -> <https://docs.docker.com/machine/drivers/aws/>
  * To get help run `docker-machine create --driver amazonec2 --help`
* List created machines with `docker-machine ls`
* You can ssh into the machine with `docker-machine ssh aws-sandbox`
  * User on the machine is "ubuntu" and Ubuntu 16.04 is the default AMI used.

## Running on the virtual machine

* After creating the machine run `eval $(docker-machine env aws-sandbox)` to source the environment variables for the current shell.
  * This is necessary before running a docker container, as any containers created will now be created in this virtual machine environment
* When running containers, you can `docker machine ssh <machine>` into the machine and run `sudo docker ps` to view the containers

## Running back on localhost

* To create containers on localhost instead of in the Docker Machine:
  * `eval $(docker-machine env -u)`
  * This unsets the environment variables created for the virtual machine

## Removing a Docker Machine

* To remove the virtual machine:
  * `docker-machine rm aws-sandbox` and select "y" to confirm the prompt

## Mounting a volume from EC2 to localhost

* The "sshfs" program must be installed since docker-machine relies on this to perform the mounting
  * Quick solution is to use `brew install sshfs` on Mac
* IMPORTANT - this method will not work internally, since port 22 is blocked on SOMEmp network when going from external to internal, which the 'sftp' command underneath is attempting to do.  Using `docker-machine scp` as an alternative
* <https://docs.docker.com/machine/reference/mount/>

## Copying files from localhost to EC2

* <https://docs.docker.com/machine/reference/scp/>
* Use `docker-machine scp -r <data_dir> aws-sandbox:/home/ubuntu/` to copy a directory over
* Potentially we can keep the data directory on the "aws-sandbox" side consistent, which reduces the potential for issues related to variations in directory paths

## Running Grotto

* `git clone https://github.com/IGS/rnaseq-docker.git`
* `sh launch_rnaseq.sh -i ~/bin/git/ergatis-docker-recipes/grotto_test_data/`
  * Grotto and Ergatis URLs are printed at bottom of output
  * The "-i" option is the location of your input data
  * This will launch a docker-machine (ec2-based) under the name "ec2\_grotto"
    * This step can take a bit of time to set up the machine
    * Currently I have it set by default to a "t3.medium" instance type"
  * The output of the script will let you know the IP address that Grotto will launch in
  * NOTE there is nothing in place to terminate this machine

## Things yet to do with the Grotto Docker stack

* Modify "launch\_rnaseq.sh" to have more robust checking
* Scaling up/down AWS instance type depending on data size
  * "Smartly" determine on our end, or have user pass in command-line option?
* Modify the "docker-compose.yml.tmpl" file to reflect new mounted paths on EC2 containers as the "host" portion
* Modify associated documentation (i.e. Github repo)