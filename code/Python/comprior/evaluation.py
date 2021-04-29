from abc import abstractmethod
import time, os, math, random
import knowledgebases, benchutils
import pandas as pd
import numpy as np
import matplotlib as matplots
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
from matplotlib_venn import venn3


class AttributeRemover():
    """Prepares the input data set for subsequent classification by removing lowly-ranked features and only keeping the top k features.
       Creates one "reduced" file for every ranking and from one to k (so if k is 50, we will end up with 50 files having one and up to 50 features.

       :param dataDir: absolute path to the directory that contains the input data set whose features to reduce.
       :type dataDir: str
       :param rankingsDir: absolute path to the directory that contains the rankings.
       :type rankingsDir: str
       :param topK: maximum numbers of features to select.
       :type topK: str
       :param outputDir: absolute path to the directory where the reduced files will be stored.
       :type outputDir: str
    """

    def __init__(self, dataDir, rankingsDir, topK, outputDir):
        self.dataDir = dataDir
        self.rankingsDir = rankingsDir
        self.topK = int(topK)
        self.outputDir = outputDir
        super().__init__()

    def loadTopKRankings(self):
        """Loads all available rankings from files.

           :return: Dictionary with selection methods as keys and  a ranked list of the (column) names of the top k features.
           :rtype: dict
           """

        #dictionary: topK genes per method
        rankings = {}
        for file in os.listdir(self.rankingsDir):
            if os.path.isfile(os.path.join(self.rankingsDir, file)):
                selectionMethod = file.split(".")[0] #get method name from filename without ending
                ranking = benchutils.loadRanking(self.rankingsDir + file)

                # geneRankings has the format attributeName, score
                # we need the feature name column
                featureNameCol = ranking.columns[0]
                # feature names
                featureNames = ranking[featureNameCol]

                # take feature names of top k features
                #if topK is larger than the actual size (=number of features), the whole list is returned without
                #throwing an error
                rankings[selectionMethod] = featureNames[:self.topK]

        return rankings

    def removeAttributesFromDataset(self, method, ranking, dataset):
        """Creates reduced data sets from dataset for the given method's ranking that only contain the top x features.
           Creates multiple reduced data sets from topKmin to topKmax specified in the config.

           :param method: selection method applied for the ranking.
           :type method: str
           :param ranking: (ranked) list of feature names from the top k features.
           :type ranking: :class:`List` of str
           :param dataset: original input data set
           :type dataset: :class:`pandas.DataFrame`
           """
        # create new subdirectory
        methodDir = self.outputDir + method + "/"
        benchutils.createDirectory(methodDir)

        topKmin = int(benchutils.getConfigValue("Evaluation", "topKmin"))
        for i in range(topKmin, len(ranking)+1):
            # write reduced data set to files
            featuresNames = ranking[:i]
            featuresToUse = list(set(featuresNames) & set(dataset.columns))
            colnames = list(dataset.columns[:2])
            colnames.extend(featuresToUse)
            reducedSet = dataset[colnames]
            # reduce i by one because ranking also contains the id column, which is not a gene
            outputFilename = methodDir + "top" + str(i) + "features_" + method + ".csv"
            reducedSet.to_csv(outputFilename, index=False, sep="\t")

    def removeUnusedAttributes(self):
        """For every method and its corresponding ranking, create reduced files with only the top x features.
           """
        #read in gene rankings and original data set
        geneRankings = self.loadTopKRankings()

        methods = list(geneRankings.keys())
        datafiles = os.listdir(self.dataDir)
        #sort input files by name length: the longer files having had a feature mapping first, the original file with only the prefix to be last
        datafiles.sort(key = len, reverse = True)

        for dataset in datafiles:

            data = pd.read_csv(self.dataDir + "/" + dataset)
            #match the method in the dataset name to the corresponding ranking
            #check if any of the available methods is a substring of the filename
            method_matches = [method for method in methods if method in dataset]
            if len(method_matches) > 0:
                #if we have a match, this file must contain a new feature space
                #we assume there is only one match possible, otherwise there would be two input data sets for the same method
                method = method_matches[0]
                #remove method from list of methods as we cannot apply this ranking to the original data set
                methods.remove(method)

                #do the attributeremoval
                ranking = geneRankings[method]
                self.removeAttributesFromDataset(method, ranking, data)

            else:
                #if not matchable, we have the original dataset
                #use the remaining rankings on the dataset
                #ASSUMPTION: we only have one file with the original prefix
                for method in methods:
                    ranking = geneRankings[method]
                    self.removeAttributesFromDataset(method, ranking, data)



