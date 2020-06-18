#!/usr/bin/python3

# Module Imports
import os
import sys
import shutil
from logging.handlers import RotatingFileHandler
import subprocess
from flask import Blueprint, render_template, redirect, request, flash, url_for, send_from_directory, session
from flask import current_app as app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from .models import SIF_entry
from .utils import helpers
from .utils import pipeline as pipeline_util
from .utils import xml as xml_util

# Blueprint Configuration
main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

# set location of current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@main_bp.route("/site_status")
def site_status():
    """ Is site up?"""
    return "OK"

@main_bp.route('/')
def index():
    """ Remove existing temporary config file and redirect to the sample_info page"""
    app.logger.debug('Clearing session variables')
    session.clear()
    return redirect(url_for('auth_bp.login'))

@main_bp.route('/help')
def help():
    return render_template('help.html')

@main_bp.route('/sample_info_file', methods=['GET', 'POST'])
@login_required
def sample_info_file():
    """ Handles various ways to create the sample_info_file, and also performs validation """

    if not session.get("uniq_file_prefix"):
        helpers.freeze_localtime()
        session["uniq_file_prefix"] = helpers.generate_unique_filename(current_user.get_id(), session.get('localtime'))

    if request.method == 'POST':
        result = []
        app.logger.debug('Collecting data for Sample Info File')
        error = []
        error_cell = []
        session.pop('error_cell', None)
        curr_row = 1
        row_index = 1
        sample_id_list = []

        # If pre-made sample_info file was uploaded, parse and validate
        if 'Upload' in request.form:
            # Is there an uploaded file in the POST request?
            if 'sif_browse' not in request.files:
                flash('No file property in the POST request')
                return render_template('sample_info_file.html', result=[SIF_entry(1, '', '', '', '')])
            _sif_base = request.files['sif_browse']

            # Is the filename empty?
            if _sif_base.filename == '':
                flash("No selected file.")
                return render_template('sample_info_file.html', result=[SIF_entry(1, '', '', '', '')])

            # Is the filename UNIX-readable?
            if not helpers.unix_readable(_sif_base.filename):
                flash("The location of the sample info file entered is not UNIX readable.")
                return render_template('sample_info_file.html', result=[SIF_entry(1, '', '', '', '')])

            # is the text extension allowed?
            if _sif_base and not helpers.allowed_file(_sif_base.filename):
                flash("Extension is not an allowed extension")
                return render_template('sample_info_file.html', result=[SIF_entry(1, '', '', '', '')])
            else:
                filename = secure_filename(_sif_base.filename)
                _sif_base.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                _sif_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Now ready to parse uploaded sample info file
            with open(_sif_location) as sif:
                for line in sif:
                    # Skip comments
                    if line.startswith('#'):
                        continue
                    values = line.split()
                    #flash(values)
                    # It's possible for the user to pass in just 1 file.
                    if len(values) < 4:
                        values.append('')
                    try:
                        data = SIF_entry(row_index, values[0], values[1], values[2], values[3])
                    except Exception as e:
                        err = "Uploaded sample info file must have either 3 columns or 4 columns."
                        app.logger.error(err)
                        app.logger.error(e)
                        app.logger.error(sys.exc_info()[0])
                        flash(err)
                        return render_template('sample_info_file.html', result=[SIF_entry(1, '', '', '', '')])
                    result.append(data.serialize())

                    row_index += 1
            return render_template('sample_info_file.html', result=result)
        # End 'Upload' if

        # Validate each existing row of sample_info
        while True:
            _sample_id = str(request.form['input_r'+str(curr_row)+'_sample_id'])
            _group_id = str(request.form['input_r'+str(curr_row)+'_group_id'])
            _file_1 = str(request.form['input_r'+str(curr_row)+'_file_1'])
            _file_2 = str(request.form['input_r'+str(curr_row)+'_file_2'])
            data = SIF_entry(curr_row, _sample_id, _group_id, _file_1, _file_2)
            result.append(data.serialize())

            sample_fields = {
                "Sample ID": {"label":"_sample_id", "result":_sample_id},
                "Group ID":{"label":"_group_id", "result":_group_id},
                "File 1":{"label":"_file_1", "result":_file_1},
                "File_2":{"label":"_file_2", "result":_file_2},
            }

            for key, val in sample_fields.items():
                # Check of each filed is UNIX readable
                if not helpers.unix_readable(val):
                    error.append('Row ' + str(curr_row) + ': ' + key + ' value "' +
                                val["result"] + '" entered in row '+str(curr_row)+' is not UNIX readable.')
                    error_cell.append('input_r'+str(curr_row) + val["label"])

            # Check if all required field are non-empty
            for key in ["Sample ID", "Group ID", "File 1"]:
                if sample_fields[key]["result"] == '':
                    error.append('Row ' + str(curr_row) + ': ' + key + ' is required.')
                    error_cell.append('input_r'+str(curr_row) + sample_fields[key]["label"])

            # Chcek if each sample id is unique within the submission
            if _sample_id in sample_id_list:
                error.append('Sample Id value \''+_sample_id+'\' entered in row '+str(curr_row)+' is already present.')
                error_cell.append('input_r'+str(curr_row)+'_sample_id')
            else:
                sample_id_list.append(_sample_id)

            # Continue if more rows are found or else break
            key = 'input_r'+str(curr_row+1)
            # flash(key)
            if key in request.form:
                curr_row = curr_row + 1
            else:
                break
        # End of While

        # No error occured. go to next page
        session['sample_info_json'] = result
        if error:
            for e in error:
                flash(e)
            session['error_cell'] = error_cell
            return render_template('sample_info_file.html', result=session.get('sample_info_json'))
        else:
            session.pop('error_cell', None)

        # flash(result)
        temp_info = session.get("uniq_file_prefix") + ".temp.info"
        session['sample_info_file'] = os.path.join(CURRENT_DIR, temp_info)

        # Write tmp sample_info file
        with open(session.get('sample_info_file'), 'w') as sample_fh:
            for elem in result:
                sample_fh.write(elem['sample_id']+'\t'+elem['group_id']+'\t'+elem['file_1'])
                if not elem['file_2']:
                    sample_fh.write('\n')
                else:
                    sample_fh.write('\t'+elem['file_2']+'\n')

        if 'edit_sif' not in session:
            session['edit_sif'] = 0
        if session.get('edit_sif') == 1:
            return redirect(url_for('main_bp.submit'))
        return redirect(url_for('main_bp.pipeline_options'))

    if 'edit_sif' in session and session.get('edit_sif') == 1:
        return render_template('sample_info_file.html', result=session.get('sample_info_json'))
    return render_template('sample_info_file.html', result=[SIF_entry(1, '', '', '', '')])

