# Running the Grotto Transcriptomics Pipeline with test data

This document is designed to help the user run the Grotto pipeline with test data to ensure that everything is set up and working on the user's system.

## Starting the Docker containers

```bash
cd ~/git/rnaseq-docker
sh launch_rnaseq.sh -i ~/grotto_test_data
```

## Small note before getting into it
Please do not hit the 'Back' button in the browser, as that can cause some unintended side effects.  If you make a mistake, there will be an 'edit' button for each section on the Summary page that will take you back to that section to make corrections.

## Sample Info File page

Click "Choose File" and in the file navigation menu, select the file at <ergatis_docker_recipes/grotto_test_data/fastq_samples.info> and select Open.  The file name should appear in the text box.  Click "Upload" to auto-populate the sample fields.

Hit Next when ready.

## Pipeline Options page
Fill out the following fields.
* Reference
  * /mnt/input_data/reference/chr22_with_ERCC92.fa
* GFF3/GTF
  * /mnt/input_data/reference/chr22_with_ERCC92.gtf
* Annotation Format - GTF option

Select the following pipeline options:
* Alignment
* Visualization
* RPKM Analysis
* Differential Gene Expression
  * Comparison Groups - UHRvsHBR

## Config File Form page
Click "Choose File" and in the file navigation menu, select the file at <ergatis_docker_recipes/grotto_test_data/Euk_template.config> and select Open.  The file name should appear in the text box.  Click "Upload" to auto-populate the configuration parameters.

Hit Next when ready.

## Summary page
On this page, verify everything looks correct, and click Next

## Pipeline Status page
* The pipeline should automatically start
* Clicking 'View Pipeline' will take you to the Ergatis pipeline page in a new tab
* When the pipeline is complete, click "Create BDBag".  This will create a BDBag object of output data from the pipeline
* After this is created, you can either a) download the object with "Download Bag" or add reports to the BDBag object by clicking "Generate Report".  
  * Note that after clicking "Generate Report" the button will be disabled to prevent potential issues with data collision
  * After clicking "Generate Report", the "Download Bag" button will download a BDBag object with additional figures.

## Shutting down the Grotto services
```bash
cd ~/git/rnaseq-docker
docker-compose down -v
```