class Evaluator:
    """Abstract super class.
       Every evaluation class has to inherit from this class and implement its :meth:`evaluate()` method.

       :param input: absolute path to the directory where the input data is located.
       :type input: str
       :param output: absolute path to the directory to which to save results.
       :type output: str
       :param methodColors: dictionary containing a color string for every selection method.
       :type methodColors: dict of str
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
       """
    def __init__(self, input, output, methodColors):
        self.javaConfig = benchutils.getConfig("Java")
        self.rConfig = benchutils.getConfig("R")
        self.evalConfig = benchutils.getConfig("Evaluation")
        self.classificationConfig = benchutils.getConfig("Classification")
        self.input = input
        self.output = output
        self.methodColors = methodColors
        super().__init__()

    @abstractmethod
    def evaluate(self):
        """Abstract.
           Must be implemented by inheriting class as this method is invoked by :class:`framework.Framework` to run the evaluation.
           """
        pass

    def loadRankings(self, inputDir, maxRank, keepOrder):
        """Loads all rankings from a specified input directory.
           If only the top k features shall be in the ranking, set maxRank accordingly, set it to 0 if otherwise (so to load all features).
           If feature order is important in the returned rankings, set keepOrder to true; if you are only interested in what features are among the top maxRank, set it to false.

           :param inputDir: absolute path to directory where all rankings are located.
           :type inputDir: str
           :param maxRank: maximum number of features to have in ranking.
           :type maxRank: int
           :param keepOrder: whether the order of the features in the ranking is important or not.
           :type keepOrder: bool
           :return: Dictionary of rankings per method, either as ordered list or set (depending on keepOrder attribute)
           :rtype: dict
           """
        rankings = {}

        for file in os.listdir(inputDir):
            if os.path.isfile(os.path.join(inputDir, file)):
                selectionMethod = file.split(".")[0]  # get method name from filename without ending
                ranking = benchutils.loadRanking(inputDir + file)
                genesColumn = ranking.columns[0]
                genes = ranking[genesColumn]
                # 0 is code number for using all items
                if maxRank == 0:
                    maxRank = len(ranking) - 1

                # add 1 for header column
                if keepOrder:
                    rankings[selectionMethod] = genes[:maxRank + 1]
                else:
                    rankings[selectionMethod] = set(genes[:maxRank + 1])

        return rankings

    def computeKendallsW(self, rankings):
        """Computes Kendall's W from two rankings.
           Note: measure does not make much sense if the two rankings are highly disjunct, which can happen especially for traditional approaches.

           :param rankings: matrix containing two rankings for which to compute Kendall's W.
           :type rankings: matrix
           :return: Kendall's W score.
           :rtype: float
           """
        if rankings.ndim != 2:
            raise 'ratings matrix must be 2-dimensional'
        m = rankings.shape[0]  # raters
        n = rankings.shape[1]  # items rated
        denom = m ** 2 * (n ** 3 - n)
        rating_sums = np.sum(rankings, axis=0)
        S = m * np.var(rating_sums)
        return 12 * S / denom

class ClassificationEvaluator(Evaluator):
    """Evaluates selection methods via classification by using only the selected features and computing multiple standard metrics.
       Uses :class:`AttributeRemover` to create reduced datasets containing only the top k features, which are then used for subsequent classification.
       Currently, classification and subsequent evaluation is wrapped here and is actually carried out by java jars using WEKA.

       :param input: absolute path to the directory where the input data for classification is located.
       :type input: str
       :param rankingsDir: absolute path to the directory where the rankings are located.
       :type rankingsDir: str
       :param intermediateDir: absolute path to the directory where the reduced datasets (containing only the top k features) are written to.
       :type intermediateDir: str
       :param output: absolute path to the directory to which to save results.
       :type output: str
       :param methodColors: dictionary containing a color string for every selection method.
       :type methodColors: dict of str
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
       """

    def __init__(self, inputDir, rankingsDir, intermediateDir, outputDir, methodColors, methodMarkers):
        self.rankingsDir = rankingsDir
        self.intermediateDir = intermediateDir
        self.methodMarkers = methodMarkers
        super().__init__(inputDir, outputDir, methodColors)

    def drawLinePlot(self, inputDir, outputDir, topK, metric):
        """Draws a line plot for a given metric, using all files containing evaluation results for that metric in inputDir.
           In the end, the plot will have one line per feature selection approach for which classification results are available.

           :param inputDir: absolute path to directory containing all input files (from which to draw the graph).
           :type inputDir: str
           :param outputDir: absolute path to the output directory where the the graph will be saved.
           :type outputDir: str
           :param topK: maximum x axis value
           :type topK: int
           :param metric: metric name for which to draw the graph.
           :type metric: str
           """
        fig, ax = plt.subplots()

        inputFiles = []

        # load data from files:
        for file in os.listdir(inputDir):
            if os.path.isfile(os.path.join(inputDir, file)) and file.endswith(metric + '.csv'):
                inputFiles.append(file)

        evalResults = {}
        count = 0
        metric_threshold = benchutils.metricScales[metric]
        miny = metric_threshold[0]
        maxy = metric_threshold[1]
        for file in inputFiles:

            ranking = pd.read_csv(inputDir + file, sep = "\t")

            methodName = file.replace("_" + metric + '.csv', '')
            #uncommend if methodNames should be shortened
            #shortened_methodName = methodName
            #if len(methodName) > 20:
            #    shortened_methodName = methodName.replace("_", "_\n")
            evalResults[file] = ranking["average"]
            if count == 0 and not ranking.empty:
                x_axis = ranking["#ofAttributes"]
                ax.set_xlim(x_axis[0], x_axis.iloc[-1])
                ax.set_xticks(x_axis)
                count = count + 1
            l1 = ax.plot(ranking["#ofAttributes"], ranking["average"], label=methodName, color = self.methodColors[methodName], marker = self.methodMarkers[methodName])
            # adapt the lower bound of y axis to the respective
            if ranking.empty:
                #no evaluation results for this approach
                local_miny = 0
            else:
                local_miny = ranking["average"].nsmallest(1).iloc[0]

            if local_miny < miny:
                miny = int(local_miny)
            tickdist = math.ceil(int(topK) / 5)
            if tickdist == 0:
                tickdist = 1
            ax.xaxis.set_major_locator(plt.MaxNLocator(tickdist)) #scale x axis to have ticks every 5 features

        ax.set_ylim(miny, maxy)
        ax.set_xlabel('Number of features selected')
        ax.set_ylabel('Average ' + metric + ' (%)')
        ax.legend()
        ax.set_title(metric + ' for Approaches')
        # plt.show()
        matplots.pyplot.savefig(outputDir + metric + ".pdf")
        matplots.pyplot.clf()

    def evaluate(self):
        """Triggers classification and evaluation in Java and creates corresponding plots for every metric that was selected in the config.
           """

        # reduce data set for crossEvaluation to selected genes
        attributeRemover = AttributeRemover(self.input, self.rankingsDir, self.evalConfig["topKmax"], self.intermediateDir)
        attributeRemover.removeUnusedAttributes()

        classifiers = self.classificationConfig["classifiers"].replace(" ", ",")
        metrics =self.classificationConfig["metrics"].replace(" ", ",")
        params = [self.intermediateDir,self.output, str(self.evalConfig["topKmin"]), str(self.evalConfig["topKmax"]), str(self.evalConfig["kfold"]) ]
        params.append(classifiers)
        params.append(metrics)

        benchutils.runJavaCommand(self.javaConfig, "/WEKA_Evaluator.jar", params)

        for metric in metrics.split(","):
            self.drawLinePlot(self.output, self.output, self.evalConfig["topKmax"], metric)

