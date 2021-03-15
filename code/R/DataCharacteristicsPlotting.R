#Creates plots to show some characteristics of a given expression data set and its class labels.
#Currently supported plots that can be selected:
# - density plots (density)
# - box plot (box)
# - mds plot (mds)
#Invoked by python's evaluation.DatasetEvaluator class.
#
#@param args the input parameters parsed from the command line, consisting of
#         - absolute path to the input expression file.
#         - absolute path to the output directory where the plots will be stored.
#         - separator to use for reading the input expression file.
#         - a boolean value whether the input expression data is labeled or not.
#         - a list of option names that define what plots are created. Currently supported: density (density plot), box (boxplot of expression values), mds).
library(ggplot2)
library(dplyr)
library(tidyr)
library(tools)

args = commandArgs(trailingOnly=TRUE)

input.filename <- args[[1]]
output.dir <- args[[2]]
separator <- args[[3]]
labeledData <- args[[4]]
options <- args[5:length(args)]

if (length(options) == 0){
  stop("No data characteristics were selected in config file", call.=FALSE)

}
rownamescol <- 1

data <- read.table(input.filename, sep= separator, header=TRUE, row.names = rownamescol, check.names = FALSE, stringsAsFactors = FALSE)
if (labeledData == "TRUE"){
  unlabeleddata <- data[-1]   #remove label column
  labelCol <- colnames(data)[1] 
}
filename = file_path_sans_ext(basename(input.filename))

#################### PLOT DENSITIES ####################
if ("density" %in% options){
  output.filename = paste0(output.dir, "density_", filename, ".pdf")
  pl2 <- data %>% gather(key = "Gene", value = "Expression", -1) %>% ggplot(., aes(x=Expression, color = get(labelCol))) + geom_density()
  pdf(output.filename)
  print(pl2)
  dev.off()
}

#################### PLOT DISTRIBUTION ####################
if ("box" %in% options){
  output.filename = paste0(output.dir, "distribution_", filename, ".pdf")
  boxpl <- data %>% gather(key = "Gene", value = "Expression", -1) %>% ggplot(., aes(get(labelCol), Expression, color = get(labelCol))) + geom_boxplot()
  pdf(output.filename)
  print(boxpl)
  dev.off()
}

#################### PLOT MDS ####################
if ("mds" %in% options){
  output.filename = paste0(output.dir, "mds_", filename, ".pdf")
  #compute euclidean distance matrix (euclidean distance is used in the limma package)
  dist.eu <- as.matrix(dist(unlabeleddata, method = "euclidean"))
  mds.eu <- as.data.frame(cmdscale(dist.eu))
  mds.eu <- merge(mds.eu, data[1], by="row.names", all=TRUE)

  mdspl <- ggplot(mds.eu, aes(V1, V2, label = classLabel, color = classLabel)) + 
    geom_point(size=2) + 
    labs(x="", y="", title="MDS by Euclidean") + theme_bw()

  pdf(output.filename)
  print(mdspl)
  dev.off()
}