@main_bp.route('/pipeline_options', methods=['GET', 'POST'])
@login_required
def pipeline_options():
    """ Choose with portions of the pipeline to run.  Also fill in associated information. """

    if request.method == 'POST':
        app.logger.debug("In /pipeline_options - POST")
        result = dict()

        session['pipeline_type'] = 'Prokaryotic' if 'pipeline_type' in request.form else 'Eukaryotic'

        _reference = str(request.form['reference'])
        _gtf = str(request.form['gtf'])
        _mapping_file = str(request.form['mapping_file'])
        _repository_root = str(request.form['repository_root'])
        _project_code = str(request.form['project_code'])
        _annotation_format = request.form['annotation_format']
        _tophat_legacy = 'on' if 'use_tophat' in request.form else 'off'
        _build_indexes = 'on' if 'build_indexes' in request.form else 'off'
        _quality_stats = 'on' if 'quality_stats' in request.form else 'off'
        _quality_trimming = 'on' if 'quality_trimming' in request.form else 'off'
        _alignment = 'on' if 'alignment' in request.form else 'off'
        _visualization = 'on' if 'visualization' in request.form else 'off'
        _rpkm_analysis = 'on' if 'rpkm_analysis' in request.form else 'off'
        _differential_isoform_analysis = 'on' if 'differential_isoform_analysis' in request.form else 'off'
        if 'differential_gene_expression' in request.form:
            _differential_gene_expression = 'on'
            _count = 'on' if 'count' in request.form else 'off'
        else:
            _differential_gene_expression = 'off'
            _count = 'off'

        if 'isoform_analysis' in request.form:
            _isoform_analysis = 'on'
            _include_novel = 'on' if 'include_novel' in request.form else 'off'
        else:
            _isoform_analysis = 'off'
            _include_novel = 'off'

        if 'differential_isoform_analysis' in request.form:
            _use_ref_gtf = 'on' if 'use_ref_gtf' in request.form else 'off'
            _cufflinks_legacy = 'on' if 'old_cufflinks' in request.form else 'off'
        else:
            _use_ref_gtf = 'off'
            _cufflinks_legacy = 'off'

        _index_file = str(request.form['index_file'])

        result['reference'] = _reference.rstrip()
        result['gtf'] = _gtf.rstrip()
        result['mapping_file'] = _mapping_file.rstrip()
        #result['repository_root'] = _repository_root.rstrip()
        result['project_code'] = _project_code.rstrip()
        result['annotation_format'] = _annotation_format
        result['tophat_legacy'] = _tophat_legacy
        result['build_indexes'] = _build_indexes
        result['quality_stats'] = _quality_stats
        result['quality_trimming'] = _quality_trimming
        result['alignment'] = _alignment
        result['visualization'] = _visualization
        result['rpkm_analysis'] = _rpkm_analysis

        result['differential_gene_expression'] = _differential_gene_expression
        result['count'] = _count

        result['isoform_analysis'] = _isoform_analysis
        result['include_novel'] = _include_novel

        result['use_ref_gtf'] = _use_ref_gtf
        result['cufflinks_legacy'] = _cufflinks_legacy
        result['differential_isoform_analysis'] = _differential_isoform_analysis

        result['index_file'] = _index_file

        result['comparison_groups'] = str(request.form['comparison_groups1'])
        result['comparison_groups'] = helpers.normalize_cmp_groups(result['comparison_groups'])

        result['file_type'] = str(request.form['file_type1'])
        result['sorted'] = str(request.form['sorted1'])

        session['pipeline_options'] = result
        if app.config['DOCKER']:
            session['pipeline_options']['repository_root'] = "/opt/projects/repository"

        # If no mapping file was provided, make it a default value
        if not len(session['pipeline_options'].get('mapping_file')):
            session['mapping_file'] = "NA"

        if not helpers.validate_param_file(_reference, "Reference") \
            or not helpers.validate_param_file(_gtf, "GTF") \
            or not helpers.validate_mapping_file(_mapping_file) \
            or not helpers.validate_repo_root(_repository_root):
            return render_template('pipeline_options.html')

        if _project_code == '':
            _project_code = 'unknown'

        if _build_indexes == 'off' \
            and _alignment == 'off' \
            and _visualization == 'off' \
            and _rpkm_analysis == 'off' \
            and _differential_gene_expression == 'off' \
            and _isoform_analysis == 'off' \
            and _differential_isoform_analysis == 'off':
            flash('At least one pipeline processing option needs to be selected')
            return render_template('pipeline_options.html')

        if _build_indexes == 'off' \
            and _alignment == 'on' \
            and _index_file == '':
            flash("'Reference Index File' is required.")
            return render_template('pipeline_options.html')

        if (_differential_gene_expression == 'on' or _differential_isoform_analysis == 'on') \
            and result['comparison_groups'] == '':
            flash('Comparison Group filed required.')
            return render_template('pipeline_options.html')

        session.setdefault('edit_po', 0)

        helpers.write_pipeline_options(result)
        return redirect(url_for('main_bp.config_file_form'))

    return render_template('pipeline_options.html')