class RankingsEvaluator(Evaluator):
    """Evaluates the rankings themselves by generating overlaps and comparing fold change differences.

       :param input: absolute path to the directory where the input data is located.
       :type input: str
       :param output: absolute path to the directory to which to save results.
       :type output: str
       :param methodColors: dictionary containing a color string for every selection method.
       :type methodColors: dict of str
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
       :param dataset: absolute file path to the input data set (from which features were selected).
       :type dataset: str
       :param metrics: list of metrics to apply to ranking evaluation (as specified in the config file).
       :type metrics: :class:`List` of str
    """

    def __init__(self, input, dataset, outputPath, methodColors):
        self.metrics = benchutils.getConfigValue("Rankings", "metrics")
        self.dataset = dataset
        super().__init__(input, outputPath, methodColors)

    def generateOverlaps(self):
        """Creates overlap plots for the available rankings (set during creating to self.input).
           For up to two rankings, use Python's matplotlib to create Venn diagrams.
           For three rankings and above, create UpsetR (https://github.com/hms-dbmi/UpSetR) diagrams via R.
           """
        inputFiles = []
        for file in os.listdir(self.input):
            inputFiles.append(file)

        sizeOfSets = len(inputFiles)

        if sizeOfSets <= 1:
            print("Cannot compute overlaps as we do not have enough valid files.")

        elif sizeOfSets == 2: #if we have only 2 sets for intersection
            rankings = self.loadRankings(self.input, int(self.evalConfig["topKmax"]), False)
            colors = []
            methodNames = []
            for ranking in rankings.keys():
                colors.append(self.methodColors[ranking])
                if len(ranking) > 20:
                    ranking = ranking.replace("_", "_\n")
                methodNames.append(ranking)
            venn2(rankings.values(), set_labels = methodNames, set_colors = colors, alpha = 1.0)
            matplots.pyplot.savefig(self.output + "geneSignatureOverlaps.pdf")
            matplots.pyplot.clf()
        elif sizeOfSets == 3: #if we have only 2 sets for intersection
            rankings = self.loadRankings(self.input, int(self.evalConfig["topKmax"]), False)
            colors = []
            methodNames = []
            for ranking in rankings.keys():
                colors.append(self.methodColors[ranking])
                if len(ranking) > 20:
                    ranking = ranking.replace("_", "_\n")
                methodNames.append(ranking)
            venn3(rankings.values(),  set_labels = methodNames, set_colors = colors, alpha = 1.0)
            matplots.pyplot.savefig(self.output + "geneSignatureOverlaps.pdf")
            matplots.pyplot.clf()
        else: #for more sets use UpSets package
            params = [self.output + "geneSignatureOverlaps.pdf", self.evalConfig["topKmax"], self.input]
            colors = ""
            filenames = []
            for file in inputFiles:
                method = file.split(".")[0]  # get method name from filename without ending (format: top5_APPROACH_annotation.txt)
                colors += "_" + self.methodColors[method]
                filenames.append(file)
            params.append(colors)
            params.extend(filenames)
            benchutils.runRCommand(self.rConfig, "UpsetDiagramCreation.R", params)

    def loadGeneRanks(self, inputDir, topK):
        """Used for computing Kendall's W.
           Loads rankings and creates a table (approach x features) containing individual ranks per feature per approach, e.g.
           #approach   G1  G2  G3
           #Ranker1    1   2   3
           #Ranker 2   3   1   2

           :param inputDir: absolute path to the directory containing all ranking files.
           :type inputDir: str
           :param topK: maximum number of features to use (=length of the rankings).
           :type topK: int
           :return: Ranking table containing every assigned rank for every feature per ranking approach.
           :rtype: :class:`numpy.array`
           """
        finalRankMatrix = []
        rankings = self.loadRankings(inputDir, topK, True)

        # first, fill matrix column with all genes that occur in the rankings
        matrix_column = set()
        for method in rankings.keys():
            matrix_column = matrix_column.union(set(rankings[method]))
        matrix_column = list(matrix_column)

        #second, fill matrix approach by approach
        for method in rankings.keys():
            #initialize list with default 0 values (0 = not part of actual ranking)
            ranks = [len(matrix_column)] * len(matrix_column)
            count = 0
            for gene in rankings[method]:
                count += 1
                matrix_index = matrix_column.index(gene)
                ranks[matrix_index] = count
            finalRankMatrix.append(ranks)
        return np.array(finalRankMatrix)


    def computePValue(self, W, m, n):
        """Computes the p-value for a given Kendall's W score via a simple permutation (1000 times) test.

           :param W: Kendall's W score.
           :type W: float
           :param m: number of approaches/rankings to compare.
           :type m: int
           :param n: number of features in each ranking.
           :type n: int
           :return: p-value of Kendall's W score.
           :rtype: float
           """
        # do permutation test
        count = 0
        permutationSize = 1000
        for trial in range(permutationSize):
            perm_trial = []
            for _ in range(m):
                perm_trial.append(list(np.random.permutation(range(1, 1 + n))))
            count += 1 if self.computeKendallsW(np.array(perm_trial)) > W else 0
        # compute p-value
        pVal = count / permutationSize
        return pVal

    def computeKendallsWScores(self):
        """Computes Kendall's correlation coefficients (W) and its corresponding p-value for the top 50, 500, 5,000 and all (code: 0) ranked features of existing rankings.
           Conducts a permutation test for all scores to receive p-value.
           Writes output to a file containing the correlation coefficients and their corresponding p-value for different length of rankings.
           """
        ranking_sizes = [50, 500, 5000, 0]
        filename = self.output + "kendallsW.csv"
        with open(filename, "w") as f:
            header = "top n,Kendalls W, p-value\n"
            f.write(header)

            for ranksize in ranking_sizes:

                rankings = self.loadGeneRanks(self.input, ranksize)
                m = rankings.shape[0]
                n = rankings.shape[1]

                W = self.computeKendallsW(rankings)
                pVal = self.computePValue(W, m, n)

                #write line
                if ranksize == 0:
                    line = str(rankings.shape[1]) + ","
                else:
                    line = str(ranksize) + ","
                line += str(W) + "," + str(pVal) + "\n"
                f.write(line)


    def drawBoxPlot(self, data, labels, prefix):
        """Draws a box plot from the given data with the given labels on the x axis and the given prefix in the headlines.

           :param data: Data to plot; a list containing lists of values.
           :type data: :class:`List` of lists of floats
           :param labels: List of method names.
           :type labels: :class:`List` of str
           :param prefix: Prefix to use for file name and title.
           :type prefix: str
           """
        fig1, ax1 = plt.subplots()
        ax1.set_title(prefix +  ' Fold Changes in Gene Signatures')
        final_labels = []
        for label in labels:
            if len(label) > 20:
                label = label.replace("_", "_\n")
            final_labels.append(label)

        pl = ax1.boxplot(data, labels=final_labels, patch_artist=True)
        plt.xticks(rotation=45)
        #set the colors
        colors = []
        for label in labels:
            colors.append(self.methodColors[label])

        for patch, color in zip(pl['boxes'], colors):
            patch.set_facecolor(color)

        ax1.set_ylabel(prefix + ' gene fold change across all samples')
        plt.tight_layout()
        matplots.pyplot.savefig(self.output + prefix + "FoldChanges.pdf", bbox_inches = "tight")
        matplots.pyplot.clf()

    def computeFoldChangeDiffs(self):
        """Computes median and mean fold changes for all selected features per approach.
           Writes fold changes to file and creates corresponding box plots.
           """
        rankings = self.loadRankings(self.input, int(self.evalConfig["topKmax"]), False)
        dataset = pd.read_csv(self.dataset)

        #collect all top k ranked genes
        rankedGenes = set()
        for method in rankings.keys():
            rankedGenes = rankedGenes.union(set(rankings[method]))
        rankedGenes = list(rankedGenes)

        #compute the average fold change for every feature
        medianFoldChanges = {}
        averageFoldChanges = {}
        for gene in rankedGenes:
            try:
                avgFoldChange = sum(dataset[gene])/len(dataset[gene])
                medianFoldChange = np.median(dataset[gene])
                medianFoldChanges[gene] = medianFoldChange
                averageFoldChanges[gene] = avgFoldChange
            except:
                #we have extracted features for which no average fold change can be computed
                continue

        #create boxplots for all methods for average and median fold change
        methodsAvg = {}
        methodsMedians = {}
        for method in rankings.keys():
            genes = rankings[method]

            #write fold changes to one file per method
            filename = self.output + "foldChanges_" + method + ".csv"
            with open(filename, "w") as f:
                header = "gene,average fold change, median fold change\n"
                f.write(header)

                avgFoldChange = []
                medianFoldChange = []
                for gene in genes:
                    try:
                        avgFoldChange.append(averageFoldChanges[gene])
                        medianFoldChange.append(medianFoldChanges[gene])
                        #write data to file
                        line = gene + "," + str(averageFoldChanges[gene]) + "," + str(medianFoldChanges[gene]) + "\n"
                        f.write(line)
                    except:
                        # we have extracted features for which no average fold change can be computed
                        continue

            methodsAvg[method] = avgFoldChange
            methodsMedians[method] = medianFoldChange

        #create Boxplot for average and median gene fold changes
        self.drawBoxPlot( list(methodsAvg.values()), list(methodsAvg.keys()), "Average")
        self.drawBoxPlot(list(methodsMedians.values()), list(methodsMedians.keys()), "Median")

    def evaluate(self):
        """Runs evaluations on feature rankings based on what is specified in the config file.
           Currently, can compute feature overlaps, Kendall's correlation coefficient (W), and box plots for mean and median fold changes of selected features.
           """
        if "top_k_overlap" in self.metrics:
            self.generateOverlaps()
        if "kendall_w" in self.metrics:
            self.computeKendallsWScores()

        if "average_foldchange" in self.metrics:
            self.computeFoldChangeDiffs()

