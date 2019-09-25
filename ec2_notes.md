# Notes on operating the Grotto UI and RNAseq container on Amazon EC2

As a prerequisite, one must have a valid Amazon EC2 instance set up, along with any associated volumes.  Please refer to [this documentation](https://github.com/IGS/Chiron/blob/master/docs/amazon_aws_setup.md) for more information on how to do this.  Make sure that you create and attach a volume to your EC2 instance, and that all steps in "Final Steps" are followed.

Differences
* You may not have the proper security group to use with this instance, so you may have to create your own.  In security group settings open up Custom Rule TCP ports 5000 and 8080 to 0.0.0.0/0, and open up SSH port 22 to 0.0.0.0/0

## After EC2 instance is set up and user has SSH'ed into it...

The next step would be to clone this git repository into the EC2 instance.  You should currently be in the home directory as user 'ubuntu'

```
mkdir git; cd git
git clone https://github.com/IGS/rnaseq-docker.git
cd rnaseq-docker
```

### Setting up the input and output areas
Next create an input area to copy input files over to. This will take advantage of the attached volume from earlier (which should be mounted to /opt).  In addition, an output area directory will be created so that the pipeline "output\_repository" directory can mount here, making results easily accessible

```
mkdir /opt/input_data
mkdir -m 0777 /opt/output_repository
```

The area should now be ready for the user to 'scp' or 'rsync' files over.

### Install Docker Compose

By default Docker Compose is not installed on the EC2 instance.  To install, do the following command:
```
sudo apt install docker-compose
```

### Start the Docker containers

Now it's time to start the Grotto and RNAseq Docker containers.  The following script will run docker-compose to set up both the Grotto and RNAseq containers.  This also mounts volumes from the EC2 host to the Docker container for passing in input data and for collecting output data.

NOTE: for the -i and the -o options, make sure to specify the FULL PATH

```
cd ~/git/rnaseq_docker
sh launch_rnaseq.sh -i /opt/input_data -o /opt/output_repository -p "<EC2_IP>"
```

The first time that launch\_rnaseq.sh is run should take a few minutes, as Docker needs to pull the images down the Dockerhub repository.  Subsequent executions of the command should be much quicker.

Next, in your web browser, navigate to <EC2_IP>:5000 to bring up the Grotto UI.  Follow the instructions to set up your pipeline noting the key differences.
* When filling out the text fields, you will need to point to the /mnt/input\_data location of the file, as that will be the location of the file within the "ergatis" Docker container.  So if your file on the EC2 container is /opt/input\_data/test.fsa, then it will need to filled in as /mnt/input\_data/test.fsa
* Uploaded files, such as the "sample info file", should have their FASTQ paths pointing to /mnt/input\_data as well.
* On the 'Pipeline Options' page, the repository root needs to point to /opt/projects/rnaseq as this is where it is in the RNASeq docker image.  This should be pointed there by default.

After the pipeline is made, the "Pipeline Status" page should appear.  This page, has a "Refresh" button that can be hit to get the current status of the pipeline and its components.  There is also a "View Pipeline" link that will take the user to the pipeline in Ergatis.  When the pipeline is first created, it does not run automatically, so the user needs to first click "View Pipeline" to bring the pipeline up in Ergatis, and then hit the "Rerun" button to start it.

Pipeline output should be written to /opt/output\_repository.

### Starting additional pipelines

In order to create additional pipelines in Grotto, the user must click the "Grotto" logo at the top of the page, which will navigate to the "Sample Info File" page again.  This clears all information stored about the previous pipeline, which allows for a new pipeline to be created.  The previous pipeline will still be accessible on the Ergatis page (<EC2_IP>:8080)and still will be running if it currently is.

## Powering down the containers

When you have finished your pipelines, you can shut down the containers with the following commands:

```
cd ~/git/ergatis-docker-recipes/rnaseq
docker-compose -f docker_templates/docker-compose.yml down -v
```

Note that this will remove all the pipeline data that was created within the containers, so be sure to migrate the data you want before running these commands.  If you do not want the volume storing the pipeline output to be destroyed, remove the "-v" option from the docker-compose command.  However, do note that specifying this directory as the output source upon running "launch\_rnaseq.sh" for a second time can cause problems, such as overwriting of existing output files.

## To use more than 4 processes in a pipeline

Currently the "rnaseq" pipeline will only utilize 4 processors, since the Docker image was built to do that.  However, if your Amazon EC2 instance has more than 4 processes and you wish to utilize them, do the following.

```
cd ~/git/rnaseq-docker
docker build --no-cache -t adkinsrs/rnaseq .
```

This should take a few minutes.
