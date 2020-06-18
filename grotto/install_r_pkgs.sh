#!/bin/sh

# Install R packages we need
echo "install.packages(c('magick', 'GlobalOptions', 'rmarkdown', 'tinytex', 'grid', 'gridExtra', 'RColorBrewer', 'gplots', 'ggplot2', 'reshape2', 'circlize', 'ggfortify', 'ggdendro', 'ggpubr', 'lme4', 'VennDiagram', 'knitr', 'modeltools', 'mvtnorm', 'png', 'dplyr', 'rafalib', 'gtools'), dependencies=TRUE, repos='http://cran.rstudio.com/')" | R --save --restore || exit 1
# Install TinyTeX as a LaTeX replacement
echo "tinytex::install_tinytex()" | R --save --restore || exit 1
# Install Bioconductor packages
echo "install.packages('BiocManager', dependencies=TRUE, repos='http://cran.rstudio.com/')" | R --save --restore || exit 1
echo "BiocManager::install(c('limma', 'ComplexHeatmap', 'edgeR', 'Biobase', 'genefilter', 'DESeq'))" | R --save --restore || exit 1
