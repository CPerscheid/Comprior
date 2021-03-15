install.packages("UpSetR", repos='http://cran.us.r-project.org') #for ranking overlap visualization

if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("genefilter") #for feature selection
BiocManager::install("mRMRe") #for feature selection
BiocManager::install("biomaRt")#for ID mapping

install.packages("xtune") #Prior knowledge as penalty term

install.packages("tidyr")