class CrossEvaluator(Evaluator):
    """Runs the evaluation across a second data set.
       Takes the top k ranked features, removes all other features from that second data set.
       Runs a :class:`ClassificationEvaluator` on that second data set with the selected features.

       :param input: absolute path to the directory where the second data set for cross-validation is located.
       :type input: str
       :param rankingsDir: absolute path to the directory containing all rankings.
       :type rankingsDir: str
       :param output: absolute path to the directory to which to write all classification results.
       :type output: str
       :param methodColors: Dictionary that assigns every (ranking) method a unique color (used for drawing subsequent plots).
       :type methodColors: dict
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
    """
    def __init__(self, input, rankingsDir, output, methodColors):
        self.rankingsDir = rankingsDir
        super().__init__(input, output, methodColors)

    def evaluate(self):
        """Runs crossClassification = takes the features selected on the original data set and uses them to classify a second (cross-validation) data set.
           """

        # reduce data set for crossEvaluation to selected genes
        reducedDatasetLocation = self.output + "reducedDataset/"
        attributeRemover = AttributeRemover(self.input, self.rankingsDir,
                                            benchutils.getConfigValue("Evaluation", "topKmax"), reducedDatasetLocation)
        attributeRemover.removeUnusedAttributes()

        # run evaluation
        evaluator = ClassificationEvaluator(reducedDatasetLocation,
                                            self.output + "classifications/", self.methodColors)
        evaluator.evaluate()


