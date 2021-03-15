#Runs Lasso feature selection with individual penalty scores for each feature as implemented in the xtune package:
#Zeng, C. et al.: "Incorporating prior knowledge into regularized regression", Bioinformatics (2020), https://doi.org/10.1093/bioinformatics/btaa776
#Invoked by python's featureselection.LassoPenaltySelector class.
# #
#@param args the input parameters parsed from the command line, consisting of
#         - absolute path to the input data set file.
#         - absolute path to the output file where the ranking will be stored.
#         - absolute path to the input ranking file (where the external rankings that will serve as penalty scores are stored).

library(xtune)

args = commandArgs(trailingOnly=TRUE)

input.filename <- args[[1]]
output.filename <- args[[2]]
external.filename <- args[[3]]

if (length(args)<3) {
  stop("Please supply three arguments: inputFile (gene expression data), outputLocation (feature ranking), and filename for external scores", call.=FALSE)
}

expression.matrix <- read.csv(input.filename, check.names = FALSE, row.names = 1)
external.scores <- read.csv(external.filename, check.names = FALSE, row.names = 1)
#check.names= FALSE necessary because R introducing X for column names beginning with numbers

expression.levels  <- expression.matrix[-c(1,1)]

#we want to predict the labels = classes
labels <- expression.matrix[1]
#make labels numeric
label.types = unique(labels[,1])

labels <- as.numeric(factor(labels[,1], label.types, labels = 1:length(label.types) ))

#train the model
prior.knowledge.model <- xtune(as.matrix(expression.levels), labels, external.scores)

coefs <- coef(prior.knowledge.model)
final.scores <- as.data.frame(as.matrix(coefs))
#rename score column
colnames(final.scores) <- c("score")
#remove intercept element (drop param keeps row names)
final.scores <- final.scores[-c(1),, drop=FALSE]
feature.indexes <- order(final.scores$score,decreasing = TRUE)
final.scores <- final.scores[feature.indexes,, drop = FALSE] #drop retains row names
final.scores <- cbind(attributeName = rownames(final.scores), final.scores)

#write dataframe
write.table(final.scores, output.filename, row.names = FALSE, sep = "\t")
