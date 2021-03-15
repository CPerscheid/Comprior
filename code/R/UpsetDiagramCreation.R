#Uses the UpSetR package to create an upset diagram for a given set of features.
#Invoked by python's evaluation.RankingsEvaluator and evaluation.AnnotationEvaluator classes.
#
#@param args the input parameters parsed from the command line, consisting of
#         - absolute path to the output file where to store the created plot.
#         - number of top k features for which to compute the feature set overlaps.
#         - absolute path to the input directory containing the input files.
#         - string of color ids separated by "_", used for giving every feature ranking a unique color.
#         - list of input files containing the rankings. their order corresponds to the order of colors.
library(UpSetR)
library(stringr)

args = commandArgs(trailingOnly=TRUE)

outputFile = args[[1]]

topK = strtoi(args[[2]])

inputPath = args[[3]]

#remove training _
colorstring = substring(args[[4]], 2)

#split by _
colors = str_split(colorstring, "_")
rankings = list()
setCount = 0

for (filename in args[5:length(args)]) {
  approach.topK = topK
  topGenes = list()
  #find fileending
  parts = gregexpr(pattern ='\\.', filename)[[1]]
  method = substr(filename, 1, parts[length(parts)] - 1)
  file = paste(inputPath, filename, sep="")
  ranking <- read.csv(file, sep = "\t", stringsAsFactors = FALSE)
  #get top n genes for the overlap and adapt topK if we have fewer genes
  numRows = nrow(ranking)
  if (numRows > 0){
    if (numRows < approach.topK){
      approach.topK = numRows
    }
    genes = head(ranking, n = approach.topK)[[1]]
    #as the genes in the columns are by default detected as factors, we just get the levels (=distinct names)
    topGenes = genes
    
  }
    
  #only add approach results if they are not empty
  if (length(topGenes) > 0){
    #make a list out of topGenes otherwise we have a format issue
    rankings[method] = list(topGenes)
    setCount = setCount + 1
  }
}
print(paste0("UPSETR SETCOUNT ", toString(setCount)))
print(paste0("UPSETR COLORCOUNT ", toString(length(colors))))
pdf(file=outputFile, onefile=FALSE)
upset(fromList(rankings), nsets = setCount, order.by = "freq", sets.bar.color = unlist(colors, use.names=FALSE))

dev.off()
