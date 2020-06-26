# utils.helpers.py

import os, sys, time
from collections import defaultdict, OrderedDict
from flask import current_app as app
from flask import session, flash
from flask_login import current_user
from . import pipeline as pipeline_util
from . import xml as xml_util
from .. import pipeline_components
from ..models import Pipeline

ALLOWED_EXTENSIONS = set(['config', 'info', 'txt'])

# set location of parent directory
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import generator scripts
sys.path.append(app.config['GENERATORS_DIR'])
import bdbag_generator, report_generator

def allowed_file(filename):
    """ Return true if extension is allowed """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def append_to_pipeline_flatfile(pipeline, sample_file, config_file):
    """ Append pipeline information to a flatfile """
    empty_file = True
    if os.path.isfile(app.config['PIPELINE_FLATFILE']):
        empty_file = False
    with open(app.config['PIPELINE_FLATFILE'], 'a+') as ff:
        if empty_file:
            row = "User\tProject\tRepo_Root\tPipeline_ID\tSample_Info\tConfig_File\tMapping_File\tEuk_or_Prok\tPipelineOpts"
            ff.write(row)
            ff.write("\n")
        pipeline_type = ""
        if session.get('pipeline_type'):
            if session.get('pipeline_type') == "Eukaryotic":
                pipeline_type = "Euk"
            else:
                pipeline_type = "Prok"
        else:
            app.log.error("Pipeline type was not saved in list of session variables")
        row = '\t'.join([
            current_user.get_id(),
            session['pipeline_options'].get('project_code'),
            session['pipeline_options'].get('repository_root'),
            pipeline.pipeline_id,
            sample_file,
            config_file,
            session.get('mapping_file'),
            pipeline_type,
            session.get('pipeline_options_string')
            ])
        ff.write(row)
        ff.write("\n")

def clear_submitted_pipeline_session_values():
    """ Clear a bunch of session values for the recently submitted pipeline """
    session.pop('edit_sif', None)
    session.pop('pipeline_options', None)
    session.pop('pipeline_options_string', None)
    session.pop('edit_po', None)
    session.pop('edit_sif', None)
    session.pop('edit_cff', None)
    session.pop('error_cell', None)
    session.pop('pipeline_type', None)
    session.pop('mapping_file', None)
    session.pop('required_fields', None)
    session.pop('uniq_file_prefix', None)
    session.pop('sample_info_file', None)
    session.pop('config_file', None)
    session.pop('pipeline_options_file', None)
    session.pop('sample_info_json', None)
    session.pop('localtime', None)
    session.pop('bdbag_zip', None)
    session.pop('reports_zip', None)

def create_bdbag(pipeline):
    """ Create and run command to create a bdbag object """
    #app.logger.debug(pipeline)
    pipe_id = pipeline['pipeline_id']
    ergatis_repository = os.path.join(xml_util.get_repository_root(pipeline["pipeline_xml"]), "output_repository")
    outfile_name = "{}_{}".format(pipeline_util.get_proj_code_from_id(pipe_id), pipe_id)
    output_dir = os.path.join(app.config["BDBAG_OUTPATH"], outfile_name)

    if 'pipeline_options' in pipeline and not pipeline['pipeline_options'] is None:
        if 'alignment' in pipeline['pipeline_options']:
            bdbag_generator.generate_fastqc_report(output_dir, ergatis_repository, pipeline['pipeline_id'])
            bdbag_generator.generate_alignment_report(output_dir, ergatis_repository, pipeline['pipeline_id'])
        if 'rpkm_analysis' in pipeline['pipeline_options'] or 'count' in pipeline['pipeline_options']:
            bdbag_generator.generate_ge_report(output_dir, ergatis_repository, pipeline['pipeline_id'])
        if 'differential_gene_expression' in pipeline['pipeline_options']:
            bdbag_generator.generate_de_report(output_dir, ergatis_repository, pipeline['pipeline_id'])
    else:
        # If 'pipeline options' is blank, just run all the commands
        bdbag_generator.generate_all_reports(output_dir, ergatis_repository, pipeline['pipeline_id'])

    # Create and archive the bag
    bdbag_zip = bdbag_generator.create_bag(output_dir, False)

    # Ensure .zip file was actually created
    if os.path.isfile(bdbag_zip):
            return bdbag_zip
    flash("BDBAG .zip file missing.  Check logs for BDBag command status.")
    return None

