#Maps a set of identifiers to a desired format by using the biomaRt package.
#Currently, usage of this functionality is not enabled as biomaRt showed to be very unstable for returning queries in parallel
#(the server is not reachable, the connection is blocked, ...).
#The current implementation sends the identifiers for mapping in chunks of 10.000 identifiers
#(that was one desperate try to improve biomaRt stability, but it probably did not help...).
# Invoked by python's knowledgebases.BioMART class.
#
#@param args the input parameters parsed from the command line, consisting of
#         - original ID format (corresponding to biomaRt identifiers), e.g. ensembl_gene_id
#         - desired ID format (corresponding to biomaRt identifiers), e.g. hgnc_symbol
#         - absolute path to the input file, which contains one identifier per line
#         - absolute path to the output file where the mapping will be stored.

library(biomaRt)
library(httr)

args = commandArgs(trailingOnly=TRUE)
originalIDFormat <- args[[1]]
requiredIDFormat <- args[[2]]
inputFile <- args[[3]]
outputFile <- args[[4]]
httr::set_config(httr::config(ssl_verifypeer = FALSE))
mart<-useEnsembl(biomart = "ENSEMBL_MART_ENSEMBL",
                 dataset = "hsapiens_gene_ensembl", mirror = "useast")
print(inputFile)
#load data set from file
data <- read.csv(inputFile, header = FALSE, stringsAsFactors = FALSE)
#fetch gene mapping
#attributes: what your results shall include
#filters: what platform your IDs are currently from
#values: the concrete IDs as input
#mapping <- getBM(attributes = c(originalIDFormat, requiredIDFormat), filters = originalIDFormat, values=data, mart = mart)
chunksize = 10000

final_mapping = NULL
chunks = as.integer(nrow(data)/chunksize)
if (chunks > 0){
  for (i in 1:chunks){
    start = ((i-1) * chunksize) + 1
    end = i * chunksize
    genechunk = data[start:end,1]
    mapping <- getBM(attributes = c(originalIDFormat, requiredIDFormat), filters = originalIDFormat, values=(genechunk), mart = mart)
    if (is.null(final_mapping)){
      final_mapping = mapping
    } else{
      final_mapping = rbind(final_mapping, mapping)
    }
  }
}

leftover = as.integer(nrow(data) - (chunks * chunksize))
if (leftover > 0){
  start = (chunks * chunksize) + 1
  end = nrow(data)
  last_genechunk = data[start:end,1]
  mapping <- getBM(attributes = c(originalIDFormat, requiredIDFormat), filters = originalIDFormat, values=(last_genechunk), mart = mart)
  if (is.null(final_mapping)){
    final_mapping = mapping
  } else{
    final_mapping = rbind(final_mapping, mapping)
  }
}
write.csv(final_mapping, outputFile, row.names = FALSE)