class AnnotationEvaluator(Evaluator):
    """Annotates and enriches feature rankings with EnrichR (https://maayanlab.cloud/Enrichr/).
       What library to be used for annotation must be specified in the config file.
       Can compute annotation and enrichment overlaps for different feature rankings.
       Annotation = annotate features with terms/information
       Enrichment = check what terms are enriched in a feature ranking and are related to multiple features.
       Overlaps then can show a) if feature rankings represent the same underlying processes via annotation (maybe although having selected different features), or b) if the underlying processes are equally strongly represented by checking the enrichment (maybe altough having seleced different features).

       :param input: absolute path to the directory where the second data set for cross-validation is located.
       :type input: str
       :param output: absolute path to the directory to which to write all classification results.
       :type output: str
       :param methodColors: dictionary that assigns every (ranking) method a unique color (used for drawing subsequent plots).
       :type methodColors: dict
       :param metrics: list of metrics to compute, to be configured in config.
       :type metrics: :class:`List` of str
       :param dataConfig: config parameters for the input dataset.
       :type dataConfig: dict
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
       """
    def __init__(self, input, output, methodColors):
        self.dataConfig = benchutils.getConfig("Dataset")
        self.metrics = benchutils.getConfigValue("Rankings", "metrics")
        super().__init__(input, output, methodColors)


    def countAnnotationPercentages(self, featureLists, inputDir):
        """Count the number of features (=number of lines in annotation file) that have been annotated and compute percentages.
           Write output to a file "annotationsPercentages.csv" in self.outputDir.

           :param featureLists: dictionary of lists of features per selection method.
           :type featureLists: dict
           :param inputDir: absolute path to directory containing annotation files.
           :type inputDir: str
           """
        annotatedGenes = {}
        for approach in featureLists.keys():

            filename = inputDir + approach + "_annotatedGenes.txt"
            numAnnotatedGenes = 0
            with open(filename, "r") as f:
                for line in f:
                    numAnnotatedGenes += 1

            annotatedGenes[approach] = numAnnotatedGenes

        # write file with annotation percentage
        annotationComparison = self.output + "annotationPercentages.csv"
        with open(annotationComparison, "w") as f:
            header = "gene\t% of genes annotated\n"
            f.write(header)
            for approach, numAnnotated in annotatedGenes.items():
                annotatedPercentage = (100 * numAnnotated) / int(self.evalConfig["topKmax"])
                line = approach + "\t" + str(annotatedPercentage) + "\n"
                f.write(line)


    def loadAnnotationFiles(self, inputDir,inputFiles):
        """Loads files with feature annotations.

           :param inputDir: absolute path to directory containing annotation files.
           :type inputDir: str
           :param inputFiles: list of annotation file names to load.
           :type inputFiles: :class:`List` of str
           :return: dictionary of annotation sets per selection method.
           :rtype: dict
           """

        featureLists = {}
        for filename in inputFiles:
            selectionMethod = "_".join(filename.split("_")[1:-1]) # get method name from filename without ending (format: top5_APPROACH_annotation.txt)
            fileContent = pd.read_csv(inputDir + filename, sep = "\t")
            itemsColumn = fileContent.columns[0]
            items = fileContent[itemsColumn]
            featureLists[selectionMethod] = set(items)
        return featureLists

    def computeOverlap(self, inputDir, fileSuffix):
        """Creates overlap plots for the available annotations/enrichments.
           For up to two rankings, use Python's matplotlib to create Venn diagrams.
           For three rankings and above, create UpsetR (https://github.com/hms-dbmi/UpSetR) diagrams via R.

           :param inputDir: absolute path to directory containing files for which to compute overlap.
           :type inputDir: str
           :param fileSuffix: suffix in filename to recognize the right files.
           :type fileSuffix: str
           """
        inputFiles = []
        for file in os.listdir(inputDir):
            if file.endswith(fileSuffix + ".txt"):
                #check if file contains more than header line to add it
                with open(inputDir + file, "r") as f:
                    content = f.readlines()
                    if len(content) > 1:
                        inputFiles.append(file)

        sizeOfSets = len(inputFiles)

        if ((sizeOfSets == 0) or (sizeOfSets == 1)):
            print("Something went wrong - you do not have enough files to compute overlap from!")
        elif (sizeOfSets == 2):  # if we have only 2 sets for intersection
            methods = self.loadAnnotationFiles(inputDir, inputFiles)
            colors = []
            methodNames = []
            for method in methods.keys():
                colors.append(self.methodColors[method])
                if len(method) > 20:
                    method = method.replace("_", "_\n")
                methodNames.append(method)
            venn2(methods.values(),  set_labels = methodNames, set_colors = colors, alpha = 1.0)
            matplots.pyplot.savefig(self.output + "overlaps" + fileSuffix + ".pdf")
            matplots.pyplot.clf()
        elif (sizeOfSets == 3):  # if we have only 3 sets for intersection
            methods = self.loadAnnotationFiles(inputDir, inputFiles)
            colors = []
            methodNames = []
            for method in methods.keys():
                colors.append(self.methodColors[method])
                if len(method) > 20:
                    method = method.replace("_", "_\n")
                methodNames.append(method)
            venn3(methods.values(), set_labels = methodNames, set_colors = colors, alpha = 1.0)
            matplots.pyplot.savefig(self.output + "overlaps" + fileSuffix + ".pdf")
            matplots.pyplot.clf()
        else:  # for more sets use UpSets package
            params = [self.output + "overlaps" + fileSuffix + ".pdf", self.evalConfig["topKmax"], inputDir]
            colors = ""
            filenames = []
            for file in inputFiles:
                method = "_".join(file.split("_")[1:-1])  # get method name from filename without ending (format: top5_APPROACH_annotation.txt)
                colors += "_" + self.methodColors[method]
                filenames.append(file)
            print("COLORS: " + colors)
            params.append(colors)
            params.extend(filenames)
            benchutils.runRCommand(self.rConfig, "UpsetDiagramCreation.R", params)

    def evaluate(self):
        """Runs the annotation/enrichment evaluation on the rankings.
           Depending on what was specified in the config file, annotate and/or enrich feature rankings and compute overlaps or percentages.
           Overlaps then can show a) if feature rankings represent the same underlying processes via annotation (maybe although having selected different features), or b) if the underlying processes are equally strongly represented by checking the enrichment (maybe altough having seleced different features).
           """
        geneLists = self.loadRankings(self.input, int(self.evalConfig["topKmax"]), False)
        outputPath = self.output + "top" + self.evalConfig["topKmax"] + "_"

        enrichr = knowledgebases.Enrichr()

        #if there is any measure mentioned related to annotation
        if "annotation" in self.metrics:
            # for every top k gene ranking, do enrichment analysis
            for approach, geneList in geneLists.items():
                outputFile = outputPath + approach
                enrichr.annotateGenes(geneList, outputFile)

        if "annotation_overlap" in self.metrics:
            # compute overlap of annotated genes
            self.computeOverlap(self.output, "_annotatedGenes")

        if "annotation_percentage" in self.metrics:
            self.countAnnotationPercentages(geneLists, outputPath)

        if "enrichment_overlap" in self.metrics:
            # for every top k gene ranking, do enrichment analysis
            for approach, geneList in geneLists.items():
                if (len(geneList) > 0):
                    outputFile = outputPath + approach
                    enrichr.enrichGeneset(geneList, outputFile)

            # compute overlap of annotated terms
            self.computeOverlap(self.output, "_enrichedTerms")