def create_config_hash_from_template(component_list, conf_file=None):
    """ Create a config hash to display in the config file form, based on a template """
    # If config file was not passed in, use one of the default templates
    if not conf_file:
        if session.get('pipeline_type') == 'Eukaryotic':
            conf_file = "Eukaryotic.RNASeq.pipeline.config"
        else:
            conf_file = "Prokaryotic.RNASeq.pipeline.config"

    result, required_fields = read_config_file(conf_file, component_list)
    session['required_fields'] = required_fields
    return result

def determine_components():
    """ Determine the components that should be included in the config file form page """
    component_list = set()
    component_sections = pipeline_components.COMPONENT_SECTIONS

    for key, val in component_sections.items():
        if session['pipeline_options'].get(key) == 'on':
            component_list.update(val)

    # Now to prune the list based on other pipeline options.
    if session['pipeline_options'].get('cufflinks_legacy') == 'on':
        component_list.difference_update(pipeline_components.CUFFLINKS_MODERN_COMPONENTS)
    else:
        component_list.difference_update(pipeline_components.CUFFLINKS_LEGACY_COMPONENTS)

    if session['pipeline_options'].get('use_ref_gtf') == 'on':
        component_list.difference_update(pipeline_components.REF_GTF_COMPONENTS)

    if session.get('pipeline_type') == 'Prokaryotic':
        component_list.difference_update(pipeline_components.HISAT_COMPONENTS)
        component_list.discard('tophat')
        # In addition, 'isoform_analysis' and 'differential_isoform_analysis' assumed to never be 'on'
    else:
        component_list.discard('bowtie')
        if session['pipeline_options'].get('tophat_legacy') == 'on':
            component_list.difference_update(pipeline_components.HISAT_COMPONENTS)
        else:
            component_list.difference_update(pipeline_components.TOPHAT_COMPONENTS)

    if session['pipeline_options'].get('count') == 'off' and session['pipeline_options'].get('alignment') == 'off':
        component_list.difference_update(pipeline_components.COUNT_OR_ALIGN_COMPONENTS)

    app.logger.debug(component_list)
    return component_list

def find_existing_bdbag_file(pipeline_id):
    """ If exists, find existing bdbag file and store to session. """
    location = app.config['BDBAG_OUTPATH']
    if not os.path.isdir(location):
        os.mkdir(location)
    for filename in os.listdir(location):
        if filename.endswith("_{}.zip".format(pipeline_id)):
            #app.logger.debug("Found BDBAG zipfile for id {}".format(pipeline_id))
            session['bdbag_zip'] = os.path.join(location, filename)
            return
    #app.logger.debug("No BDBAG file exists for id {}".format(pipeline_id))

def find_existing_reports_zip(pipeline_id):
    """ If exists, find existing "reports" bdbag file and store to session. """
    location = app.config['REPORTS_OUTPATH']
    if not os.path.isdir(location):
        os.mkdir(location)
    for filename in os.listdir(location):
        #app.logger.debug(filename)
        if filename.endswith("_{}.zip".format(pipeline_id)):
            #app.logger.debug("Found reports directory for id {}".format(pipeline_id))
            session['reports_zip'] = os.path.join(location, filename)
            return
    #app.logger.debug("No reports BDBAG for id {}".format(pipeline_id))

def freeze_localtime():
    """ Store localtime into session to use in naming files. """
    if not session.get('localtime'):
        if not session.get('edit_sif') or session.get('edit_sif') == 0:
            session['localtime'] = get_timestamp()
            app.logger.debug("localtime timestamp is {}".format(session.get('localtime')))

def generate_unique_filename(user_name, localtime):
    """ Generate file basename using username and localtime """
    return user_name + "_" + str(localtime)

