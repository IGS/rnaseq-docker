
# pipeline_components.py

# Contains data structures to assist in determining which components with
# config sections in the Prok or Euk template config file should be loaded in
# the config_file_form page.

# If --tophat_legacy, use Tophat instead of HiSat2
TOPHAT_COMPONENTS = {'bowtie_build', 'tophat'}
HISAT_COMPONENTS = {'hisat2_build', 'hisat2'}

# If --cufflinks_legacy, use the old cufflinks components
CUFFLINKS_MODERN_COMPONENTS = {'cuffquant', 'cuffmerge', 'cuffnorm'}
CUFFLINKS_LEGACY_COMPONENTS = {'cuffcompare'}

# Exclude if both --count and --alignment are not passed
COUNT_OR_ALIGN_COMPONENTS = {'htseq'}

# Exclude if 'use_ref_gtf' is enabled
REF_GTF_COMPONENTS = {'cuffmerge', 'cuffcompare'}

# Each key is a section of the pipeline that is specified in Pipeline Options
# Each value is a set of components associated with that section.
COMPONENT_SECTIONS = {
    'build_indexes' : {'bowtie_build', 'hisat2_build'},
    'quality_stats' : {'fastx_quality_stats'},
    'quality_trimming' : {'fastx_trimming'},
    'alignment' : {'bowtie', 'tophat', 'hisat2', 'percent_mapped_stats'},
    'rpkm_analysis' : {'rpkm_coverage_stats', 'expression_plots'},
    'visualization' : {'bam2bigwig'},
    'differential_gene_expression' : {'htseq', 'deseq', 'filter_deseq', 'edgeR', 'filter_edgeR'},
    'isoform_analysis' : {'cufflinks'},
    'differential_isoform_analysis' : {'cuffcompare', 'cuffmerge', 'cuffdiff', 'cuffdiff_filter', 'cuffquant', 'cuffnorm', 'expression_plots', 'cummerbund'}
}

ACCORDION_INFO = {
    "bowtie_build": {
        "title": "Bowtie Build",
        "description": "Build Bowtie reference indexes",
        "color": "green"
    },
    "hisat2_build": {
        "title": "Hisat2 Build",
        "description": "Build HiSat2 reference indexes",
        "color": "green"
    },
    "fastx_quality_stats": {
        "title": "Fastx Quality Stats",
        "description": "Generate quality statistics of the sample input",
        "color": "green"
    },
    "fastx_trimming": {
        "title": "Fastx Trimming",
        "description": "Trim sample sequences",
        "color": "green"
    },
    "split_fastq": {
        "title": "Split FastQ",
        "description": "Split sample input into smaller files for quicker runtimes<",
        "color": "green"
    },
    "tophat": {
        "title": "Tophat",
        "description": "Run Tophat fast splice junction mapper",
        "color": "yellow"
    },
    "bowtie": {
        "title": "Bowtie",
        "description": "Run Bowtie aligner",
        "color": "green"
    },
    "hisat2": {
        "title": "Hisat2",
        "description": "Run HiSat2 aligner",
        "color": "yellow"
    },
    "percent_mapped_stats": {
        "title": "Percent Mapped Stats",
        "description": "Calculate mapping statistics of aligned reads",
        "color": "red"
    },
    "rpkm_coverage_stats": {
        "title": "RPKM Coverage Stats",
        "description": "Calculate coverage statistics using BEDtools",
        "color": "red"
    },
    "bam2bigwig": {
        "title": "Bam2BigWig",
        "description": "Convert BAM to BigWig format",
        "color": "green"
    },
    "htseq": {
        "title": "HTSeq",
        "description": "Generate HTSeq read counts",
        "color": "yellow"
    },
    "deseq": {
        "title": "DESeq",
        "description": "Analyze differential gene expression from HTSeq read counts",
        "color": "green"
    },
    "filter_deseq": {
        "title": "Filter DESeq",
        "description": "Filter DESeq output on various metrics",
        "color": "green"
    },
    "edgeR": {
        "title": "EdgeR",
        "description": "Analyze differential gene expression from HTSeq read counts",
        "color": "green"
    },
    "filter_edgeR": {
        "title": "Filter EdgeR",
        "description": "Filter EdgeR output on various metrics",
        "color": "green"
    },
    "cufflinks": {
        "title": "Cufflinks",
        "description": "Transcriptome assembly and differential expression analysis for RNA-Seq",
        "color": "yellow"
    },
    "cuffcompare": {
        "title": "Cuffcompare",
        "description": "Compare Cufflinks GTF transcript to known annotation",
        "color": "green"
    },
    "cuffdiff": {
        "title": "Cuffdiff",
        "description": "Compare expression levels of transcripts",
        "color": "green"
    },
    "cuffdiff_filter": {
        "title": "Cuffdiff Filter",
        "description": "Filter cuffdiff results by various metrics",
        "color": "green"
    },
    "cuffquant": {
        "title": "Cuffquant",
        "description": "Generate transcript expression profiles for Cufflinks/Cuffcompare results",
        "color": "green"
    },
    "cuffmerge": {
        "title": "Cuffmerge",
        "description": "Merge Cufflinks transcript GTF files with or without reference",
        "color": "green"
    },
    "cuffnorm": {
        "title": "Cuffnorm",
        "description": "Generate Cuffnorm transcript normalized expression for Cuffquant results",
        "color": "green"
    },
    "expression_plots": {
        "title": "Expression Plots",
        "description": "Creates plots for DESeq/Cuffdiff or RPKM analysis",
        "color": "green"
    },
    "cummerbund": {
        "title": "CummeRbund",
        "description": "Generate plots from Cuffdiff analysis",
        "color": "green"
    }
}
