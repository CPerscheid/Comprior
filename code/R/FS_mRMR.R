#Runs mRMR feature selection in parallel as implemented in the mRMRe package: De Jay, N. et al. "mRMRe: an R package for parallelized mRMR ensemble feature selection." Bioinformatics (2013).
#Although run in parallel, the performance is still not very good for high-dimensional data sets (>20.000 features).
#The resulting scores sometimes seem to not be sorted.
#However, these scores are the individual features' scores and feature combinations can result in a different overall ranking.
#Invoked by python's featureselection.MRMRSelector class.
#
#@param args the input parameters parsed from the command line, consisting of
#         - absolute path to the input data set file.
#         - absolute path to the output file where the ranking will be stored.
#         - maximum number of features to select.

library(mRMRe)

args = commandArgs(trailingOnly=TRUE)

inputFile <- args[[1]]
outputLocation <- args[[2]]
maxFeatures <- args[[3]]


if (length(args)<3) {
  stop("Please supply three arguments: inputFile (data set), outputLocation (feature ranking), and maxFeatures (number of features to select)", call.=FALSE)
}

rawData <- read.csv(inputFile, check.names = FALSE, stringsAsFactors = TRUE)
#check.names= FALSE necessary because R introducing X for column names beginning with numbers
geneExpressionMatrix <- rawData[-c(1)]
geneExpressionMatrix[,1] <- as.numeric(geneExpressionMatrix[,1])

#do feature selection here
dd <- mRMR.data(data = geneExpressionMatrix)
features <- mRMR.classic(data = dd, target_indices = c(1), feature_count = maxFeatures)

ranking <- solutions(features)
scores <- features@scores[[1]]

colNames <- names(geneExpressionMatrix)
featureNames <- list(colNames[unlist(ranking)])

outputData <- list(featureNames,scores)

fileOutput <- as.data.frame(outputData)

colnames(fileOutput) <- c("attributeName", "score")

write.csv(fileOutput, file = outputLocation, row.names = FALSE, sep = "\t")