def get_extra_pipeline_flatfile_info(pipeline_dict):
    """Given a pipeline dictionary, find the row in the flatfile and add extra information."""
    try:
        with open(app.config['PIPELINE_FLATFILE'], 'r') as ff:
            ff.readline()
            for line in ff:
                fields = line.rstrip().split()
                repo_root = fields[2]
                pipe_id = fields[3]
                pipeline_xml = "{}/workflow/runtime/pipeline/{}/pipeline.xml".format(repo_root, pipe_id)
                # Ensure passed in XML equals current row's XML
                if not pipeline_dict['pipeline_xml'] == pipeline_xml:
                    continue

                # Initial internal flatfile is potentially missing fields 4 and after
                try:
                    sample_info = fields[4]
                except IndexError:
                    sample_info = None

                try:
                    config_file = fields[5]
                except IndexError:
                    config_file = None

                try:
                    mapping_file = fields[6]
                except IndexError:
                    mapping_file = None
                if mapping_file == "NA":
                    mapping_file = None

                try:
                    euk_or_prok = fields[7]
                except IndexError:
                    euk_or_prok = None

                try:
                    pipeline_options = fields[8]
                except IndexError:
                    pipeline_options = None

                pipeline_dict['sample_info'] = sample_info
                pipeline_dict['config_file'] = config_file
                pipeline_dict['mapping_file'] = mapping_file
                pipeline_dict['pipeline_type'] = euk_or_prok
                pipeline_dict["pipeline_options"] = pipeline_options.split(";")
                return
    except IOError as e:
        err = "File that stores pipeline information could not be read.  Perhaps the " \
            "filepath is incorrect or there are permissions issues."
        app.logger.error(err)
        app.logger.error(e)
        app.logger.error(sys.exc_info()[0])

def get_timestamp():
    """ Get localtime timestamp """
    return str(time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time())))

def handle_create_pipeline_subprocess(proc):
    """ Ensure the 'create_rnaseq_pipeline' script was successful """
    error = None
    if proc.stderr:
        line = proc.stderr.readline()
        line = line.rstrip()
        if line:
            error = line
            app.logger.error("Error from process is: " + error)

    if error is None:
        if proc.stdout:
            pipeline_id = None

            # RNASeq pipeline command typically has multiple lines of output
            for line in proc.stdout:
                line = line.rstrip()
                app.logger.debug(line)
                if line.startswith('pipeline_id -> '):
                    # Parse out pipeline ID and URL
                    pipeline_id = pipeline_util.parse_id_from_pipeline_launcher(line)
                    pipeline_url = pipeline_util.parse_url_from_pipeline_launcher(line)

                    #now = datetime.datetime.now()
                    #now = unicode(str(now.replace(microsecond=0)
                    #app.logger.debug("Time is now : " + now)

                    pipeline_xml = pipeline_util.parse_xml_from_url(pipeline_url)
                    app.logger.debug("ID is: " + pipeline_id +
                                    "\nView URL is: " + pipeline_url +
                                    "\nXML is " + pipeline_xml)

                    pipeline = Pipeline(pipeline_id, pipeline_xml, pipeline_url, "Pending", None, None, None)
                    return pipeline

            # If there is any error, then return to 'submit' page
            if not pipeline_id:
                error = "Could not find pipeline ID for launched pipeline. Please notify the system administrator.\n Error: " + error
        else:
            error = "Something went wrong, but no error has been reported. Please notify the system administrator.\n Error: " + error
    else:
        error = "Something went wrong while submitting the pipeline: Error: " + error

    # Will hit here if any errors occured
    flash(error)
    app.logger.error(error)

