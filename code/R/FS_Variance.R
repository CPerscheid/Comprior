#Runs variance-based feature selection as implemented in the genefilter package.
#For every feature, computes its variance across all samples.
#Features are then ranked in descending order - highly variant features are more likely to separate samples into classes and seem to be the most interesting ones.
#Invoked by python's featureselection.VarianceSelector class.
#
#@param args the input parameters parsed from the command line, consisting of
#         - absolute path to the input data set file.
#         - absolute path to the output file where the ranking will be stored.

library(genefilter)

args = commandArgs(trailingOnly=TRUE)

if (length(args)<2) {
  stop("Please supply two arguments: inputFile (gene expression data) and outputLocation (feature ranking)", call.=FALSE)
}

rawData <- read.csv(args[1], check.names = FALSE)
#check.names= FALSE necessary because R introducing X for column names beginning with numbers

geneExpressionMatrix <- rawData[-c(1,2)]

rV <- rowVars(t(geneExpressionMatrix))

ordered <- rV[order(-rV) , drop = FALSE]

orderedNameList <-  names(ordered)

orderedNameValueList <- c(orderedNameList,data.frame(ordered)[,1])

orderedNameValueMatrix <- matrix(orderedNameValueList,ncol=2)

colnames(orderedNameValueMatrix) <- c("attributeName", "score")

write.table(orderedNameValueMatrix, file = args[2], row.names = FALSE, sep = "\t")