####### Creates density plots for input data set (if available, also for crossvalidation data set) #######
class DatasetEvaluator(Evaluator):
    """Creates plots regarding data set quality, currently: MDS, density, and box plots.
       Wrapper class because the actual evaluation and plot creation is done in an R script.

       :param input: absolute path to the directory where the input data set is located (for which to create the plots).
       :type input: str
       :param output: absolute path to the directory to which to save plots.
       :type output: str
       :param separator: separator character in data set to read it correctly.
       :type separator: str
       :param options: what plots to create, a list of method names that must be specified in the config file.
       :type options: list of str
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
       """
    def __init__(self, input, output, separator, options):
        #options must be a list of strings
        self.options = options
        self.separator = separator
        super().__init__(input, output, None)

    def evaluate(self):
        """Triggers the actual evaluation/plot generation in R.
           If a second data set for cross-validation was provided, also run the corresponding R script on that data set.
           """
        params = [self.input, self.output, self.separator, "TRUE"]
        params.extend(self.options)
        benchutils.runRCommand(benchutils.getConfig("R"), "DataCharacteristicsPlotting.R", params)

        if (benchutils.getConfigBoolean("Evaluation", "enableCrossEvaluation")):
            crossValidationFile = benchutils.getConfigValue("Evaluation", "crossEvaluationData")
            params = [crossValidationFile, self.output, self.separator, "TRUE"]
            params.extend(self.options)
            benchutils.runRCommand(benchutils.getConfig("R"), "DataCharacteristicsPlotting.R", params)