def make_pipeline_report(pipeline):
    """ Make pipeline report using make_report.pl """

    # Cannot proceed without a BDBag zip file
    outfile_base = ''
    if session.get('bdbag_zip'):
        (before, sep, after) = session.get('bdbag_zip').rpartition('.zip')
        outfile_base = os.path.basename(before)
    else:
        app.logger.error("No BDBAG Zip file for this pipeline saved in sessions dict")
        flash("Cannot find BDBag file.  Something is wrong!")
        return False

    # Need sample info file to create comparison PDFs
    if pipeline["sample_info"] is None:
        app.logger.error("Sample info file parameter is missing so cannot create PDFs in make_report.pl")
        flash("Cannot generate PDFs")
        return False

    # Get extracted data directory path from original BDBag
    extracted_path = report_generator.extract_bag(session.get('bdbag_zip'))

    wrappers_dir = os.path.join(app.config["GENERATORS_DIR"], "wrappers")

    # Generate additional reports in the extracted bdbag directory
    if 'pipeline_options' in pipeline and not pipeline['pipeline_options'] is None:
        if 'alignment' in pipeline['pipeline_options']:
            wrapper_script = os.path.join(wrappers_dir, "wrapper_FastQC.R")
            report_generator.generate_fastqc_report(extracted_path, wrapper_script, outfile_base, pipeline['sample_info'])
            # Alignment reports differ for Proks and Euks
            wrapper_script = os.path.join(wrappers_dir, "wrapper_Alignment.R")
            if pipeline['pipeline_type'] == "Prok":
                wrapper_script = os.path.join(wrappers_dir, "wrapper_Alignment_prok.R")
            report_generator.generate_alignment_report(extracted_path, wrapper_script, outfile_base, pipeline['sample_info'])
        if 'count' in pipeline['pipeline_options']: # RPKM reports are not generated, only HTSeq count reports
            if pipeline['mapping_file'] is None:
                wrapper_script = os.path.join(wrappers_dir, "wrapper_GE.R")
                report_generator.generate_ge_report(extracted_path, wrapper_script, outfile_base, pipeline['sample_info'])
            else:
                wrapper_script = os.path.join(wrappers_dir, "wrapper_GE_mapping.R")
                report_generator.map_to_GE(extracted_path, wrapper_script, outfile_base, pipeline['sample_info'], pipeline['mapping_file'])
        if 'differential_gene_expression' in pipeline['pipeline_options']:
            if pipeline['mapping_file'] is None:
                wrapper_script = os.path.join(wrappers_dir, "wrapper_DE.R")
                report_generator.generate_de_report(extracted_path, wrapper_script, outfile_base, pipeline['sample_info'])
            else:
                wrapper_script = os.path.join(wrappers_dir, "wrapper_DE_mapping.R")
                report_generator.map_to_DE(extracted_path, wrapper_script, outfile_base, pipeline['sample_info'], pipeline['mapping_file'])
    else:
        # If 'pipeline options' is blank, just run all the commands
        report_generator.generate_all_reports(extracted_path, wrappers_dir, outfile_base, pipeline['sample_info'])

    # Construct the name of the expected zip file and update the bag
    # Create a temporary directory to create the reports BDBag
    #reports_dir = tempfile.mkdtemp(prefix="{}-".format(outfile_base), dir=app.config["REPORTS_OUTPATH"])
    #os.chmod(reports_dir, 0o777)

    reports_zip = report_generator.update_bag(extracted_path)

    # Ensure .zip file was actually created
    if os.path.isfile(reports_zip):
        ln_zip = os.path.join(app.config["REPORTS_OUTPATH"], "{}.zip".format(outfile_base))
        # If symlink exists in base reports out-directory, remove symlink.  Symlink newest zip file to base directory.
        try:
            os.unlink(ln_zip)
        except OSError:
            pass
        app.logger.debug("Symlinking from {} to {}".format(reports_zip, ln_zip))
        os.symlink(reports_zip, ln_zip)
        return ln_zip
    flash("Reports successfully generated but .zip file missing.")
    return None

def normalize_cmp_groups(cmp_groups):
    """ Normalize comparison groups string. Right now it's just removing spaces. """
    return cmp_groups.replace(' ', '').rstrip()

def parse_pipeline_options_flags():
    """ Build pipeline cmd options based on the selected options in the web page """

    no_align = False
    comp_groups = False

    cmd_args = []

    if session['pipeline_options'].get('build_indexes') == 'on':
        cmd_args.append("--build_indexes")

    if session['pipeline_options'].get('quality_stats') == 'on':
        cmd_args.append("--quality_stats")

    if session['pipeline_options'].get('quality_trimming') == 'on':
        cmd_args.append("--quality_trimming")

    if session['pipeline_options'].get('alignment') == 'on':
        if session['pipeline_options'].get('build_indexes') == 'off':
            cmd_args.append("--split")
            cmd_args.append("--idxfile=" + session['pipeline_options'].get('index_file'))
        cmd_args.append("--alignment")

    if session['pipeline_options'].get('visualization') == 'on':
        cmd_args.append("--visualization")
        if session['pipeline_options'].get('alignment') == 'off':
            no_align = True

    if session['pipeline_options'].get('rpkm_analysis') == 'on':
        cmd_args.append("--rpkm_analysis")
        if session['pipeline_options'].get('alignment') == 'off':
            no_align = True

    if session['pipeline_options'].get('differential_gene_expression') == 'on':
        cmd_args.append("--diff_gene_expr")
        comp_groups = True
        if session['pipeline_options'].get('alignment') == 'off':
            no_align = True
        if session['pipeline_options'].get('count') == 'on':
            cmd_args.append("--count")

    if session.get('pipeline_type') == 'Eukaryotic':
        if session['pipeline_options'].get('tophat_legacy') == 'on':
            cmd_args.append("--tophat_legacy")
        if session['pipeline_options'].get('cufflinks_legacy') == 'on':
            cmd_args.append("--cufflinks_legacy")

        if session['pipeline_options'].get('isoform_analysis') == 'on':
            cmd_args.append("--isoform_analysis")
            if session['pipeline_options'].get('alignment') == 'off':
                no_align = True
            if session['pipeline_options'].get('include_novel') == 'on':
                cmd_args.append("--include_novel")

        if session['pipeline_options'].get('differential_isoform_analysis') == 'on':
            cmd_args.append("--diff_isoform_analysis")
            comp_groups = True
            if session['pipeline_options'].get('alignment') == 'off':
                no_align = True
            if session['pipeline_options'].get('use_ref_gtf') == 'on':
                cmd_args.append("--use_ref_gtf")

    if comp_groups:
        cmd_args.append("--comparison_groups=" + session['pipeline_options'].get('comparison_groups'))

    if no_align:
        cmd_args.append("--file_type=" + session['pipeline_options'].get('file_type'))
        cmd_args.append("--sorted=" + session['pipeline_options'].get('sorted'))

    return cmd_args