@main_bp.route('/config_file_form', methods=['GET', 'POST'])
@login_required
def config_file_form():
    """ Handles the various routes through setting up the config file """

    if not session.get('pipeline_options'):
        app.logger.error("Pipeline options have not been set upon 'config_file_form' page upload. " +
                        "Was the 'Back' button hit?")

    component_list = helpers.determine_components()

    if request.method == 'POST':
        app.logger.debug('In /config_file_form - POST')

        temp_config = session.get("uniq_file_prefix") + ".temp.config"
        session["config_file"] = os.path.join(CURRENT_DIR, temp_config)

        ### 1) If pre-made config file was uploaded, parse and validate
        if 'Upload' in request.form:
            app.logger.debug("Have chosen to upload a file")

            failed_load = False
            # Is there an uploaded file in the POST request?
            if 'cff_browse' not in request.files:
                flash('No file property in the POST request')
                result = helpers.create_config_hash_from_template(component_list)
                return render_template('config_file_form.html', result=result)
            _cff_base = request.files['cff_browse']

            # Is the filename empty?
            if _cff_base.filename == '':
                flash("No selected file.")
                failed_load = True

            # Is the filename UNIX-readable?
            if not helpers.unix_readable(_cff_base.filename):
                flash("The location of the config info file entered is not UNIX readable.")
                failed_load = True

            # is the text extension allowed?
            if _cff_base and not helpers.allowed_file(_cff_base.filename):
                flash("Extension is not an allowed extension")
                failed_load = True

            if failed_load:
                result = helpers.create_config_hash_from_template(component_list)
                return render_template('config_file_form.html', result=result)

            # All our uploaded file validation steps passed
            # Reload page, filling in config fields in form
            filename = secure_filename(_cff_base.filename)
            _cff_base.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            _cff_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            shutil.copyfile(_cff_location, session.get("config_file"))
            result = helpers.create_config_hash_from_template(component_list, session.get("config_file"))
            if result is None:
                return render_template('config_file_form.html', result=result)

            # Ensure all required components have a config file section
            missing_components = [component for component in component_list if component not in result.keys()]
            if missing_components:
                for comp in missing_components:
                    flash('Uploaded config file is missing fields for component \'' +
                        comp+'\', which is required for one of the selected pipeline options.')
                result = helpers.create_config_hash_from_template(component_list)
                return render_template('config_file_form.html', result=result)

            session['cff_location'] = _cff_location
            return render_template('config_file_form.html', result=result)
        # end Upload if

        ### 2) Hit 'Next' on template section page with uploaded file.
        if session.get('cff_location'):
            # This assumes the user's uploaded form is correct (no required_fields check)
            session.pop('cff_location', None)
            return redirect(url_for('main_bp.submit'))

        ### 3) Config fields were manually filled in, and "Next" was clicked.

        # Get fields, either from Prok/Euk template, or from existing temp.config file
        if os.path.exists(session.get("config_file")):
            # Only reach here if required param validation failed
            app.logger.debug("Reading from temp config file. " +
                            "Must have failed required param validation or hit 'Back' in browser.")
            try:
                result = helpers.create_config_hash_from_template(component_list, session.get("config_file"))
            except KeyError as e:
                # Safeguarding against accidental removal of the file since the script removes it at one point
                err = "The {} file could not be read.  Resetting page.".format(session.get("config_file"))
                app.logger.error(err)
                app.logger.error(e)
                app.logger.error(sys.exc_info()[0])
                flash(err)
                session.pop('edit_cff', None)
                result = helpers.create_config_hash_from_template(component_list)
                return render_template('config_file_form.html', result=result)
        else:
            result = helpers.create_config_hash_from_template(component_list)

        # Write fields to temporary pipeline config file
        with open(session.get("config_file"), 'w') as config_fh:
            for component in result:
                if not component:
                    continue
                config_fh.write('['+component+']\n')
                for i in range(0, len(result[component])):
                    _key = result[component][str(i)]['key']
                    _value = str(request.form[component + '_' + _key])
                    _comment = result[component][str(i)]['comment']
                    result[component][str(i)]['value'] = _value
                    config_fh.write(';; ' + _comment + '\n')
                    config_fh.write('$;' + _key + '$; = ' + _value + '\n')
                config_fh.write('\n')

        # Verify all required config fields have a value
        invalid_components = []
        for elem in session.get('required_fields'):
            if str(request.form[elem[0]+'_'+elem[1]]) == '':
                invalid_components.append(elem[0])
        invalid_comp_set = set(invalid_components)
        # Failed validation
        if invalid_comp_set:
            for comp in invalid_comp_set:
                flash('Required fields in section \''+comp+'\' cannot be left empty.')
            result = helpers.create_config_hash_from_template(component_list, session.get("config_file"))
            return render_template('config_file_form.html', result=result)

        # If config data validated, go to next page
        return redirect(url_for('main_bp.submit'))

    else:
        # Reach here during edit from 'submit'.  Will show config file results.
        result = dict()
        if session.get('edit_cff') == 1:
            try:
                result = helpers.create_config_hash_from_template(component_list, session.get("config_file"))
            except Exception as e:
                # Safeguarding against accidental removal of the file since the script removes it at one point
                err = "The {} file could not be read.  Resetting page.".format(session.get("config_file"))
                app.logger.error(err)
                app.logger.error(e)
                app.logger.error(sys.exc_info()[0])
                flash(err)
                session.pop('edit_cff', None)
                result = helpers.create_config_hash_from_template(component_list)
            return render_template('config_file_form.html', result=result)

    session.setdefault('edit_cff', 0)

    result = helpers.create_config_hash_from_template(component_list)
    return render_template('config_file_form.html', result=result)