class KnowledgeBaseEvaluator(Evaluator):
    """Creates plots to evaluate knowledge base coverage.
       Queries the knowledge bases with the given search terms and checks how many genes or pathways are found.

       :param output: absolute path to the directory to which to save plots.
       :type output: str
       :param knowledgebases: a list of knowledgebases to test.
       :type knowledgebases: list of str
       :param searchterms: list of search terms for which to check knowledge base coverage.
       :type searchterms: list of str
       :param javaConfig: configuration parameters for java code (as specified in the config file).
       :type javaConfig: str
       :param rConfig: configuration parameters for R code (as specified in the config file).
       :type rConfig: str
       :param evalConfig: configuration parameters for evaluation, e.g. how many features to select (as specified in the config file).
       :type evalConfig: str
       :param classificationConfig: configuration parameters for classification, e.g. which classifiers to use (as specified in the config file).
       :type classificationConfig: str
       """
    def __init__(self, output, knowledgebases, searchterms):
        self.knowledgebases = self.createKnowledgeBases(knowledgebases)
        self.searchterms = searchterms
        super().__init__(None, output, None)

    def drawBoxPlot(self, stats, colIndex, filename, title, ylabel, colors):
        """Creates box plot from a data set.

           :param stats: statistics to plot.
           :type stats: :class:`pandas.DataFrame`
           :param colIndex: column index to use as column.
           :type colIndex: int
           :param filename: filename for the plot.
           :type filename: str
           :param title: title for the plot.
           :type title: str
           :param ylabel: label of y axis.
           :type ylabel: str
           :param colors: List of colors to use for the different search terms.
           :type colors: :class:`List` of str
           """
        pl = stats.boxplot(by =stats.columns[0], rot = 90, column = stats.columns[colIndex], patch_artist=True, return_type = "both",
                           boxprops = dict(color="k"), medianprops= dict(color="k"),whiskerprops= dict(color="k"), capprops= dict(color="k"), flierprops= dict(color="k", markeredgecolor="k"))  # fill with color
        bplot = pl.iloc[0]
        for patch, color in zip(bplot[1]['boxes'], colors):
            patch.set_facecolor(color)
        bplot[0].set_ylabel(ylabel)
        bplot[0].set_xlabel("")
        bplot[0].set_title(title)
        bplot[0].figure.texts = []
        ind = np.arange(1, len(colors)+1)
        bplot[0].set_xticks(ind)
        bplot[0].set_xticklabels(bplot[0].get_xticklabels())
        plt.gca().autoscale()

        matplots.pyplot.savefig(self.output + filename, bbox_inches = "tight")
        matplots.pyplot.clf()


    def drawBarPlot(self, stats, filename, title, ylabel, colors):
        """Creates a bar plot from a given data set.

           :param stats: DataFrame from which to draw the bar plot.
           :type stats: :class:`DataFrame`
           :param filename: filename for the plot.
           :type filename: str
           :param title: title for the plot.
           :type title: str
           :param ylabel: label of y axis.
           :type ylabel: str
           :param colors: List of colors to use.
           :type colors: :class:`List` of str
           """
        pl = stats.plot.bar(x=stats.index, rot = 90, color = colors)
        pl.set_ylabel(ylabel)
        pl.set_xlabel("")
        pl.set_title(title)
        pl.figure.texts = []
        ind = np.arange(stats.shape[0] + 1)
        pl.set_xticks(ind)
        pl.set_xticklabels(pl.get_xticklabels())

        matplots.pyplot.savefig(self.output + filename, bbox_inches = "tight")
        matplots.pyplot.clf()

    def createKnowledgeBases(self, knowledgebaseList):
        """Creates knowledge base objects from a given list.

           :param knowledgeBaseList: List of knowledge base names to create.
           :type knowledgeBaseList: :class:`List` of str.
           :return: List of knowledge base objects
           :rtype: :class:`List` of :class:`KnowledgeBase` or inheriting classes
           """

        kbfactory = knowledgebases.KnowledgeBaseFactory()
        kbs = []
        for kb in knowledgebaseList:
            kbs.append(kbfactory.createKnowledgeBase(kb))
        return kbs

    def checkCoverage(self, kb, colors, useIDs):
        """Checks the coverage for a given knowledge base and creates corresponding plots.

           :param kb: knowledge base object for which to check coverage.
           :type kb: :class:`knowledgebases.KnowledgeBase` or inheriting class
           :param colors: List of colors to use for plots.
           :type colors: :class:`List` of str
           """
        stats = pd.DataFrame()
        for term in self.searchterms:
            # query knowledge base
            geneSet = kb.getGeneScores([term])
            if useIDs:
                geneSet.insert(0, "search term", [int(self.searchterms.index(term) + 1)] * len(geneSet.index), True)
            else:
                geneSet.insert(0, "search term", [term] * len(geneSet.index), True)
            if stats.empty:
                stats = geneSet
            else:
                stats = stats.append(geneSet)

        stats.columns = ["search term", "gene", "score"]
        # write to file
        stats.to_csv(self.output + kb.getName() + "_GeneStats.csv", index=False)
        boxplotfile = kb.getName() + "_GeneScores.pdf"
        barplotfile = kb.getName() + "_NumberOfGenes.pdf"
        df_statscounts = stats["search term"].value_counts()
        if not stats.empty:
            self.drawBoxPlot(stats, 2, boxplotfile, kb.getName(),
                         "gene association scores", colors)
            self.drawBarPlot(df_statscounts, barplotfile, kb.getName(),
                         "number of genes per search term", colors)
        else:
            print("NO RESULTS FOR SEARCH TERMS, SO NO PLOTS GENERATED.")


    def checkPathwayCoverage(self, kb, colors, useIDs):
        """Checks the pathway coverage for a given knowledge base and creates corresponding plots.

           :param kb: knowledge base object for which to check pathway coverage.
           :type kb: :class:`knowledgebases.KnowledgeBase` or inheriting class
           :param colors: List of colors to use for plots.
           :type colors: :class:`List` of str
           """
        stats = []
        for term in self.searchterms:
            #query knowledge base
            pathways = kb.getRelevantPathways([term])
            for pathwayName, value in pathways.items():
                #numGenes = len(pathway.getNodes())
                numGenes = value.vcount
                #pathwayName = pathway.name
                #evtl. score attribut?
                if useIDs:
                    stats.append((int(self.searchterms.index(term) + 1), pathwayName, numGenes))
                else:
                    stats.append((term, pathwayName, numGenes))

        #make dataframe from list
        df_stats = pd.DataFrame(stats, columns = ["search term", "pathway", "#genes"])
        #write to file
        df_stats.to_csv(self.output + kb.getName() + "_PathwayStats.csv", index = False)
        boxplotfile = kb.getName() + "_PathwaySizes.pdf"
        barplotfile = kb.getName() + "_NumberOfPathways.pdf"
        df_statscounts = df_stats["search term"].value_counts()

        if not df_stats.empty:
            self.drawBoxPlot(df_stats, 2, boxplotfile, kb.getName() + ": Pathway sizes per search term",
                             "number of genes in pathway", colors)
            self.drawBarPlot(df_statscounts, barplotfile, kb.getName() + ": Number of pathways per search term",
                             "number of pathways", colors)
        else:
            print("NO RESULTS FOR SEARCH TERMS, SO NO PLOTS GENERATED.")

    def evaluate(self):
        """Evaluates every given knowledge base and checks how many genes and pathways (and how large they are) are in there for the given search terms.
           Creates corresponding plots.
           """
        #set colors for every search term
        colors = []

        #check if the individual length of a search term is longer than 20
        #map them to IDs then instead to avoid too long axis labels to be plotted
        maxLength = len(max(self.searchterms, key=len))
        useIDs = False
        if maxLength > 15:
            useIDs = True
            term_df = pd.DataFrame(self.searchterms, columns=['search term'])
            term_df.index = term_df.index + 1
            term_df.to_csv(self.output + "searchterm_IDs.txt")


        #if we have more than 12 search terms we need a color map with more colors
        if len(self.searchterms) <= 12:
            colorPalette = list(plt.get_cmap("Paired").colors)
        else:
            #create color palette with as many colors as search terms from a cyclic colormap
            cmap = plt.cm.get_cmap("hsv", len(self.searchterms))
            colorPalette = []
            for i in range(0, len(self.searchterms)):
                colorPalette.append(cmap(i))

        for term in self.searchterms:
            labelColor = random.choice(colorPalette)
            colorPalette.remove(labelColor)
            colors.append(labelColor)

        for kb in self.knowledgebases:
            print("Draw plots for " + kb.getName() + "...")
            if kb.hasPathways():
                self.checkPathwayCoverage(kb, colors, useIDs)

            if kb.hasGenes():

                self.checkCoverage(kb, colors, useIDs)

        print("...finished.")