def read_config_file(file_name, component_list=None):
    """ Read a pipeline template config file and store into a data structure """

    result = OrderedDict()
    # Using a default dict to avoid missing key issues
    section = defaultdict(dict)
    component = ''
    required_fields = []
    component_info = pipeline_components.ACCORDION_INFO
    i = 0

    with open(os.path.join(PARENT_DIR, file_name)) as config_file:
        for line in config_file:
            # It is a section
            if line.startswith('['):
                if component:
                    result[component] = section
                    # Components in template config not in component_info will be deleted later
                    if component in component_info:
                        # Should always have at least one index.  Store header title name
                        result[component][str(0)]['title'] = component_info[component]['title']
                        result[component][str(0)]['description'] = component_info[component]['description']
                        result[component][str(0)]['color'] = "circle-{}".format(component_info[component]['color'])

                    section = defaultdict(dict)
                    i = 0
                component = line.strip()
                component = component[1:len(component)-1]

            # It is a comment.  Comments are optional
            elif line.startswith(';;'):
                comment = line.strip(';;')
                comment = comment.strip()
                if 'comment' in section[str(i)]:
                    section[str(i)]['comment'] += comment
                else:
                    section[str(i)]['comment'] = comment

            # It is a key/value pair
            elif line.startswith('$;') or line.startswith('*$;'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key.startswith('*'):
                    key = key[1:].strip('$;')
                    required_fields.append([component, key])
                    section[str(i)]['required'] = True
                else:
                    key = key.strip('$;')
                    section[str(i)]['required'] = False
                section[str(i)]['key'] = key
                section[str(i)]['value'] = value
                i += 1

        result[component] = section
        # Should always have at least one index.  Store header title name
        try:
            result[component][str(0)]['title'] = component_info[component]['title']
            result[component][str(0)]['description'] = component_info[component]['description']
            result[component][str(0)]['color'] = "circle-{}".format(component_info[component]['color'])
        except KeyError as e:
            flash("Config file passed appears to be invalid or formatted incorrectly.")
            result = None

    if component_list:
        try:
            # Now to delete irrelevent sections based on the list of components we need
            for component in list(result.keys()):
                if component not in component_list:
                    del result[component]
            # Dangerous to delete off list while iterating so just append hits to new list
            final_req_fields = [field for field in required_fields if field[0] in component_list]
            required_fields = final_req_fields
        except AttributeError as e:
            required_fields = ""

    return result, required_fields

def remove_temp_files():
    app.logger.debug("Removing temp.config and temp.info from app directory")
    for file in ["config_file", "sample_info_file"]:
        try:
            os.remove(session.get(file))
        except OSError:
            pass
        try:
            os.remove(session.get(file))
        except OSError:
            pass
    # TODO: potentially remove /static/tmp tempfiles as well (though may be nice to have for debugging)

def unix_readable(field):
    """ If string has invalid UNIX chars, then return False """
    if field:
        return True
    for char in field:
        if not str.isalnum(str(char)):
            if not (char == '_' or char == '/' or char == '.' or char == '-'):
                return False
    return True

def validate_mapping_file(filename):
    """If mapping file was provided, ensure the filepath is valid."""
    if filename:
        if not os.path.isfile(filename):
            flask("'{}' mapping file path does not exist.".format(filename))
            return False
    return True

def validate_param_file(filename, param):
    """Ensure parameter has a valid file."""
    if filename == '':
        flash("'{}' field cannot be left empty.".format(param))
        return False
    elif not os.path.isfile(filename):
        flash("'{}' file path does not exist.".format(param))
        return False
    return True

def validate_repo_root(repo_root):
    """Ensure repository root area has been created and is valid."""
    if repo_root == '':
        flash("'Repository Root' field cannot be left empty.")
        return False
    elif not os.path.isdir(repo_root):
        flash("'Repository Root' directory does not exist.")
        ergatis_url = current_app.config['ERGATIS_URL']
        if os.getenv('DOCKER_HOST'):
            ergatis_url = 'http://{}:8080/ergatis/cgi'.format(os.getenv('DOCKER_HOST'))
        flash("Go to {}/create_project.cgi to create a valid repository root.".format(ergatis_url))
        return False
    return True

def write_pipeline_options(result):
    """ Store chosen pipeline options into a file """
    pipeopts = session.get("uniq_file_prefix") + ".pipeline_options.txt"
    session["pipeline_options_file"] = os.path.join(PARENT_DIR, "static/tmp", pipeopts)

    # TODO: Rewrite to allow it to be reused

    with open(session.get("pipeline_options_file"), 'w') as pipe_fh:
        pipe_fh.write('Reference\t' + str(result['reference']) + '\n')
        pipe_fh.write('GTF\t' + str(result['gtf']) + '\n')
        pipe_fh.write('Repository Root\t' + str(result['repository_root']) + '\n')
        pipe_fh.write('Project Code\t' + str(result['project_code']) + '\n')
        pipe_fh.write('Mapping File\t' + str(result['mapping_file']) + '\n')

        pipe_fh.write('Annotation Format\t' + str(result['annotation_format']) + '\n')
        if 'tophat_legacy' in result and str(result['tophat_legacy']) == 'on':
            pipe_fh.write('Legacy Tophat Pipeline\t' + '\n')
        if 'cufflinks_legacy' in result and str(result['cufflinks_legacy']) == 'on':
            pipe_fh.write('Legacy Cufflinks Pipeline\t' + '\n')
        if 'build_indexes' in result and str(result['build_indexes']) == 'on':
            pipe_fh.write('Build Indexes\t' + '\n')
        if 'quality_stats' in result and str(result['quality_stats']) == 'on':
            pipe_fh.write('Quality Stats\t' + '\n')
        if 'quality_trimming' in result and str(result['quality_trimming']) == 'on':
            pipe_fh.write('Quality Trimming\t' + '\n')
        if 'alignment' in result and str(result['alignment']) == 'on':
            pipe_fh.write('Alignment\t' + '\n')
        if 'visualization' in result and str(result['visualization']) == 'on':
            pipe_fh.write('Visualization\t' + '\n')
        if 'rpkm_analysis' in result and str(result['rpkm_analysis']) == 'on':
            pipe_fh.write('RPKM Analysis\t' + '\n')
        if 'differential_gene_expression' in result and str(result['differential_gene_expression']) == 'on':
            pipe_fh.write('Differential Gene Expression\t' + '\n')
            if 'alignment' in result and str(result['alignment']) == 'off':
                if 'count' in result and str(result['count']) == 'on':
                    pipe_fh.write('Count\t' + '\n')
        if 'isoform_analysis' in result and str(result['isoform_analysis']) == 'on':
            pipe_fh.write('Isoform Analysis\t' + '\n')
            if 'include_novel' in result and str(result['include_novel']) == 'on':
                pipe_fh.write('Include Novel\t' + '\n')
        if 'differential_isoform_analysis' in result and str(result['differential_isoform_analysis']) == 'on':
            pipe_fh.write('Differential Isoform Analysis\t' + '\n')
            if 'use_ref_gtf' in result and str(result['use_ref_gtf']) == 'on':
                pipe_fh.write('Use reference GTF/GFF3 in Cuffdiff\t' + '\n')

        if 'build_indexes' in result and str(result['build_indexes']) == 'off':
            if 'index_file' in result and str(result['index_file']) != '':
                pipe_fh.write('Reference Index File\t' + str(result['index_file']) + '\n')

        if 'alignment' in result and str(result['alignment']) == 'off':
            if 'file_type' in result and str(result['file_type']) != '':
                pipe_fh.write('File Type\t' + str(result['file_type']) + '\n')
            if 'sorted' in result and str(result['sorted']) != '':
                pipe_fh.write('Sorted\t' + str(result['sorted']) + '\n')

        if 'comparison_groups' in result and str(result['comparison_groups']) != '':
            pipe_fh.write('Comparison Groups\t' + str(result['comparison_groups']) + '\n')