@main_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():

    # Turn session vars on indicating that the pages have been filled with initial values and now need to be modified
    session['edit_cff'] = 1
    session['edit_sif'] = 1
    session['edit_po'] = 1

    user_name = current_user.get_id()
    temp_config = session.get("uniq_file_prefix") + ".temp.config"
    temp_info = session.get("uniq_file_prefix") + ".temp.info"

    result, _ = helpers.read_config_file(session.get("config_file"))

    # Copy files to 'static' directory, where they can be downloaded
    shutil.copyfile(session.get("config_file"), os.path.join(CURRENT_DIR, "static/tmp", temp_config))
    shutil.copyfile(session.get("sample_info_file"), os.path.join(CURRENT_DIR, "static/tmp", temp_info))

    if request.method == 'POST':
        app.logger.debug('In /submit - POST')
        dir_prefix = 'Input'
        input_dir_name = dir_prefix + '_' + session.get('localtime')

        ### Start building the argument for the Perl script ###
        cmd_args = ["/usr/bin/perl"]
        script_dir = os.path.join(app.config['PACKAGE_DIR'], 'bin')
        templates_dir = os.path.join(app.config['PACKAGE_DIR'],'global_pipeline_templates')
        if app.config['DOCKER']:
            templates_dir = os.path.join(app.config['PACKAGE_DIR'],'pipeline_templates')
        ergatis_ini = app.config['ERGATIS_INI']

        # Create output dir to place pipeline-relevant files, if it does not exist
        output_dir = os.path.join(session['pipeline_options'].get('repository_root'),  "pipelines/")
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
            os.chmod(output_dir, 0o777)

        # flash(output_dir)
        app.logger.debug("Output directory : " + output_dir)

        info_file_name = input_dir_name+'_sample.info'
        info_file = os.path.join(output_dir, info_file_name)
        shutil.copyfile(session.get("sample_info_file"), info_file)
        session['sample_info_file'] = info_file


        config_file_name = input_dir_name+'_template.config'
        config_file = os.path.join(output_dir, config_file_name)
        shutil.copyfile(session.get("config_file"), config_file)

        script_path = os.path.join(script_dir, "create_prok_rnaseq_pipeline_config.pl")
        template = os.path.join(templates_dir, "Prokaryotic_RNA_Seq_Analysis")

        if session.get('pipeline_type') == "Eukaryotic":
            script_path = os.path.join(script_dir, "create_euk_rnaseq_pipeline_config.pl")
            template = os.path.join(templates_dir, "Eukaryotic_RNA_Seq_Analysis")

        cmd_args.append(script_path)
        cmd_args.append("--td=" + template)
        cmd_args.append("--s=" + info_file)
        cmd_args.append("--c=" + config_file)
        cmd_args.append("--ei=" + ergatis_ini)
        cmd_args.append("--r=" + session['pipeline_options'].get('reference'))
        cmd_args.append("--gtf=" + session['pipeline_options'].get('gtf'))
        cmd_args.append("--rr=" + session['pipeline_options'].get('repository_root'))
        cmd_args.append("--o=" + output_dir)
        cmd_args.append("--annotation_format=" + session['pipeline_options'].get('annotation_format'))

        cmd_args.append("--user=" + user_name)

        # Lastly, assign all variable option flags
        pipeline_args = helpers.parse_pipeline_options_flags()
        cmd_args.extend(pipeline_args)

        # The perl script command should be built at this point
        # Append 'sudo' stuff in front if running internally.  Docker image does not have 'sudo'
        if not app.config['DOCKER']:
            cmd_args[:0] = ["sudo", "-u", user_name]

        pipeline_opts_keys = []
        if session.get('pipeline_options'):   # should always be true
            pipeline_opts_keys = [x for x in session.get('pipeline_options') if session['pipeline_options'].get(x) == 'on']
        session['pipeline_options_string'] = ';'.join(pipeline_opts_keys)

        cmd_line = ' '.join(cmd_args)
        app.logger.debug("Preparing to launch pipeline - command:\n" + cmd_line)

        proc = subprocess.Popen(cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            universal_newlines=True
        )
        proc.wait()
        # This function will redirect to pipeline_status if successful
        pipeline = helpers.handle_create_pipeline_subprocess(proc)
        if pipeline:
            pipeline_util.run_pipeline(pipeline.pipeline_url)
            pipeline.sample_info = info_file
            pipeline.config_file = config_file
            helpers.append_to_pipeline_flatfile(pipeline, info_file, config_file)
            helpers.remove_temp_files()
            helpers.clear_submitted_pipeline_session_values()
            return redirect(url_for('main_bp.pipeline_status', pipeline_id=pipeline.pipeline_id))

    return render_template('submit.html', result=result)

