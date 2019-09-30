# Transcriptomics Pipeline README

This document aims to help you download Grotto and the RNASeq pipeline, and walks you through how to use Grotto on your personal computer.  

Keep in mind that this interface has only recently been developed and is still under active development.  If you have any questions, comments, or suggestions feel free to send an e-mail to Shaun Adkins (sadkins@som.umaryland.edu)

If you use Grotto in published research, please cite:

> Shetty, A.C., Adkins, R.S., Chatterjee, A., McCracken, C.L., Hodges, T., Creasy, H.H., Giglio, M., Mahurkar, A. and White, O. 2019. CAVERN: Computational and visualization environment for RNA-seq analyses. Presented at the 69th Annual Meeting of the American Society of Human Genetics, Houston, Texas.

## Requirements

The following tools are required in order to run Grotto;

* Docker (https://docs.docker.com/engine/installation/)
* docker-compose (https://docs.docker.com/compose/install/)
  * Typically Docker-Compose comes installed with Docker with more recent versions, but this is helpful if you find that is not the case.
* git (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Also it is worth noting that Grotto has only been tested in the Mac and Linux OS environments.  It may not work on a Windows environment.

### Special Note

Various transcriptomics datasets can be computationally intensive, meaning there is a possibility of running out of RAM to complete one or more intermediate tasks.  You can run `docker stats` to view resource usage in a live stream and `docker stats --no-stream` to view a snapshot of the resource usage.

The choice in starting dataset can also result in large intermediate files that may use up most, if not all, of the storage space either allocated for Docker or for your computer.  You can run `docker system df -v` to view the amount of storage that Docker is using.  If you are running Docker on a Mac, you can change the percent of total system storage that Docker can utilize by following the steps in this link (https://docs.docker.com/docker-for-mac/space/)

Remember, Docker allows for applications to be run anywhere that you can deploy Docker, but you have to use your own discretion regarding if your dataset(s) can actually be analyzed on your machine.

## Getting the RNAseq GitHub repository

The first step is to use 'git' to clone the "rnaseq-docker" GitHub repository, which houses information and scripts for the "rnaseq" Docker image.  For this example, the following will take place in the user's home directory, but the `git clone` command can be run in any directory, so long as you modify the directory paths for any future instructions to account for this.

```bash
cd ~
mkdir git; cd git
git clone https://github.com/IGS/rnaseq-docker.git
cd rnaseq-docker
```

### Setting up the input area

Next, the input area for the "rnaseq" Docker container to read from will need to be created.  For this example, we will create them in the home directory (~). The input directory will be mounted as a volume within the Docker container, so that the container can access it to read from.

NOTE:  This step is important, as the Ergatis pipeline will fail if the input\_data directory is not created beforehand.

```bash
mkdir ~/input_data
```

At this point you should now move or copy the pipeline input\_data to the "~/input\_data" directory.  Input data consists of *any files* that would be used in the pipeline.  This includes any potential FASTQ, BAM, counts, GFF3/GTF, and reference files.

## Start the Docker containers

Now it's time to start the Grotto and RNAseq Docker containers.  The following script will run docker-compose to set up both the Grotto and RNAseq containers.  This also mounts volumes from the local machine to the Docker container for passing in input data and for collecting output data.

NOTE: for the -i option, it is recommended to specify the full (absolute) path to ensure that Docker mounts the correct area.

NOTE: Before doing this step, make sure no other services are bound to ports 5000 or 8080 on your computer.  If other Docker containers are services are using those ports, either the Grotto site or the Ergatis site will not work.

```bash
cd ~/git/rnaseq-docker
sh launch_rnaseq.sh -i ~/input_data
```

The first time that launch\_rnaseq.sh is run should take a few minutes, as Docker needs to pull the various images down the Dockerhub repository.  Subsequent executions of the command should be much quicker.

Next, in your web browser, navigate to *localhost:5000* to bring up the Grotto UI.

### Small note before getting into it

Please do not hit the 'Back' button in the browser, as that can cause some unintended side effects.  If you make a mistake, there will be an 'edit' button for each section on the Summary page that will take you back to that section to make corrections.

## Once Grotto is up...

Follow the instructions (as per the workshop notes) to set up your pipeline noting the key differences.

* When filling out the text fields, you will need to point to the /mnt/input\_data location of the file, as that will be the location of the file within the "ergatis" Docker container.  So if your filepath is ~/input\_data/test.fsa, then it will need to filled in as /mnt/input\_data/test.fsa
* Uploaded files, such as the "sample info file", should have their FASTQ (or SAM/BAM) paths pointing to /mnt/input_data as well.  If submitting a SAM/BAM file (in cases where you already have alignments for samples but only want analyses), place that in the "File1" section and leave "File2" blank.
* On the 'Pipeline Options' page, the repository root needs to point to /opt/projects/rnaseq as this is where it is in the RNASeq docker image.  This should be pointed there by default so do not change it.

### Acquiring configuration files for future runs

On the Summary page, each section has a "Download" link that will create a "sample\_info" file or a "config form" file that can be uploaded on subsequent runs, which makes it easy to repeat samples or repeat conditions.  You can also download a "pipeline options" file but it currently cannot be uploaded at this time.

### After submitting the pipeline...

After the pipeline is made, the "Pipeline Status" page should appear.  This page, has a "Refresh" button that can be hit to get the current status of the pipeline and its components, but the page will automatically refresh every 60 seconds anyways.  There is also a "View Pipeline" link that will take the user to the pipeline in Ergatis.  When the pipeline is first created, it does not run automatically, so the user needs to first click "View Pipeline" to bring the pipeline up in Ergatis, and then hit the "Rerun" button to start it.

## Starting additional pipelines

In order to create additional pipelines in Grotto, the user must click the "Grotto" logo at the top of the page, which will navigate to the "Sample Info File" page again.  This clears all information stored about the previous pipeline, which allows for a new pipeline to be created.  The previous pipeline will still be accessible on the Ergatis page (localhost:8080) and still will be running if it currently is.

## Finding a recent pipeline

On any page in Grotto, there is a "Recent Pipelines" link that will let you view recently submitted pipelines.  After clicking that link, select the "Docker" project from the "Select a project" drop-down menu, and information on the 10 most recently submitted pipelines should appear.  Clicking "View" will naviagate to that pipeline's "Pipeline Status" page.

## Downloading pipeline data

On Grotto's "Pipeline Status" page, when a given pipeline status is shown as "complete", the "Create BDBag" button will be enabled (turn from gray to blue) either during the next automatic refresh, or when the user manually hits "Refresh Page".  Hitting this button will create a BDBag zip file containing various outputs from the pipeline.

When this step is completed, the "Generate Report" button will be enabled.  Clicking this button will generate various PDFs and report images related to the pipeline, and these will be added to the existing BDBag zipfile.

When either the "Create BDBag" or "Generate Report" steps finish and a BDBag zipfile is created, the option to download the BDBag object will be available by clicking the "Download Bag" button.

## Powering down the containers

When you have finished your pipelines, you can shut down the containers with the following commands:

```bash
cd ~/git/rnaseq-docker
docker-compose down -v
```
