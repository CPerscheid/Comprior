import datetime, time, os
import random
import multiprocessing
from matplotlib import colors as mcolors
import benchutils
import preprocessing
import featureselection
import evaluation
import argparse
import pandas as pd

MARKERS = [".", "o", "v", "^", "<", ">", "1", "s", "p", "P", "*", "h", "+", "x", "d", "D"]

class Pipeline():
    """Class that executes the complete benchmarking pipeline.

       :param outputRootPath: absolute path to the overall output directory (will be extended by own folders by every :class:`evaluation.Evaluator`).
       :type outputRootPath: str
       """
    def __init__(self, userConfig):
        self.outputRootPath = self.prepareExecution(userConfig)

        super().__init__()

    def prepareExecution(self, userConfig):
        """Prepares the pipeline execution by loading the configuration file, clearing intermediate directories, and creating output directories.

           :param userConfig: absolute path to an additional user configuration file (config.ini will always be used by default) to overwrite default configuration.
           :type userConfig: str
           """
        print("######################## LOAD CONFIG... ########################")
        self.loadConfig(userConfig)
        print("######################## ... FINISHED ########################")

        print("######################## PREPARE DIRECTORIES... ########################")
        outputRootPath = self.prepareDirectories()
        print("######################## ... FINISHED ########################")
        return outputRootPath

    def evaluateInputData(self, inputfile):
        """Run :class:`evaluation.DatasetEvaluator` to create plots as specified by the config's Evaluation-preanalysis parameter.

            :param inputfile: absolute path to the input data set to be analyzed.
            :type inputfile: str
            """
        opts = benchutils.getConfigValue("Evaluation", "preanalysis_plots").split(" ")
        dataEvaluator = evaluation.DatasetEvaluator(inputfile, self.outputRootPath + benchutils.getConfigValue("Evaluation", "preanalysis") , ",", opts)
        dataEvaluator.evaluate()

    def evaluateKnowledgeBases(self, labeledInputDataPath):
        """Evaluates knowledge base coverage for all knowledge bases that are used in the specified feature selection methods.
           Uses the class labels and alternativeSearchTerms from the config, queries the knowledge bases and creates corresponding plots regarding coverage of theses search terms.

           :param labeledInputDataPath: absolute path to the labeled input data set.
           :type labeledInputDataPath: str
           """

        if (benchutils.getConfigBoolean("Evaluation", "evaluateKBcoverage")):
            output = self.outputRootPath + benchutils.getConfigValue("Evaluation", "preanalysis")

            #get all knowledgebases that are used by selected approaches
            methods = []
            methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "combining_methods").split(" "))
            methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "modifying_methods").split(" "))
            methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "network_methods").split(" "))
            # remove empty values in case a methods list was empty
            methods = [value for value in methods if value != ""]

            knowledgebases =[method.split("_")[-1] for method in methods]

            #get all searchterms from config and classlabels
            alternativeTerms = benchutils.getConfigValue("Dataset", "alternativeSearchTerms").split(" ")
            altTerms = []
            for term in alternativeTerms:
                if len(term) > 1:
                    altTerms.append(term.replace("_", " "))
            #only read in the first column with the class labels
            classLabels = pd.read_csv(labeledInputDataPath, usecols=[1], squeeze = True)
            searchTerms = list(classLabels.unique())
            searchTerms.extend(altTerms)


            dataEvaluator = evaluation.KnowledgeBaseEvaluator(output, knowledgebases, searchTerms)
            dataEvaluator.evaluate()

    def runFeatureSelector(self, selector, datasetLocation, outputDir, loggingDir):
        """Runs a given feature selector.

           :param selector: Any feature selector that inherits from :class:`featureselection.FeatureSelector`.
           :type selector: :class:`featureselection.FeatureSelector`
           :param datasetLocation: absolute path to the input data set (from which features should be selected).
           :type datasetLocation: str
           :param outputDir: absolute path to the selector's output directory (where ranking will be written to).
           :type outputDir: str
           """
        selector.setParams(datasetLocation, outputDir, loggingDir)
        selector.selectFeatures()

    def selectFeatures(self, datasetLocation):
        """Creates and runs all feature selectors that are listed in the config file.
           Applies parallelization by running as much feature selectors in parallel as stated in the config's General-->numCores attribute.

           :param datasetLocation: absolute path to the input data set (from which features should be selected).
           :type datasetLocation: str
           :param outputRootPath: absolute path to the selector's output directory (where ranking will be written to).
           :type outputRootPath: str
           :return: absolute path to directory that contains generated feature rankings.
           :rtype: str
           """
        outputDir = self.outputRootPath + benchutils.getConfigValue("Gene Selection - General", "outputDirectory")
        # create directory for time logging files
        loggingDir = self.outputRootPath + "timeLogs/"
        benchutils.createDirectory(loggingDir)

        methods = []
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "traditional_methods").split(" "))
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "combining_methods").split(" "))
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "modifying_methods").split(" "))
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "network_methods").split(" "))
        # remove empty values in case a methods list was empty
        methods = [value for value in methods if value != ""]

        selectorFactory = featureselection.FeatureSelectorFactory()

        try:
            numCores = int(benchutils.getConfigValue("General", "numCores"))
        except:
            print("numCores must be an integeger value. Exit program.")
            exit()

        rounds = int(len(methods) / numCores)
        #walk through every method and create a gene selector
        #parallelize, but only run at max as much threads as cpus in parallel, also to avoid running out of space
        for j in range(rounds):
            # create threadpool
            threads = [None] * numCores
            for i in range(numCores):
                selector = selectorFactory.createFeatureSelector(methods[(j * numCores) + i])
                self.runFeatureSelector(selector, datasetLocation, outputDir, loggingDir)
                #spawn new process for actual gene selection
                #print("spawn process number " + str((j * numCores) + i) + ": " + methods[(j * numCores) + i])
                #p = multiprocessing.Process(target=self.runFeatureSelector, args=(selector, datasetLocation, outputDir, loggingDir))
                #threads[i] = p
                #p.start()

                # wait for all threads to finish
            #for thr in threads:
                #print("join thread...")
                #thr.join()
                ##print("... finished")

        #if there are remaining threads, start them
        remaining_threads = len(methods) - (rounds * numCores)
        #print("remaining threads: " + str(remaining_threads))
        if remaining_threads > 0:
            # create threadpool
            threads = [None] * remaining_threads
            for i in range(1, remaining_threads + 1):
                selector = selectorFactory.createFeatureSelector(methods[len(methods) - i])
                #print("spawn process number " + str(len(methods) - i) + ": " + methods[len(methods) - i])
                self.runFeatureSelector(selector, datasetLocation, outputDir, loggingDir)
                #spawn new process for actual gene selection
                #p = multiprocessing.Process(target=self.runFeatureSelector, args=(selector, datasetLocation, outputDir, loggingDir))
                #threads[i-1] = p
                #p.start()

                # wait for all threads to finish
            #for thr in threads:
                #print("join thread...")
                #thr.join()
                #print("... finished")

        return outputDir

    def assignColors(self, methods):
        """Assigns each (feature selection) method a unique color.
           Will be delivered later on to every :class:`evaluation.Evaluator` instance to create visualizations with consistent coloring for evaluated approaches.

           :param methods: List of method names.
           :type methods: :class:`List` of str
           :return: Dictionary containing hex color codes for every method
           :rtype: dict
           """
        colors = {}
        colorPalette = dict(**mcolors.CSS4_COLORS)

        colorNames = list(colorPalette.keys())
        for method in methods:
            labelColor = random.choice(colorNames)
            colorNames.remove(labelColor)
            #colors[method] = labelColor
            colors[method] = mcolors.to_hex(labelColor)

        return colors

    def assignMarkers(self, approaches):
        """Assigns each (feature selection) method a unique color.
           Will be delivered later on to every :class:`evaluation.Evaluator` instance to create visualizations with consistent coloring for evaluated approaches.

           :param methods: List of method names.
           :type methods: :class:`List` of str
           :return: Dictionary containing hex color codes for every method
           :rtype: dict
           """
        markers = {}
        for approach in approaches:
            markers[approach] = random.choice(MARKERS)

        return markers

    def evaluateBiomarkers(self, inputDir, dataset, rankingsDir):
        """Covers the evaluation phase.
           Processes input data to only contain the top k selected features per feature selection approach via the :class:`evaluation.AttributeRemover`.
           Runs all selected evaluation strategies that cover assessment of rankings (:class:`evaluation.RankingsEvaluator`), annotations(:class:`evaluation.AnnotationEvaluator`), and classification performance (:class:`evaluation.ClassificationEvaluator`).
           If selected, also conducts cross-validation across data sets with :class:`evaluation.CrossEvaluator`.

           :param inputDir: absolute path to the directory where input data sets are located (for :class:`evaluation.AttributeRemover`).
           :type inputDir: str
           :param dataset: absolute file path to the input data set (from which features should be selected).
           :type dataset: str
           :param rankingsDir: absolute path to the directory that contains all rankings.
           :type rankingsDir: str
           """

        methods = []
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "traditional_methods").split(" "))
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "combining_methods").split(" "))
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "modifying_methods").split(" "))
        methods.extend(benchutils.getConfigValue("Gene Selection - Methods", "network_methods").split(" "))
        # remove empty values in case a methods list was empty
        methods = [value for value in methods if value != ""]

        methodColors = self.assignColors(methods)
        methodMarkers = self.assignMarkers(methods)

        #################################
        ### RANKINGS EVALUATION ###
        #################################

        rankingsEvaluator = evaluation.RankingsEvaluator(rankingsDir, dataset,
                                                         self.outputRootPath + benchutils.getConfigValue("Rankings", "metricsDir"), methodColors)
        rankingsEvaluator.evaluate()

        annotationEvaluator = evaluation.AnnotationEvaluator(rankingsDir, self.outputRootPath + benchutils.getConfigValue("Rankings",
                                                                                                            "annotationsDir"), methodColors)
        annotationEvaluator.evaluate()

        #################################
        ### CLASSIFICATION EVALUATION ###
        #################################
        #attributeRemover = evaluation.AttributeRemover(inputDir,
        #                                               self.outputRootPath + benchutils.getConfigValue(
        #                                                   "Gene Selection - General",
        #                                                   "outputDirectory"),
        #                                               benchutils.getConfigValue("Evaluation", "topKmax"),
        #                                               self.outputRootPath + benchutils.getConfigValue("Evaluation",
        #                                                                                              "reducedDataset"))
        #attributeRemover.removeUnusedAttributes()

        if benchutils.getConfigBoolean("Evaluation", "enableClassification"):
            datasetDir = inputDir
            rankingsDir = self.outputRootPath + benchutils.getConfigValue("Gene Selection - General","outputDirectory")
            reducedDatasetDir = self.outputRootPath + benchutils.getConfigValue("Evaluation", "reducedDataset")
            metricsDir = self.outputRootPath + benchutils.getConfigValue("Classification", "metricsDir")
            classificationEvaluator = evaluation.ClassificationEvaluator(datasetDir, rankingsDir, reducedDatasetDir, metricsDir, methodColors, methodMarkers)

            #classificationEvaluator = evaluation.ClassificationEvaluator(
            #    self.outputRootPath + benchutils.getConfigValue("Evaluation", "reducedDataset"),
            #    self.outputRootPath + benchutils.getConfigValue("Classification", "metricsDir"), methodColors)
            classificationEvaluator.evaluate()

        ##########################################
        ### CROSS-VALIDATION ON SECOND DATASET ###
        ##########################################
        if benchutils.getConfigBoolean("Evaluation", "enableCrossEvaluation"):
            crossValFileDir = benchutils.getConfigValue("General", "crossVal_preprocessing") + "ready/"
            outputDir = self.outputRootPath + benchutils.getConfigValue("Classification", "crossEvaluationDir")
            reducedDatasetDir = outputDir + "/reducedData/"
            resultsDir = outputDir + "/classification/"

            robustnessEvaluator = evaluation.ClassificationEvaluator(crossValFileDir, rankingsDir, reducedDatasetDir, resultsDir, methodColors, methodMarkers)
            robustnessEvaluator.evaluate()

    def preprocessData(self):
        """Preprocesses the input data set specified in the config file.
           Preprocessing consists of a) transposing the data so that features are in the columns (if necessary), b) mapping the features to the right format (if necessary), c) labeling the data with the user-specified metadata attribute, d) filtering features or samples that have too few information (optional, specified via config), and finally e) putting the analysis-ready data set to the right location for further processing.

           :return: A tuple consisting of the absolute path to the analysis-ready data set and the absolute path to the mapped input final_filename and mapped_input
           :rtype: tuple(str,str)
           """
        #####################
        ### PREPROCESSING ###
        #####################

        input = benchutils.getConfigValue("Dataset", "input")
        input_metadata = benchutils.getConfigValue("Dataset", "metadata")
        intermediate_output = benchutils.getConfigValue("General", "preprocessing") + "preprocessed/"
        final_output = benchutils.getConfigValue("General", "preprocessing") + "ready/"
        sep = benchutils.getConfigValue("Dataset", "dataSeparator")
        currentIDFormat = benchutils.getConfigValue("Dataset", "currentGeneIDFormat")
        desiredIDFormat = benchutils.getConfigValue("Dataset", "finalGeneIDFormat")

        #get original filename
        original_filename = os.path.basename(input)

        # THIS ONE MUST ALWAYS BE THE FIRST PREPROCESSING STEP because it potentially changes the separators used in the data
        # transpose data matrix if genes are not located in the columns, replace custom separators to the framework-specific ones
        dataFormatter = preprocessing.DataTransformationPreprocessor(input, input_metadata, intermediate_output, sep)
        transposed_input = dataFormatter.preprocess()

        mappingPreprocessor = preprocessing.MappingPreprocessor(transposed_input, intermediate_output, currentIDFormat,
                                                                desiredIDFormat, False)
        mapped_input = mappingPreprocessor.preprocess()

        # add disease type from metadata to main data set
        metadataAnnotator = preprocessing.MetaDataPreprocessor(mapped_input, input_metadata, intermediate_output, sep)
        labeled_input = metadataAnnotator.preprocess()

        filterPreprocessor = preprocessing.FilterPreprocessor(labeled_input, input_metadata, intermediate_output)
        filtered_input = filterPreprocessor.preprocess()

        #move last processed file into ready directory with original filename as prefix
        final_filename = final_output + original_filename
        datasetPreprocessor = preprocessing.DataMovePreprocessor(filtered_input, final_filename)
        datasetPreprocessor.preprocess()

        # if cross-validation is enabled, map the dataset for cross-validation correctly and move it to the right directory
        if (benchutils.getConfigBoolean("Evaluation", "enableCrossEvaluation")):
            crossValidationFile = benchutils.getConfigValue("Evaluation", "crossEvaluationData")
            crossValFileName = os.path.basename(crossValidationFile)
            crossValidationPath = benchutils.getConfigValue("General", "crossVal_preprocessing") + "preprocessed/"
            crossValIDFormat = benchutils.getConfigValue("Evaluation", "crossEvaluationGeneIDFormat")
            crossVal_mappingPreprocessor = preprocessing.MappingPreprocessor(crossValidationFile, crossValidationPath,
                                                                    crossValIDFormat,desiredIDFormat, True)
            mapped_crossValdata = crossVal_mappingPreprocessor.preprocess()
            crossval_final_output = benchutils.getConfigValue("General", "crossVal_preprocessing") + "ready/"
            crossval_final_filename = crossval_final_output + crossValFileName
            datasetPreprocessor = preprocessing.DataMovePreprocessor(mapped_crossValdata, crossval_final_filename)
            datasetPreprocessor.preprocess()


        return final_filename, mapped_input

    def loadConfig(self, userConfig):
        """Loads the config files.
           config.ini will always be loaded as default config file, all other config files provided by userConfig overwrite corresponding values.

           :param userConfig: absolute path(s) to user-defined config files that should be used. If config files specify the same parameter, the value specified by the last config file in the list will be used.
           :type userConfig: str or :class:`List` of str, optional
           """
        if userConfig:
            #config can read in a list of multiple config files one after the other. if they have overlapping keywords, the values from the config last read are kept.
            benchutils.loadConfig(["../../configs/config.ini", userConfig])
        else:
            benchutils.loadConfig("../../configs/config.ini")

    def prepareDirectories(self):
        """Prepares directory structure for benchmarking run.
           Creates all necessary directories in the output folder.
           Also cleans up intermediate directory so that no old data is accidentially used.

           :return: absolute path to the directory where all results from this run will be stored.
           :rtype: str
           """
        ##########################################
        ###  CLEANUP RESULTS FROM FORMER RUNS  ###
        ##########################################

        # create directory for intermediate results from knowledge bases
        benchutils.createDirectory(benchutils.getConfigValue("General", "intermediateDir"))
        benchutils.createDirectory(benchutils.getConfigValue("General", "preprocessing"))
        benchutils.createDirectory(benchutils.getConfigValue("General", "preprocessing") + "preprocessed/")
        benchutils.createDirectory(benchutils.getConfigValue("General", "preprocessing") + "ready/")
        benchutils.createDirectory(benchutils.getConfigValue("General", "crossVal_preprocessing") + "preprocessed/")
        benchutils.createDirectory(benchutils.getConfigValue("General", "crossVal_preprocessing") + "ready/")
        benchutils.createDirectory(benchutils.getConfigValue("General", "externalKbDir"))
        benchutils.createDirectory(benchutils.getConfigValue("General", "intermediateDir") + "identifierMappings/")


        benchutils.cleanupResults()
        outputPath = benchutils.getConfigValue("General", "resultsdir") + benchutils.getConfigValue("General", "outputDir_name") + "/"
        # create root directory for final analysis outputs
        #rename output folder if it already exists
        i = 1
        while os.path.exists(outputPath):
            dir = benchutils.getConfigValue("General", "outputDir_name").strip("/")
            outputPath = benchutils.getConfigValue("General", "resultsdir") + dir + str(i)+ "/"
            i += 1

        benchutils.createDirectory(outputPath)

        # create new directory for ranking and evaluation results
        benchutils.createDirectory(outputPath + benchutils.getConfigValue("Evaluation", "results"))
        benchutils.createDirectory(outputPath + benchutils.getConfigValue("Evaluation", "reducedDataset"))
        #create directory for preanalysis plots
        benchutils.createDirectory(outputPath + benchutils.getConfigValue("Evaluation", "preanalysis"))

        # create directory for ranking results
        # ranking analysis will always be conducted
        benchutils.createDirectory(outputPath + benchutils.getConfigValue("Rankings", "metricsDir"))
        benchutils.createDirectory(outputPath + benchutils.getConfigValue("Rankings", "annotationsDir"))

        # create directory for classification results
        if (benchutils.getConfigBoolean("Evaluation", "enableClassification")):
            benchutils.createDirectory(outputPath + benchutils.getConfigValue("Classification", "metricsDir"))
            if benchutils.getConfigBoolean("Evaluation", "enableCrossEvaluation"):
                benchutils.createDirectory(outputPath + benchutils.getConfigValue("Classification", "crossEvaluationDir"))
                benchutils.createDirectory(
                    outputPath + benchutils.getConfigValue("Classification", "crossEvaluationDir") + "reducedData/")
                benchutils.createDirectory(
                    outputPath + benchutils.getConfigValue("Classification", "crossEvaluationDir") + "classification/")

        # create directory for prediction results
        if (benchutils.getConfigBoolean("Evaluation", "enablePrediction")):
            benchutils.createDirectory(outputPath + benchutils.getConfigValue("Prediction", "metricsDir"))
            if benchutils.getConfigBoolean("Evaluation", "doCrossEvaluation"):
                benchutils.createDirectory(outputPath + benchutils.getConfigValue("Prediction", "crossEvaluationDir"))
                benchutils.createDirectory(
                    outputPath + benchutils.getConfigValue("Prediction", "crossEvaluationDir") + "reducedDataset/")

        benchutils.createDirectory(outputPath + benchutils.getConfigValue("Gene Selection - General", "outputDirectory"))

        return outputPath

    def executePipeline(self):
        """The entry point for the overall benchmarking process.
           This method is invoked when running the framework, and from here all other steps of the benchmarking process are encapsulated in own methods.

        :param userConfig: absolute path to an additional user configuration file (config.ini will always be used by default) to overwrite default configuration.
        :type userConfig: str
        """
        print("######################## PREPROCESS DATA... ########################")
        datasetLocation, mappedLocation = self.preprocessData()
        print("######################## ... FINISHED ########################")

        print("######################## EVALUATE INPUT DATA... ########################")
        self.evaluateInputData(datasetLocation)
        print("######################## ... FINISHED ########################")

        print("######################## EVALUATE KNOWLEDGE BASES... ########################")
        self.evaluateKnowledgeBases(datasetLocation)
        print("######################## ... FINISHED ########################")

        print("######################## SELECT FEATURES... ########################")
        outputDir = self.selectFeatures(datasetLocation)
        print("######################## ... FINISHED ########################")

        print("######################## EVALUATE BIOMARKERS... ########################")
        dataPath = os.path.dirname(datasetLocation)
        self.evaluateBiomarkers(dataPath, mappedLocation, outputDir)
        print("######################## ... FINISHED ########################")

if __name__ == '__main__':
    # parse input params
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, help='User-specific config file that overwrites parts of the original config file.')


    args = parser.parse_args()
    pipeline = Pipeline(args.config)
    pipeline.executePipeline()