@main_bp.route('/pipeline_status', methods=['GET', 'POST'])
@main_bp.route('/pipeline_status/<int:pipeline_id>', methods=['GET', 'POST'])
@login_required
def pipeline_status(pipeline_id):
    ''' Monitor current status of the running pipeline '''
    #app.logger.debug('Entered /pipeline_status - ' + request.method)

    pipeline = ''
    p_url = ''
    if pipeline_id:
        # Determine if BDBag (w/ or w/o reports) is present.  Dictates which buttons are enabled/disabled
        helpers.find_existing_bdbag_file(pipeline_id)
        helpers.find_existing_reports_zip(pipeline_id)
        pipeline_obj = pipeline_util.get_pipeline_from_id(pipeline_id)
        try:
            pipeline = pipeline_obj.serialize()
            #app.logger.debug("{}".format(pipeline))
            if not ("pipeline_xml" in pipeline or "pipeline_url" in pipeline) \
                or (pipeline["pipeline_xml"] == None and pipeline["pipeline_url"] == None):
                app.logger.error("Unable to update pipeline from filesystem")
                app.logger.error(sys.exc_info()[0])
            if not "pipeline_url" in pipeline or pipeline["pipeline_url"] == None:
                #app.logger.debug("Building URL from pipeline XML")
                pipeline['pipeline_url'] = xml_util.build_view_pipeline_url(pipeline['pipeline_xml'])
            if not "pipeline_xml" in pipeline or pipeline["pipeline_xml"] == None:
                #app.logger.debug("Building XML from pipeline URL")
                pipeline['pipeline_xml'] = pipeline_util.parse_xml_from_url(pipeline['pipeline_url'])
            p_url = pipeline['pipeline_url']
            pipeline = xml_util.get_pipeline_details(pipeline['pipeline_xml'])
        except Exception as e:
            err = "Pipeline could not be obtained via ID {}".format(pipeline_id)
            app.logger.error(err)
            app.logger.error(e)
            app.logger.error(sys.exc_info()[0])
            flash(err)
    pipeline['pipeline_url'] = p_url
    helpers.get_extra_pipeline_flatfile_info(pipeline)

    # Reach this if any button is hit.
    if request.method == 'POST':
        if 'Refresh' in request.form:
            app.logger.debug("Refresh was hit.  Updating pipeline status for pipeline ID " + str(pipeline_id))
            if pipeline['status'] != "complete":
                pipeline_xml = pipeline['pipeline_xml']
                pipeline = xml_util.get_pipeline_details(pipeline_xml)
            else:
                app.logger.debug("Pipeline is complete!")
        elif 'create_bdbag' in request.form:
            bdbag_zip = helpers.create_bdbag(pipeline)
            if bdbag_zip:
                session['bdbag_zip'] = bdbag_zip
                flash("BDBag object has been successfully created!", "success")
        elif 'generate_report' in request.form:
            if helpers.make_pipeline_report(pipeline):
                app.logger.debug("Report created for pipeline {}".format(pipeline["pipeline_id"]))
                flash("Report has been successfully generated!", "success")
                helpers.find_existing_reports_zip(pipeline_id)
        elif "download_bag" in request.form:
            app.logger.debug("BDBag with reports for pipeline {}... ready for download".format(pipeline["pipeline_id"]))
            filename = os.path.basename(session.get('bdbag_zip'))
            zip_path = "bdbag"
            if session.get('reports_zip'):
                filename = os.path.basename(session.get('reports_zip'))
                zip_path = "reports"
            return redirect(url_for('main_bp.download_bag', path=zip_path, bdbag_zip=filename))

    #app.logger.debug("{}".format(pipeline))
    return render_template('pipeline_status.html', pipeline=pipeline)

@main_bp.route('/recent_pipelines')
@main_bp.route('/recent_pipelines/<string:proj_code>')
@login_required
def recent_pipelines(proj_code=None):
    """Load project codes, if passed one, load recent pipelines."""
    app.logger.debug('Entered /recent_pipelines - ' + request.method)
    session.pop('bdbag_zip', None)
    session.pop('reports_zip', None)
    codes = set()
    pipelines = []

    try:
        with open(app.config['PIPELINE_FLATFILE'], 'r') as ff:
            ff.readline()
            for line in ff:
                if not line.startswith(current_user.get_id()):
                    continue
                fields = line.rstrip().split()
                user = fields[0]
                code = fields[1]
                repo_root = fields[2]
                pipe_id = fields[3]

                codes.add(code)
                if proj_code:
                    if code != proj_code:
                        continue
                    pipeline_xml = "{}/workflow/runtime/pipeline/{}/pipeline.xml".format(repo_root, pipe_id)
                    # If pipeline object does not exist, it will be created.
                    # This could happen if the app is re-deployed but the flatfile remained
                    # However pipeline URL will not be created (yet)
                    # Missing Pipeline XML could cause the pipeline object to not be created as well
                    pipeline = xml_util.get_pipeline_details(pipeline_xml)

                    if not pipeline:
                        continue
                    pipelines.append(pipeline)
    except IOError as e:
        err = "File that stores pipeline information could not be read.  Perhaps no " \
            "pipelines have been run yet (meaning the file hasn't been created), " \
            "or there are permissions issues."
        app.logger.error(err)
        app.logger.error(e)
        app.logger.error(sys.exc_info()[0])
    # Prune pipelines down to most recent ones per project
    if proj_code and len(pipelines) > app.config['MAX_RECENT_PIPELINES']:
        pipelines = pipelines[-app.config['MAX_RECENT_PIPELINES']:]

    return render_template(
        'recent_pipelines.html',
        pipelines=pipelines,
        codes=codes
        )

@main_bp.route('/download/<string:path>/<string:bdbag_zip>')
@login_required
def download_bag(path, bdbag_zip):
    """ Retrieve and download the zipped BDBag object. """
    zip_path = app.config["BDBAG_OUTPATH"]
    if path == "reports":
        zip_path = app.config["REPORTS_OUTPATH"]
    return send_from_directory(zip_path, bdbag_zip, as_attachment=True)