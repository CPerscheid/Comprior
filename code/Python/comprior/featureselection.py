import abc
import time, random
import pandas as pd
import os
import numpy as np
import benchutils as utils
import knowledgebases
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_selection import RFE, VarianceThreshold
from sklearn import preprocessing


class FeatureSelectorFactory():
    """Singleton class.
       Python code encapsulates it in a way that is not shown in Sphinx, so have a look at the descriptions in the source code.

       Creates feature selector object based on a given name.
       New feature selection approaches must be registered here.
       Names for feature selectors must follow to a particular scheme, with keywords separated by _:
       - first keyword is the actual selector name
       - if needed, second keyword is the knowledge base
       - if needed, third keyword is the (traditional) approach to be combined
       Examples:
       - Traditional Approaches have only one keyword, e.g. InfoGain or ANOVA
       - LassoPenalty_KEGG provides KEGG information to the LassoPenalty feature selection approach
       - Weighted_KEGG_InfoGain --> Factory creates an instance of KBweightedSelector which uses KEGG as knowledge base and InfoGain as traditional selector.
       While the focus here lies on the combination of traditional approaches with prior biological knowledge, it is theoretically possible to use ANY selector object for combination that inherits from :class:`FeatureSelector`.

       :param config: configuration parameters for UMLS web service as specified in config file.
       :type config: dict
       """
    class __FeatureSelectorFactory():

        def createFeatureSelector(self, name):
            """Create selector from a given name.
               Separates creation process into (traditional) approaches (only one keyword), approaches requiring a knowledge base, and approaches requiring both a knowledge base and another selector, e.g. a traditional one.

               :param name: selector name following the naming conventions: first keyword is the actual selector name, second keyword is the knowledge base, third keyword another selector to combine. Keywords must be separated by "_". Example: Weighted_KEGG_InfoGain
               :type name: str
               :return: instance of a feature selector implementation.
               :rtype: :class:`FeatureSelector` or inheriting class
               """
            parts = name.split("_")

            if len(parts) == 1:
                return self.createTraditionalSelector(name)
            elif len(parts) == 2:
                return self.createIntegrativeSelector(parts[0], parts[1])
            elif len(parts) == 3:
                return self.createCombinedSelector(parts[0], parts[1], parts[2])

            utils.logError("ERROR: The provided selector name does not correspond to the expected format. "
                  "A selector name should consist of one or more keywords separated by _. "
                  "The first keyword is the actual approach (e.g. weighted, or a traditional approach), "
                  "the second keyword corresponds to a knowledge base to use (e.g. KEGG),"
                  "the third keyword corresponds to a traditional selector to use (e.g. when using a modifying or combining approach")
            exit()

        def createTraditionalSelector(self, selectorName):
            """Creates a (traditional) selector (without a knowledge base) from a given name.
               Register new implementations of a (traditional) selector here.
               Stops processing if the selector could not be found.

               :param selectorName: selector name
               :type selectorName: str
               :return: instance of a feature selector implementation.
               :rtype: :class:`FeatureSelector` or inheriting class
               """
            if selectorName == "Random":
                return RandomSelector()
            if selectorName == "VB-FS":
                return VarianceSelector()
            if selectorName == "Variance":
                return Variance2Selector()
            if selectorName == "ANOVA":
                return AnovaSelector()
            if selectorName == "mRMR":
                return MRMRSelector()
            if selectorName == "SVMpRFE":
                return SVMRFESelector()
            # RUN WEKA FEATURE SELECTION AS SELECTED
            if selectorName == "InfoGain":
                return InfoGainSelector()
            if selectorName == "ReliefF":
                return ReliefFSelector()
            #if "-RFE" in selectorName or "-SFS" in selectorName: -- SFS is currently disabled because sometimes the coef_ param is missing and error is thrown
            if "-RFE" in selectorName:
                return WrapperSelector(selectorName)
            if selectorName == "Lasso":
                return LassoSelector()
            if selectorName == "RandomForest":
                return RandomForestSelector()
            utils.logError("ERROR: The listed selector " + selectorName + " is not available. See the documentation for available selectors. Stop execution.")
            exit()

        def createIntegrativeSelector(self, selectorName, kb):
            """Creates a feature selector using a knowledge base from the given selector and knowledge base names.
               Register new implementations of a prior knowledge selector here that does not requires a (traditional) selector.
               Stops processing if the selector could not be found.

               :param selectorName: selector name
               :type selectorName: str
               :param kb: knowledge base name
               :type kb: str
               :return: instance of a feature selector implementation.
               :rtype: :class:`FeatureSelector` or inheriting class
               """
            kbfactory = knowledgebases.KnowledgeBaseFactory()
            knowledgebase = kbfactory.createKnowledgeBase(kb)

            if selectorName == "NetworkActivity":
                featuremapper = PathwayActivityMapper()
                return NetworkActivitySelector(knowledgebase, featuremapper)
            if selectorName == "CorgsNetworkActivity":
                featuremapper = CORGSActivityMapper()
                return NetworkActivitySelector(knowledgebase, featuremapper)
            if selectorName == "LassoPenalty":
                return LassoPenalty(knowledgebase)
            if selectorName == "KBonly":
                return KbSelector(knowledgebase)
            utils.logError("ERROR: The listed selector " + selectorName + " is not available. See the documentation for available selectors. Stop execution.")
            exit()

        def createCombinedSelector(self, selectorName, trad, kb):
            """Creates a feature selector that combines a knowledge base and another feature selector based on the given names.
               Register new implementations of a prior knowledge selector that requires another selector here.
               Stops processing if the selector could not be found.

               :param selectorName: selector name
               :type selectorName: str
               :param trad: name of the (traditional) feature selector.
               :type trad: str
               :param kb: knowledge base name
               :type kb: str
               :return: instance of a feature selector implementation.
               :rtype: :class:`FeatureSelector` or inheriting class
               """
            tradSelector = self.createTraditionalSelector(trad)
            kbfactory = knowledgebases.KnowledgeBaseFactory()
            knowledgebase = kbfactory.createKnowledgeBase(kb)

            if selectorName == "Postfilter":
                return PostFilterSelector(knowledgebase, tradSelector)
            if selectorName == "Prefilter":
                return PreFilterSelector(knowledgebase, tradSelector)
            if selectorName == "Extension":
                return ExtensionSelector(knowledgebase, tradSelector)
            if selectorName == "Weighted":
                return KBweightedSelector(knowledgebase, tradSelector)

            utils.logError("ERROR: The listed selector " + selectorName + " is not available. See the documentation for available selectors. Stop execution.")
            exit()

    instance = None

    def __init__(self):
        if not FeatureSelectorFactory.instance:
            FeatureSelectorFactory.instance = FeatureSelectorFactory.__FeatureSelectorFactory()

    def __getattr__(self, name):
        return getattr(self.instance, name)

class FeatureSelector:
    """Abstract super class for feature selection functionality.
       Every feature selection class has to inherit from this class and implement its :meth:`FeatureSelector.selectFeatures` method and - if necessary - its :meth:`FeatureSelector.setParams` method.
       Once created, feature selection can be triggered by first setting parameters (input, output, etc) as needed with :meth:`FeatureSelector.setParams`.
       The actual feature selection is triggered by invoking :meth:`FeatureSelector.selectFeatures`.

       :param input: absolute path to input dataset.
       :type input: str
       :param output: absolute path to output directory (where the ranking will be stored).
       :type output: str
       :param dataset: the dataset for which to select features. Will be loaded dynamically based on self.input at first usage.
       :type dataset: :class:`pandas.DataFrame`
       :param dataConfig: config parameters for input data set.
       :type dataConfig: dict
       :param name: selector name
       :type name: str
       """

    def __init__(self, name):
        self.input = None
        self.output = None
        self.dataset = None
        self.loggingDir = None
        self.dataConfig = utils.getConfig("Dataset")
        self.setTimeLogs(utils.createTimeLog())
        self.enableLogFlush()
        self.name = name
        super().__init__()

    @abc.abstractmethod
    def selectFeatures(self):
        """Abstract.
           Invoke feature selection functionality in this method when implementing a new selector

           :return: absolute path to the output ranking file.
           :rtype: str
           """
        pass

    def getTimeLogs(self):
        """Gets all logs for this selector.

           :return: dataframe of logged events containing start/end time, duration, and a short description.
           :rtype: :class:`pandas.DataFrame`
           """
        return self.timeLogs

    def setTimeLogs(self, newTimeLogs):
        """Overwrites the current logs with new ones.

           :param newTimeLogs: new dataframe of logged events containing start/end time, duration, and a short description.
           :type newTimeLogs: :class:`pandas.DataFrame`
           """
        self.timeLogs = newTimeLogs

    def disableLogFlush(self):
        """Disables log flushing (i.e., writing the log to a separate file) of the selector at the end of feature selection.
           This is needed when a :class:`CombiningSelector` uses a second selector and wants to avoid that its log messages are written, potentially overwriting logs from another selector of the same name.
           """
        self.enableLogFlush = False

    def enableLogFlush(self):
        """Enables log flushing, i.e. writing the logs to a separate file at the end of feature selection.
           """
        self.enableLogFlush = True

    def getName(self):
        """Gets the selector's name.

           :return: selector name.
           :rtype: str
           """
        return self.name

    def getData(self):
        """Gets the labeled dataset from which to select features.

           :return: dataframe containing the dataset with class labels.
           :rtype: :class:`pandas.DataFrame`
           """
        if self.dataset is None:
            self.dataset = pd.read_csv(self.input, index_col=0)
        return self.dataset

    def getUnlabeledData(self):
        """Gets the dataset without labels.

           :return: dataframe containing the dataset without class labels.
           :rtype: :class:`pandas.DataFrame`
           """
        dataset = self.getData()
        return dataset.loc[:, dataset.columns != "classLabel"]

    def getFeatures(self):
        """Gets features from the dataset.

           :return: list of features.
           :rtype: list of str
           """
        return self.getData().columns[1:]

    def getUniqueLabels(self):
        """Gets the unique class labels available in the dataset.

           :return: list of distinct class labels.
           :rtype: list of str
           """

        return list(set(self.getLabels()))

    def getLabels(self):
        """Gets the labels in the data set.

           :return: all labels from the dataset.
           :rtype: list of str
           """
        return list(self.getData()["classLabel"])

    def setParams(self, inputPath, outputDir, loggingDir):
        """Sets parameters for the feature selection run: path to the input datast and path to the output directory.

           :param inputPath: absolute path to the input file containing the dataset for analysis.
           :type inputPath: str
           :param outputDir: absolute path to the output directory (where to store the ranking)
           :type outputDir: str
           :param loggingDir: absolute path to the logging directory (where to store log files)
           :type loggingDir: str
           """
        self.input = inputPath
        self.output = outputDir
        self.loggingDir = loggingDir

    def writeRankingToFile(self, ranking, outputFile, index = False):
        """Writes a given ranking to a specified file.

           :param ranking: dataframe with the ranking.
           :type ranking: :class:`pandas.DataFrame`
           :param outputFile: absolute path of the file where ranking will be stored.
           :type outputFile: str
           :param index: whether to write the dataframe's index or not.
           :type index: bool, default False
           """
        if not ranking.empty:
            ranking.to_csv(outputFile, index = index, sep = "\t")
        else:
            #make sure to write at least the header if the dataframe is empty
            with open(outputFile, 'w') as outfile:
                header_line = "\"attributeName\"\t\"score\"\n"
                outfile.write(header_line)

class PythonSelector(FeatureSelector):
    """Abstract.
       Inherit from this class when implementing a feature selector using any of scikit-learn's functionality.
       As functionality invocation, input preprocessing and output postprocessing are typically very similar/the same for such implementations, this class already encapsulates it.
       Instead of implementing :meth:`PythonSelector.selectFeatures`, implement :meth:`PythonSelector.runSelector`.
       """
    def __init__(self, name):
        super().__init__(name)

    @abc.abstractmethod
    def runSelector(self, data, labels):
        """Abstract - implement this method when inheriting from this class.
           Runs the actual feature selector of scikit-learn.
           Is invoked by :meth:`PythonSelector.selectFeatures`.

           :param data: dataframe containing the unlabeled dataset.
           :type data: :class:`pandas.DataFrame`
           :param labels: numerically encoded class labels.
           :type labels: list of int
           :return: sklearn/mlxtend selector that ran the selection (containing coefficients etc.).
           """
        pass

    def selectFeatures(self):
        """Executes the feature selection procedure.
           Prepares the input data set to match scikit-learn's expected formats and postprocesses the output to create a ranking.

           :return: absolute path to the output ranking file.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        filename = self.getName() + ".csv"
        outputFile = self.output + filename

        data, labels = self.prepareInput()

        selector = self.runSelector(data, labels)

        self.prepareOutput(outputFile, data, selector)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished ########################")
        return outputFile

    def prepareInput(self):
        """Prepares the input data set before running any of scikit-learn's selectors.
           Removes the labels from the input data set and encodes the labels in numbers.

           :return: dataset (without labels) and labels encoded in numbers.
           :rtype: :class:`pandas.DataFrame` and list of int
           """
        start = time.time()
        labels = self.getLabels()
        data = self.getUnlabeledData()
        le = preprocessing.LabelEncoder()
        numeric_labels = le.fit_transform(labels)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Input Preparation")

        return data, numeric_labels

    def prepareOutput(self, outputFile, data, selector):
        """Transforms the selector output to a valid ranking and stores it into the specified file.

           :param outputFile: absolute path of the file to which to write the ranking.
           :type outputFile: str
           :param data: input dataset.
           :type data: :class:`pandas.DataFrame`
           :param selector: selector object from scikit-learn.
           """
        start = time.time()
        ranking = pd.DataFrame()
        ranking["attributeName"] = data.columns
        ranking["score"] = selector.scores_
        ranking = ranking.sort_values(by='score', ascending=False)
        self.writeRankingToFile(ranking, outputFile)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Output Preparation")

class RSelector(FeatureSelector,metaclass=abc.ABCMeta):
    """Selector class for invoking R code for feature selection.
       Inherit from this class if you want to use R code, implement :meth:`RSelector.createParams` with what your script requires, and set self.scriptName accordingly.

       :param rConfig: config parameters to execute R code.
       :type rConfig: dict
       """
    def __init__(self, name):
        self.rConfig = utils.getConfig("R")
        self.scriptName = "FS_" + name + ".R"
        super().__init__(name)

    @abc.abstractmethod
    def createParams(self, filename):
        """Abstract.
           Implement this method to set the parameters your R script requires.

           :param filename: absolute path of the output file.
           :type filename: str
           :return: list of parameters to use for R code execution, e.g. input and output filenames.
           :rtype: list of str
           """
        pass

    def selectFeatures(self):
        """Triggers the feature selection.
           Actually a wrapper method that invokes external R code.

           :return: absolute path to the result file containing the ranking.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        filename = self.getName() + ".csv"
        outputFile = self.output + filename
        params = self.createParams(outputFile)
        utils.runRCommand(self.rConfig, self.scriptName , params)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished ########################")

        return filename

class JavaSelector(FeatureSelector):
    """Selector class for invoking R code for feature selection.
       Inherit from this class if you want to use R code, implement :meth:`RSelector.createParams` with what your script requires, and set self.scriptName accordingly.

       :param javaConfig: config parameters to execute java code.
       :type javaConfig: dict
       """
    def __init__(self, name):
        self.javaConfig = utils.getConfig("Java")
        super().__init__(name)

    @abc.abstractmethod
    def createParams(self):
        """Abstract.
           Implement this method to set the parameters your java code requires.

           :return: list of parameters to use for java code execution, e.g. input and output filenames.
           :rtype: list of str
           """
        pass

    def selectFeatures(self):
        """Triggers the feature selection.
           Actually a wrapper method that invokes external java code.

           :return: absolute path to the result file containing the ranking.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        filename = self.name + ".csv"
        params = self.createParams()
        utils.runJavaCommand(self.javaConfig, "/WEKA_FeatureSelector.jar", params)
        output_filepath = self.output + filename
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished ########################")
        return output_filepath

############################### PRIOR KNOWLEDGE SELECTORS ###############################
class PriorKnowledgeSelector(FeatureSelector,metaclass=abc.ABCMeta):
    """Super class for all prior knowledge approaches.
       If you want to implement an own prior knowledge approach that uses a knowledge base (but not a second selector and no network approaches), inherit from this class.

       :param knowledgebase: instance of a knowledge base.
       :type knowledgebase: :class:`knowledgebases.KnowledgeBase` or inheriting class
       :param alternativeSearchTerms: list of alternative search terms to use for querying the knowledge base.
       :type alternativeSearchTerms: list of str
       """
    def __init__(self, name, knowledgebase):
        self.knowledgebase = knowledgebase
        super().__init__(name)
        self.alternativeSearchTerms = self.collectAlternativeSearchTerms()


    @abc.abstractmethod
    def selectFeatures(self):
        """Abstract.
           Implement this method when inheriting from this class.

           :return: absolute path to the output ranking file.
           :rtype: str
           """
        pass

    def collectAlternativeSearchTerms(self):
        """Gets all alternative search terms that were specified in the config file and put them into a list.

           :return: list of alternative search terms to use for querying the knowledge base.
           :rtype: list of str
           """
        alternativeTerms = self.dataConfig["alternativeSearchTerms"].split(" ")
        searchTerms = []
        for term in alternativeTerms:
            searchTerms.append(term.replace("_", " "))
        return searchTerms

    def getSearchTerms(self):
        """Gets all search terms to use for querying a knowledge base.
           Search terms that will be used are a) the class labels in the dataset, and b) the alternative search terms that were specified in the config file.

           :return: list of search terms to use for querying the knowledge base.
           :rtype: list of str
           """
        searchTerms = list(self.getUniqueLabels())
        searchTerms.extend(self.alternativeSearchTerms)

        return searchTerms

    def getName(self):
        """Returns the full name (including applied knowledge base) of this selector.

           :return: selector name.
           :rtype: str
           """
        return self.name + "_" + self.knowledgebase.getName()

#selector class for modifying integrative approaches
class CombiningSelector(PriorKnowledgeSelector):
    """Super class for prior knoweldge approaches that use a knowledge base AND combine it with any kind of selector, e.g. a traditional approach.
       Inherit from this class if you want to implement a feature selector that requires both a knowledge base and another selector, e.g. because it combines information from both.

       :param knowledgebase: instance of a knowledge base.
       :type knowledgebase: :class:`knowledgebases.KnowledgeBase` or inheriting class
       :param tradApproach: any feature selector implementation to use internally, e.g. a traditional approach like ANOVA
       :type tradApproach: :class:`FeatureSelector`
       """
    def __init__(self, name, knowledgebase, tradApproach):
        self.tradSelector = tradApproach
        self.tradSelector.disableLogFlush()
        super().__init__(name, knowledgebase)
        self.tradSelector.setTimeLogs(self.timeLogs)

    @abc.abstractmethod
    def selectFeatures(self):
        """Abstract.
           Implement this method as desired when inheriting from this class.

           :return: absolute path to the output ranking file.
           :rtype: str
           """
        pass

    def getName(self):
        """Returns the full name (including applied knowledge base and feature selector) of this selector.

           :returns: selector name.
           :rtype: str
           """
        return self.name + "_" + self.tradSelector.getName() + "_" +  self.knowledgebase.getName()

    def getExternalGenes(self):
        """Gets all genes related to the provided search terms from the knowledge base.

           :returns: list of gene names.
           :rtype: list of str
           """
        start = time.time()
        externalGenes = self.knowledgebase.getRelevantGenes(self.getSearchTerms())
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Getting External Genes")

        return externalGenes

class NetworkSelector(PriorKnowledgeSelector):
    """Abstract.
       Inherit from this method if you want to implement a new network approach that actually conducts feature EXTRACTION, i.e. maps the original data set to have pathway/subnetworks.
       Instead of  :meth:`FeatureSelector.selectFeatures` implement :meth:`NetworkSelector.selectPathways` when inheriting from this class.

       Instances of :class:`NetworkSelector` and inheriting classes also require a :class:`PathwayMapper` object that transfers the dataset to the new feature space.
       Custom implementations thus need to implement a) a selection strategy to select pathways and b) a mapping strategy to compute new feature values for the selected pathways.

       :param featureMapper: feature mapping object that transfers the feature space.
       :type featureMapper: :class:`FeatureMapper` or inheriting class
       """
    def __init__(self, name, knowledgebase, featuremapper):
        self.featureMapper = featuremapper
        super().__init__(name, knowledgebase)

    @abc.abstractmethod
    def selectPathways(self, pathways):
        """Selects the pathways that will become the new features of the data set.
           Implement this method (instead of :meth:`FeatureSelector.selectFeatures` when inheriting from this class.

           :param pathways: dict of pathways (pathway names as keys) to select from.
           :type pathways: dict
           :returns: pathway ranking as dataframe
           :rtype: :class:`pandas.DataFrame`
           """
        pass

    def writeMappedFile(self, mapped_data, fileprefix):
        """Writes the mapped dataset with new feature values to the same directory as the original file is located (it will be automatically processed then).

           :param mapped_data: dataframe containing the dataset with mapped feature space.
           :type mapped_data: :class:`pandas.DataFrame`
           :param fileprefix: prefix of the file name, e.g. the directory path
           :type fileprefix: str
           :return: absolute path of the file name to store the mapped data set.
           :rtype: str
           """
        mapped_filepath = fileprefix + "_" + self.getName() + ".csv"
        mapped_data.to_csv(mapped_filepath)

        return mapped_filepath


    def getName(self):
        """Gets the selector name (including the knowledge base).

           :returns: selector name.
           :rtype: str
           """
        return self.name + "_" +  self.knowledgebase.getName()

    def filterPathways(self, pathways):
        filtered_pathways = {}
        for pathwayName in pathways:
            genes = pathways[pathwayName].nodes_by_label.keys()
            #check if there is an overlap between the pathway and data set genes
            existingGenes = list(set(self.getFeatures()) & set(genes))
            if len(existingGenes) > 0:
                filtered_pathways[pathwayName] = pathways[pathwayName]
            else:
                utils.logWarning("WARNING: No genes of pathway " + pathwayName + " found in dataset. Pathway will not be considered")

        return filtered_pathways

    def selectFeatures(self):
        """Instead of selecting existing features, instances of :class:`NetworkSelector` select pathways or submodules as features.
           For that, it first queries its knowledge base for pathways.
           It then selects the top k pathways (strategy to be implemented in :meth:`NetworkSelector.selectPathways`) and subsequently maps the dataset to its new feature space.
           The mapping will be conducted by an object of :class:`PathwayMapper` or inheriting classes.
           If a second dataset for cross-validation is available, the feature space of this dataset will also be transformed.

           :returns: absolute path to the pathway ranking.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        overallstart = time.time()
        pathways = self.knowledgebase.getRelevantPathways(self.getSearchTerms())
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, overallstart, end, "Get Pathways")

        #filter pathways to only those that contain at least one gene from the data set
        pathways = self.filterPathways(pathways)
        start = time.time()
        pathwayRanking = self.selectPathways(pathways)
        outputFile = self.output + self.getName() + ".csv"
        self.writeRankingToFile(pathwayRanking, outputFile)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Pathway Selection")

        pathwayNames = pathwayRanking["attributeName"]

        start = time.time()
        mapped_data = self.featureMapper.mapFeatures(self.getData(), pathways)
        fileprefix = os.path.splitext(self.input)[0]
        mapped_filepath = self.writeMappedFile(mapped_data, fileprefix)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Mapping")

        #if crossvalidation is enabled, we also have to map the crossvalidation file
        if (utils.getConfigBoolean("Evaluation", "enableCrossEvaluation")):
            start = time.time()

            #we need to get the cross validation file that had been moved into the intermediate folder
            crossValidationPath = utils.getConfigValue("General", "crossVal_preprocessing") + "ready/"
            crossValidationFile = utils.getConfigValue("Evaluation", "crossEvaluationData")
            crossValFilename = os.path.basename(crossValidationFile)
            crossValFilepath = crossValidationPath + crossValFilename
            crossValData = pd.read_csv(crossValFilepath, index_col=0)
            mapped_crossValData = self.featureMapper.mapFeatures(crossValData, pathways)
            crossvalFileprefix = os.path.splitext(crossValFilepath)[0]
            crossval_mapped_filepath = self.writeMappedFile(mapped_crossValData, crossvalFileprefix)

            end = time.time()
            self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "CrossValidation Feature Mapping")

        overallend = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, overallstart, overallend, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished ########################")
        return outputFile

############################### FILTER ###############################

class RandomSelector(FeatureSelector):
    """Baseline Selector: Randomly selects any features.
       """
    def __init__(self):
        super().__init__("Random")

    def selectFeatures(self):
        """Randomly select any features from the feature space.
           Assigns a score of 0.0 to every feature

           :returns: absolute path to the ranking file.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        filename = self.getName() + ".csv"
        outFilename = self.output + filename
        #randomly pick any features
        with open(self.input, 'r') as infile:
            header = infile.readline().rstrip().split(",")

        max_index = len(header)
        min_index = 2

        shuffled_indices = random.sample(range(min_index, max_index), max_index - 2)

        with open(outFilename, 'w') as outfile:
            header_line = "\"attributeName\"\t\"score\"\n"
            outfile.write(header_line)
            for i in shuffled_indices:
                line = "\"" + header[i] + "\"\t\"0.0000\"\n"
                outfile.write(line)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished ########################")

        return outFilename

class AnovaSelector(PythonSelector):
    """Runs ANOVA feature selection using scikit-learn implementation
       """

    def __init__(self):
        super().__init__("ANOVA")

    def runSelector(self, data, labels):
        """Runs the ANOVA feature selector of scikit-learn.
           Is invoked by :meth:`PythonSelector.selectFeatures`.

           :param data: dataframe containing the unlabeled dataset.
           :type data: :class:`pandas.DataFrame`
           :param labels: numerically encoded class labels.
           :type labels: list of int
           :return: sklearn/mlxtend selector that ran the selection (containing coefficients etc.).
           """
        start = time.time()
        #setting k to "all" returns all features
        selector = SelectKBest(f_classif, k="all")
        selector.fit_transform(data, labels)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "ANOVA")
        return selector

class Variance2Selector(PythonSelector):
    """Runs variance-based feature selection using scikit-learn.
       """
    def __init__(self):
        super().__init__("Variance")

    def prepareOutput(self, outputFile, data, selector):
        """Transforms the selector output to a valid ranking and stores it into the specified file.
           We need to override this method because variance selector has no attribute scores but variances.

           :param outputFile: absolute path of the file to which to write the ranking.
           :type outputFile: str
           :param data: input dataset.
           :type data: :class:`pandas.DataFrame`
           :param selector: selector object from scikit-learn.
           """
        start = time.time()
        ranking = pd.DataFrame()
        ranking["attributeName"] = data.columns
        ranking["score"] = selector.variances_
        ranking = ranking.sort_values(by='score', ascending=False)
        self.writeRankingToFile(ranking, outputFile)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Output Preparation")

    def runSelector(self, data, labels):
        """Runs the actual variance-based feature selector of scikit-learn.
           Is invoked by :meth:`PythonSelector.selectFeatures`.

           :param data: dataframe containing the unlabeled dataset.
           :type data: :class:`pandas.DataFrame`
           :param labels: numerically encoded class labels.
           :type labels: list of int
           :return: sklearn/mlxtend selector that ran the selection (containing coefficients etc.).
           """
        start = time.time()
        selector = VarianceThreshold()
        selector.fit_transform(data)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Variance_p")

        return selector


class MRMRSelector(RSelector):
    """Runs maximum Relevance minimum Redundancy (mRMR) feature selection using the mRMRe R implementation: https://cran.r-project.org/web/packages/mRMRe/index.html
       Actually a wrapper class for invoking the R code.

       :param scriptName: name of the R script to invoke.
       :type scriptName: str
       :param maxFeatures: maximum number of features to select. Currently all features (=0) are ranked..
       :type maxFeatures: int
       """
    def __init__(self):
        self.maxFeatures = 0
        super().__init__("mRMR")

    def createParams(self, outputFile):
        """Sets the parameters the R script requires (input file, output file, maximum number of features).

           :return: list of parameters to use for mRMR execution in R.
           :rtype: list of str
           """
        params = [self.input, outputFile, str(self.maxFeatures)]
        return params

class VarianceSelector(RSelector):
    """Runs variance-based feature selection using R genefilter library.
       Actually a wrapper class for invoking the R code.

       :param scriptName: name of the R script to invoke.
       :type scriptName: str
       """
    def __init__(self):
        super().__init__("VB-FS")

    def createParams(self, outputFile):
        """Sets the parameters the R script requires (input file, output file).

           :param outputFile: absolute path to the output file that will contain the ranking.
           :type outputFile: str
           :return: list of parameters to use for mRMR execution in R.
           :rtype: list of str
           """
        params = [self.input, outputFile]
        return params


class InfoGainSelector(JavaSelector):
    """Runs InfoGain feature selection as provided by WEKA: https://www.cs.waikato.ac.nz/ml/weka/
       Actually a wrapper class for invoking java code.
       """

    def __init__(self):
        super().__init__("InfoGain")

    def createParams(self):
        """Sets the parameters the java program requires (input file, output file, selector name).

           :return: list of parameters to use for InfoGain execution in java.
           :rtype: list of str
           """
        params = [self.input, self.output, "InfoGain"]
        return params

class ReliefFSelector(JavaSelector):
    """Runs ReliefF feature selection as provided by WEKA: https://www.cs.waikato.ac.nz/ml/weka/
       Actually a wrapper class for invoking java code.
       """

    def __init__(self):
        super().__init__("ReliefF")

    def createParams(self):
        """Sets the parameters the java program requires (input file, output file, selector name).

           :return: list of parameters to use for InfoGain execution in java.
           :rtype: list of str
           """
        params = [self.input, self.output, "ReliefF"]
        return params

############################### FILTER - COMBINED ###############################
class KbSelector(PriorKnowledgeSelector):
    """Knowledge base selector.
       Selects features exclusively based the information retrieved from a knowledge base.

       :param knowledgebase: instance of a knowledge base.
       :type knowledgebase: :class:`knowledgebases.KnowledgeBase`
       """
    def __init__(self, knowledgebase):
        super().__init__("KBonly", knowledgebase)

    def updateScores(self, entry, newGeneScores):
        """Updates a score entry with the new score retrieved from the knowledge base.
           Used by apply function.

           :param entry: a gene score entry consisting of the gene name and its score
           :type entry: :class:`pandas.Series`
           :param newGeneScores: dataframe containing gene scores retrieved from the knowledge base.
           :type newGeneScores: :class:`pandas.DataFrame`
           :returns: updated series element.
           :rtype: :class:`pandas.Series`
           """
        gene = entry["attributeName"]
        updatedGenes = newGeneScores.iloc[:,0]
        #if the gene has a new score, update the entry
        if gene in updatedGenes.values:
            x = newGeneScores.loc[(newGeneScores["gene_symbol"] == gene), "score"]
            #necessary because we want to get the scalar value, not a series
            entry["score"] = x.iloc[0]
        return entry

    def selectFeatures(self):
        """Does the actual feature selection.
           Retrieves association scores for genes from the knowledge base based on the given search terms.

           :returns: absolute path to the resulting ranking file.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        outputFile = self.output + self.getName() + ".csv"

        genes = self.getFeatures()

        # assign a minimal default score (0.000001) to all genes
        attributeNames = genes
        scores = [0.00001] * len(genes)
        ranking = pd.DataFrame({"attributeName": attributeNames, "score": scores})

        kb_start = time.time()
        associatedGenes = self.knowledgebase.getGeneScores(self.getSearchTerms())
        kb_end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, kb_start, kb_end, "Getting External Gene Scores")

        # assign association score to all genes in data
        updated_ranking = ranking.apply(self.updateScores, axis = 1, newGeneScores = associatedGenes)

        #sort by score, with highest on top
        updated_ranking = updated_ranking.sort_values("score", ascending=False)
        #save final rankings to file
        self.writeRankingToFile(updated_ranking, outputFile)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished. ########################")
        return outputFile

class KBweightedSelector(CombiningSelector):
    """Selects features based on association scores retrieved from the knowledge base and the relevance score retrieved by the (traditional) approach.
       Computes the final score via tradScore * assocScore.

       :param knowledgebase: instance of a knowledge base.
       :type knowledgebase: :class:`knowledgebases.KnowledgeBase` or inheriting class
       :param tradApproach: any feature selector implementation to use internally, e.g. a traditional approach like ANOVA
       :type tradApproach: :class:`FeatureSelector`
       """
    def __init__(self, knowledgebase, tradApproach):
        super().__init__("Weighted", knowledgebase, tradApproach)

    def updateScores(self, entry, newGeneScores):
        """Updates a score entry with the new score retrieved from the knowledge base.
           Used by apply function.

           :param entry: a gene score entry consisting of the gene name and its score
           :type entry: :class:`pandas.Series`
           :param newGeneScores: dataframe containing gene scores retrieved from the knowledge base.
           :type newGeneScores: :class:`pandas.DataFrame`
           :returns: updated series element.
           :rtype: :class:`pandas.Series`
           """
        gene = entry["attributeName"]
        updatedGenes = newGeneScores.iloc[:,0]
        #if the gene has a new score, update the entry
        if gene in updatedGenes.values:
            x = newGeneScores.loc[(newGeneScores["gene_symbol"] == gene), "score"]
            #necessary because we want to get the scalar value, not a series
            entry["score"] = x.iloc[0]
        return entry

    def getName(self):
        """Gets the selector name (including the knowledge base and (traditional) selector).

           :returns: selector name.
           :rtype: str
           """
        return self.name + "_" + self.tradSelector.getName() + "_" +  self.knowledgebase.getName()

    def computeStatisticalRankings(self, intermediateDir):
        """Computes the statistical relevance score of all features using the (traditional) selector.

           :param intermediateDir: absolute path to output directory for (traditional) selector (where to write the statistical rankings).
           :type intermediateDir: str
           :returns: dataframe with statistical ranking.
           :rtype: :class:`pandas.DataFrame`
           """
        start = time.time()
        self.tradSelector.setParams(self.input, intermediateDir, self.loggingDir)
        statsRankings = self.tradSelector.selectFeatures()
        #load data frame from file
        statisticalRankings = pd.read_csv(statsRankings, index_col = 0, sep = "\t", engine = "python")
        self.timeLogs = pd.concat([self.timeLogs, self.tradSelector.getTimeLogs()])
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Statistical Ranking")

        return statisticalRankings

    def computeExternalRankings(self):
        """Computes the association scores for every gene using the knowledge base.
           Genes for which no entry could be found receive a default score of 0.000001.

           :return: dataframe with statistical ranking.
           :rtype: :class:`pandas.DataFrame`
           """
        start = time.time()
        genes = self.getFeatures()

        # assign a minimal default score (0.000001) to all genes
        geneScores = dict.fromkeys(genes, 0.000001)
        associatedGenes = self.knowledgebase.getGeneScores(self.getSearchTerms())
        #assign association score to all genes in data

        # assign association score to all genes in data
        for gene in geneScores.keys():
            # check if score for gene was found in knowledge base
            if gene in list(associatedGenes.iloc[:, 0]):
                gene_entry = associatedGenes[associatedGenes["gene_symbol"] == gene]
                geneScores[gene] = gene_entry.iloc[0, 1]

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "External Ranking")
        return geneScores

    def combineRankings(self, externalRankings, statisticalRankings):
        """Combines score rankings from both the knowledge base and the (traditional) selector (kb_score * trad_score) to retrieve a final score for every gene.

           :param externalRankings: dataframe with ranking from knowledge base.
           :type externalRankings: :class:`pandas.DataFrame`
           :param statisticalRankings: dataframe with statistical ranking.
           :type statisticalRankings: :class:`pandas.DataFrame`
           :returns: dataframe with final combined ranking.
           :rtype: :class:`pandas.DataFrame`
           """
        start = time.time()
        #just take over the statistical rankings and alter the scores accordingly
        combinedRankings = statisticalRankings.copy()

        features = statisticalRankings.index
        #go trough every item and combine by weighting
        for feature in features:
            #update scores - external rankings only provide feature scores, no indices
            if feature in externalRankings.keys():
                externalScore = externalRankings[feature]
            else:
                #if no entry exists, set the score to be minimal to not zero up the whole equation in the end
                externalScore = 0.00001
            if externalScore == 0:
                # if no entry exists, set the score to be minimal to not zero up the whole equation in the end
                externalScore = 0.00001
            statsScore = statisticalRankings.at[feature, "score"]
            combinedRankings.at[feature, "score"] = externalScore * statsScore

        #reorder genes based on new score
        combinedRankings = combinedRankings.sort_values('score', ascending=False)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Ranking Combination")
        return combinedRankings

    def selectFeatures(self):
        """Runs the feature selection process.
           Retrieves scores from knowledge base and (traditional) selector and combines these to a single score.

           :returns: absolute path to final output file containing the ranking.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        intermediateDir = utils.getConfigValue("General",
                                                      "intermediateDir") + self.getName() + "/"

        utils.createDirectory(intermediateDir)

        outputFile = self.output + self.getName() + ".csv"

        #compute gene rankings with traditional approaches
        statisticalRankings = self.computeStatisticalRankings(intermediateDir)

        #compute gene rankings/associations with external knowledge base
        externalRankings = self.computeExternalRankings()

        #combine ranking scores
        combinedRankings = self.combineRankings(externalRankings, statisticalRankings)

        #save final rankings to file
        #note: here the gene ids are the index, so write it to file
        self.writeRankingToFile(combinedRankings, outputFile, True)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished. ########################")
        return outputFile

class LassoPenalty(PriorKnowledgeSelector, RSelector):
    """Runs feature selection by invoking xtune R package: https://cran.r-project.org/web/packages/xtune/index.html

       xtune is a Lasso selector that uses feature-individual penalty scores.
       These penalty scores are retrieved from the knowledge base.
       """
    selectFeatures = RSelector.selectFeatures #make sure the right selectFeatures method will be invoked

    getName = PriorKnowledgeSelector.getName

    def __init__(self, knowledgebase):

        super().__init__("LassoPenalty", knowledgebase)
        self.scriptName = "FS_LassoPenalty.R"

    def createParams(self, outputFile):
        """Sets the parameters the xtune R script requires (input file, output file, filename containing rankings from knowledge base).

           :return: list of parameters to use for xtune execution in R.
           :rtype: list of str
           """
        externalScore_filename = self.computeExternalRankings()
        params = [self.input, outputFile, externalScore_filename]
        return params

    def computeExternalRankings(self):
        """Computes the association scores for each feature based on the scores retrieved from the knowledge base.
           Features that could not be found in the knowledge base receive a default score of 0.000001.

           :return: absolute path to the file containing the external rankings.
           :rtype: str
           """
        start = time.time()
        intermediateOutput = utils.getConfigValue("General",
                                                      "intermediateDir") + self.getName() + "/"

        utils.createDirectory(intermediateOutput)
        genes = self.getFeatures()
        # assign a minimal default score (0.000001) to all genes
        geneScores = dict.fromkeys(genes, 0.000001)
        associatedGenes = self.knowledgebase.getGeneScores(self.getSearchTerms())

        #assign association score to all genes in data
        for gene in geneScores.keys():
            #check if score for gene was found in knowledge base
            if gene in list(associatedGenes.iloc[:,0]):
                gene_entry = associatedGenes[associatedGenes["gene_symbol"] == gene]
                geneScores[gene] = gene_entry.iloc[0,1]

        #write gene scores to file

        scores_filename = intermediateOutput + self.knowledgebase.getName() + "_scores.csv"
        scores_df = pd.DataFrame.from_dict(geneScores, orient = "index", columns = ["score"])
        scores_df = scores_df.sort_values('score', ascending=False)
        scores_df.to_csv(scores_filename, index=True)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "External Ranking")
        return scores_filename


############################### WRAPPER ###############################
class WrapperSelector(PythonSelector):
    """Selector implementation for wrapper selectors using scikit-learn.
       Currently implements recursive feature eliminatin (RFE) and sequential forward selection (SFS) strategies,
       which can be combined with nearly any classifier offered by scikit-learn, e.g. SVM.

       :param selector: scikit-learn selector strategy (currently RFE and SFS)
       :param classifier: scikit-learn classifier to use for wrapper selection.
       """
    def __init__(self, name):
        super().__init__(name)
        self.classifier = self.createClassifier()
        self.selector = self.createSelector()


    def createClassifier(self):
        """Creates a classifier instance (from scikit-learn) to be used during the selection process.
           To enable the framework to use a new classifier, extend this method accordingly.

           :returns: scikit-learn classifier instance.
           """
        classifier = None
        classifierType = self.name.split("-")[0]

        if "KNN" in classifierType:
            #attention: assumes that KNN is followed by a number!
            k = int(classifierType.replace("KNN", ""))
            classifier = KNeighborsClassifier(n_neighbors=k)
        elif classifierType == "SVMl":#SVM with linear kernel
            classifier = LinearSVC(max_iter=10000)
        #elif classifierType == "SVMp":  # SVM with polynomial kernel, but it does not have coef component
        #    classifier = SVC(kernel="poly")
        elif classifierType == "LR":
            classifier = LinearRegression()
        elif classifierType == "NB":
            #use MultinomialNB because we cannot assume feature likelihood to be gaussian by default
            classifier = MultinomialNB()
        elif classifierType == "ANOVA":
            classifier = f_classif
        else:
            raise BaseException("No suitable classifier found for " + classifierType + ". Choose between KNNx, SVMl (SVM with linear kernel), SVMp (SVM with polynomial kernel), LR, NB, ANOVA.")

        return classifier

    def createSelector(self):
        """Creates a selector instance that leads the selection process.
           Currently, sequential forward selection (SFS) and recursive feature elimination (RFE) are implemented.
           Extend this method if you want to add another selection strategy.

           :returns: scikit-learn selector instance.
           """
        selector = None
        k = utils.getConfigValue("Gene Selection - General", "selectKgenes")
        selectorType = self.name.split("-")[1]
        if selectorType == "RFE":
            selector = RFE(self.classifier, int(k))
        elif selectorType == "SFS":
            selector = SFS(self.classifier,
                      k_features=int(k),
                      forward=True,
                      floating=False,
                      scoring='accuracy',
                      verbose = 2,
                      n_jobs = int(utils.getConfigValue("General", "numCores"))/2, #use half of the available cores
                      cv=0)

        return selector

    def prepareOutput(self, outputFile, data, selector):
        """Overwrites the inherited prepareOutput method because we need to access the particular selector's coefficients.
           The coefficients are extracted as feature scores and will be written to the rankings file.

           :param outputFile: selector name
           :type outputFile: str
           :param data: input dataset to get the feature names.
           :type data: :class:`pandas.DataFrame`
           :param selector: selector instance that is used during feature selection.
           """
        start = time.time()
        ranking = pd.DataFrame()
        try:
            x = selector.estimator_.coef_
        except:
            try:
                x = selector.estimator.coef_
            except:
                x = selector.est_.coef_
        selected_columnIDs = selector.ranking[selector.ranking_ == 1]
        selected_features = data.columns[selected_columnIDs]
        ranking["attributeName"] = selected_features
        ranking["score"] = x[0]
        ranking = ranking.sort_values('score', ascending=False)
        self.writeRankingToFile(ranking, outputFile)
        end = time.time()
        self.timeLogs = utils.logRuntime(start, end, "Prepare Output")


    def runSelector(self, data, labels):
        """Runs the actual feature selector of scikit-learn.
           Is invoked by :meth:`PythonSelector.selectFeatures`.

           :param data: dataframe containing the unlabeled dataset.
           :type data: :class:`pandas.DataFrame`
           :param labels: numerically encoded class labels.
           :type labels: list of int
           :return: sklearn/mlxtend selector that ran the selection (containing coefficients etc.).
           """

        # do gene selection
        start = time.time()
        #adjust k to not exceed data columns
        k = int(utils.getConfigValue("Gene Selection - General", "selectKgenes"))
        if k > data.columns.size:
            self.selector.n_features_to_select_ = data.columns.size
            self.selector.k_features = data.columns.size

        # do data scaling
        scaling = StandardScaler().fit(data)
        scaled_data = scaling.transform(data)
        data = scaled_data
        self.selector = self.selector.fit(data, labels)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Wrapper Selector")

        return self.selector

class SVMRFESelector(JavaSelector):
    """Executes SVM-RFE with poly-kernel.
       Uses an efficient java implementation from WEKA and is thus just a wrapper class to invoke the corresponding jars.
       """
    def __init__(self):
        super().__init__("SVMpRFE")

    def createParams(self):
        """Sets the parameters the java program requires (input file, output file, selector name).

           :return: list of parameters to use for InfoGain execution in java.
           :rtype: list of str
           """
        params = [self.input, self.output, "SVMpRFE"]
        return params

############################### EMBEDDED ###############################
class RandomForestSelector(PythonSelector):
    """Selector class that implements RandomForest as provided by scikit-learn.
       """
    def __init__(self):
        super().__init__("RandomForest")

    #override method because there is no scores_ attribute but instead feature_importances_
    def prepareOutput(self, outputFile, data, selector):
        """Overwrites the inherited prepareOutput method because we need to access the RandomForest selector's feature importances.
           These feature importances are extracted as feature scores and will be written to the rankings file.

           :param outputFile: selector name
           :type outputFile: str
           :param data: input dataset to get the feature names.
           :type data: :class:`pandas.DataFrame`
           :param selector: RandomForest selector instance that is used during feature selection.
           """
        start = time.time()
        ranking = pd.DataFrame()
        ranking["attributeName"] = data.columns
        ranking["score"] = selector.feature_importances_
        ranking = ranking.sort_values('score', ascending=False)
        self.writeRankingToFile(ranking, outputFile)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Prepare Output")

    def runSelector(self, data, labels):
        """Runs the actual feature selection using scikit-learn's RandomForest classifier.
           Is invoked by :meth:`PythonSelector.selectFeatures`.

           :param data: dataframe containing the unlabeled dataset.
           :type data: :class:`pandas.DataFrame`
           :param labels: numerically encoded class labels.
           :type labels: list of int
           :return: scikit-learn RandomForestClassifier that ran the selection.
           """
        # setting k to "all" returns all features

        start = time.time()
        clf = RandomForestClassifier(random_state = 0)
        # Train the classifier
        clf.fit(data, labels)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Random Forest")

        return clf

class LassoSelector(PythonSelector):
    """Selector class that implements Lasso feature selection using scikit-learn.
       """
    def __init__(self):
        super().__init__("Lasso")

        # override method because there is no scores_ attribute but instead feature_importances_
    def prepareOutput(self, outputFile, data, selector):
        """Overwrites the inherited prepareOutput method because we need to access Lasso's coefficients.
           These coefficients are extracted as feature scores and will be written to the rankings file.

           :param outputFile: selector name
           :type outputFile: str
           :param data: input dataset to get the feature names.
           :type data: :class:`pandas.DataFrame`
           :param selector: RandomForest selector instance that is used during feature selection.
           """
        start = time.time()
        ranking = pd.DataFrame()
        ranking["attributeName"] = data.columns
        ranking["score"] = selector.coef_
        ranking = ranking.sort_values('score', ascending=False)
        self.writeRankingToFile(ranking, outputFile)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Prepare Output")

    def runSelector(self, data, labels):
        """Runs the actual Lasso feature selector using scikit-learn.
           Is invoked by :meth:`PythonSelector.selectFeatures`.

           :param data: dataframe containing the unlabeled dataset.
           :type data: :class:`pandas.DataFrame`
           :param labels: numerically encoded class labels.
           :type labels: list of int
           :return: Lasso selector that ran the selection.
           """
        # setting k to "all" returns all features

        start = time.time()

        clf = Lasso()
        clf.fit(data, labels)

        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Lasso")

        return clf


############################### INTEGRATIVE ###############################
class PreFilterSelector(CombiningSelector):
    """Applies a two-level prefiltering strategy for feature selection.
       Filters all features that were not retrieved by a knowledge base based on the search terms provided in the config file.
       Applies a (traditional) feature selector on the remaining features afterwards.

       For traditional univariate filter approaches, the results retrieved by this class and :class:`PostFilterSelector` will be the same.
       """
    def __init__(self, knowledgebase, tradApproach):
        super().__init__("Prefilter", knowledgebase, tradApproach)

    def selectFeatures(self):
        """Carries out feature selection.
           First queries the assigned knowledge base to get genes that are associated to the given search terms.
           Filter feature set of input data set to contain only features that are in the retrieved gene set.
           Apply (traditional) selector on the filtered data set.

           :returns: absolute path to rankings file.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")

        intermediateOutput = utils.getConfigValue("General",
                                                      "intermediateDir") + self.getName() + "/"
        utils.createDirectory(intermediateOutput)
        start = time.time()
        externalGenes = self.knowledgebase.getRelevantGenes(self.getSearchTerms())
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Getting Relevant Genes")

        outputFilename = self.output + self.getName() + ".csv"

        #stop if no genes could be found for filtering
        if len(externalGenes) == 0:
            return outputFilename

        #filter input by externalGenes, keep classLabel and sampleID
        matrix = pd.read_csv(self.input)
        finalCols = matrix.columns.to_list()[0:2]
        # filter externalGenes by genes available in the rankings
        dataGenes = set(matrix.columns.to_list())
        sharedGenes = list(dataGenes & set(externalGenes))
        finalCols.extend(sharedGenes)
        filteredMatrix =  matrix[finalCols]
        #write to file and set this as new input
        filtered_input = intermediateOutput + self.getName() + ".csv"
        filteredMatrix.to_csv(filtered_input, index = False)
        self.tradSelector.setParams(filtered_input, intermediateOutput, self.loggingDir)
        rankingFile = self.tradSelector.selectFeatures()
        self.timeLogs = pd.concat([self.timeLogs, self.tradSelector.getTimeLogs()])

        #rename ranking file so that we can recognize it in the output files
        os.rename(rankingFile, outputFilename)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")

        utils.logInfo("######################## " + self.getName() + " finished. ########################")
        return outputFilename

class PostFilterSelector(CombiningSelector):
    """Applies a two-level postfiltering strategy for feature selection.
       Applies (traditional) feature selection to the input data set.
       Afterwards, removes all genes for which no information in the corresponding knowledge base was found based on the search terms provided in the config file.
       For traditional univariate filter approaches, the results retrieved by this class and :class:`PreFilterSelector` will be the same.
       """
    def __init__(self, knowledgebase, tradApproach):
        super().__init__("Postfilter", knowledgebase, tradApproach)

    def selectFeatures(self):
        """Carries out feature selection.
           First executes (traditional) selector.
           Then queries the assigned knowledge base to get genes that are associated to the given search terms.
           Finally filters feature set to contain only features that are in the retrieved gene set.

           :returns: absolute path to rankings file.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        intermediateOutput = utils.getConfigValue("General",
                                                    "intermediateDir") + self.getName() + "/"
        utils.createDirectory(intermediateOutput)

        outputFile = self.output + self.getName() + ".csv"
        self.tradSelector.setParams(self.input, intermediateOutput, self.loggingDir)
        rankingFile = self.tradSelector.selectFeatures()
        self.timeLogs = pd.concat([self.timeLogs, self.tradSelector.getTimeLogs()])
        ranking = utils.loadRanking(rankingFile)

        kb_start = time.time()
        #filter ranking by genes from knowledge base
        externalGenes = self.knowledgebase.getRelevantGenes(self.getSearchTerms())
        kb_end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, kb_start, kb_end, "Getting Relevant Genes")

        #filter externalGenes by genes available in the rankings
        dataGenes = set(ranking["attributeName"])
        sharedGenes = list(dataGenes & set(externalGenes))
        filteredRanking = ranking[ranking["attributeName"].isin(sharedGenes)]
        self.writeRankingToFile(filteredRanking, outputFile)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() +".csv")

        utils.logInfo("######################## " + self.getName() + " finished. ########################")
        return outputFile

class ExtensionSelector(CombiningSelector):
    """Selector implementation inspired by SOFOCLES:
       "SoFoCles: Feature filtering for microarray classification based on Gene Ontology", Papachristoudis et al., Journal of Biomedical Informatics, 2010

       This selector carries out (traditional) feature selection and in parallel retrieves relevant genes from a knowledge base based on the provided search terms.
       The ranking is then adapted by alternating the feature ranking retrieved by the (traditiona) selection approach and the externally retrieved genes.
       This is kind of related to an extension approach, where a feature ranking that was retrieved by a traditional approach is extended by such external genes.
       """
    def __init__(self, knowledgebase, tradApproach):
        super().__init__("Extension", knowledgebase, tradApproach)

    def selectFeatures(self):
        """Carries out feature selection.
           Executes (traditional) selector and separately retrieves genes from the assigned knowledge base based on the search terms specified in the config.
           Finally merges the two feature lists alternating to form an "extended" feature ranking.

           :returns: absolute path to rankings file.
           :rtype: str
           """
        utils.logInfo("######################## " + self.getName() + "... ########################")
        start = time.time()
        intermediateOutput = utils.getConfigValue("General",
                                                      "intermediateDir") + self.getName() + "/"
        utils.createDirectory(intermediateOutput)

        outputFile = self.output + self.getName() + ".csv"
        self.tradSelector.setParams(self.input, intermediateOutput, self.loggingDir)
        rankingFile = self.tradSelector.selectFeatures()
        self.timeLogs = pd.concat([self.timeLogs, self.tradSelector.getTimeLogs()])

        trad_ranking = utils.loadRanking(rankingFile)
        # extend ranking by genes from knowledge base
        kb_start = time.time()
        ext_ranking = self.knowledgebase.getGeneScores(self.getSearchTerms())
        kb_end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, kb_start, kb_end, "Getting External Gene Scores")

        #select top k genes from ext_ranking
        #topK = int(utils.getConfigValue("Evaluation", "topKmax"))

        #rename columns
        ext_ranking.columns = ["attributeName", "score_ext"]
        #select only genes from dataset from external ranking
        ext_ranking_genes = trad_ranking[trad_ranking["attributeName"].isin(ext_ranking["attributeName"])]
        #join gene indices with external ranking to get index column
        x = ext_ranking_genes.reindex(columns =["attributeName"])
        merged_ranking = x.merge(ext_ranking, on= "attributeName")
        merged_ranking = merged_ranking.loc[:,["attributeName", "score_ext"]]
        #rename score column
        merged_ranking.columns = ["attributeName", "score"]
        # sort by scores
        merged_ranking.sort_values('score', ascending=False, inplace=True)
        ext_ranking = merged_ranking
        #ext_len = topK
        #if len(merged_ranking.index) < topK:
        #    ext_len = len(merged_ranking.index)

        #topK_ext = merged_ranking.head(ext_len)
        #reset index of topK_ext (needed for interleaving)

        ext_ranking.index = list(range(1,2 * len(ext_ranking.index) + 1 , 2))

        trad_ranking.index = list(range(0, 2 * len(trad_ranking.index), 2))
        #interleave both dataframes
        interleaved_ranking = pd.concat([trad_ranking, ext_ranking]).sort_index()

        #remove duplicate entries and keep first occurrences
        interleaved_ranking.drop_duplicates(subset=interleaved_ranking.columns[0], keep="first", inplace=True)

        #if len(interleaved_ranking) < topK:
        #    topK = len(interleaved_ranking)
        #cut ranking to topK
        #final_ranking = interleaved_ranking.head(topK)

        #adjust relevance scores of external genes so that sorting stays the same (assign score between scores of
        #gene before and after own rank
        indices_to_change = range(1, len(interleaved_ranking)-1, 2)
        for index in indices_to_change:
            pregene_entry = interleaved_ranking.iloc[index - 1,]
            pre_score = pregene_entry.iloc[1]

            postgene_entry = interleaved_ranking.iloc[index + 1,]
            post_score = postgene_entry.iloc[1]

            #set new score to something between scores of gene before and after in this ranking
            gene_entry = interleaved_ranking.iloc[index,]
            gene_entry["score"] = random.uniform(pre_score, post_score)
        self.writeRankingToFile(interleaved_ranking, outputFile)
        end = time.time()
        self.timeLogs = utils.logRuntime(self.timeLogs, start, end, "Feature Selection")
        if self.enableLogFlush:
            utils.flushTimeLog(self.timeLogs, self.loggingDir + self.getName() + ".csv")
        utils.logInfo("######################## " + self.getName() + " finished. ########################")

        return outputFile



class NetworkActivitySelector(NetworkSelector):
    """Selector implementation that selects a set of pathways from the knowledge base and maps the feature space to the pathways.
       Pathway ranking scores are computed based on the average ANOVA p-value of its member genes and the sample classes.
       This method is also used by Chuang et al. and Tian et al. (Discovering statistically significant pathways in expression profiling studies)
       Pathway feature values are computed with an instance of :class:`FeatureMapper` or inheriting classes, whose mapping strategies can vary.
       If pathways should be selected according to another strategy, use this class as an example implementation to implement a new class that inherits from :class:`NetworkSelector`.
       """
    def __init__(self, knowledgebase, featuremapper):
        if isinstance(featuremapper, CORGSActivityMapper):
            name = "CorgsNetworkActivity"
        elif isinstance(featuremapper, PathwayActivityMapper):
            name = "NetworkActivity"
        else:
            name = "NetworkActivity"
        super().__init__(name, knowledgebase, featuremapper)

    def selectPathways(self, pathways):
        """Computes a pathway ranking for the input pathways.
           Computes a pathway score based on the average ANOVA's f-test p-values of a pathway's member genes and the sample classes.

           :param pathways: selector name
           :type pathways: str
           :returns: pathway ranking with pathway scores
           :rtype: :class:`pandas.DataFrame`
           """
        #this selector selects the most significant pathways according to the average t-test of its member genes and the sample classes
        #method used by Chuang et al. and Tian et al. (Discovering statistically significant pathways in expression profiling studies)
        #as we can have > 2 classes, we just use ANOVA instead of t-test
        dataset = self.getUnlabeledData()

        # define input params
        # load data
        labels = self.getLabels()
        le = preprocessing.LabelEncoder()
        numeric_labels = le.fit_transform(labels)

        #run ANOVA (if we have just 2 classes, ANOVA is equivalent to the t-test)
        selector = SelectKBest(f_classif, k="all")
        selector.fit_transform(dataset, numeric_labels)
        pvals = pd.Series(selector.pvalues_, index = dataset.columns)

        #for every pathway, get the average score from its member genes
        pathway_scores = {}
        for pathwayName in pathways:
            genes = pathways[pathwayName].nodes_by_label.keys()
            #check if all genes in genes are in the pvals matrix
            existingGenes = list(set(pvals.index) & set(genes))
            score = pvals.loc[existingGenes].mean()
            pathway_scores[pathwayName] = score

        # if we do not have any pathways, stop here
        if not pathway_scores:
            ranking = pd.DataFrame(columns=["attributeName", "score"])
        else:

            # sort pathways by score in ascending order
            sorted_pathways = sorted(pathway_scores.items(), key=lambda x: x[1])
            #create output: a file with: feature, score, and file index
            feature_ranking_list = list()
            for pathway in sorted_pathways:
                feature_ranking_list.append([pathway[0], pathway[1]])
            ranking = pd.DataFrame(data = np.array(feature_ranking_list), columns = ["attributeName", "score"])

        return ranking





############################### FEATURE MAPPERS ###############################

class FeatureMapper():
    """Abstract.
       Inherit from this class and implement :meth:`FeatureMapper.mapFeatures` to implement a new mapping strategy.
       Maps the feature space of the given input data to a given set of pathways.
       Computes a new feature value for every feature and sample based on the implemented strategy.
       """
    def __init__(self, ):
        super().__init__()

    @abc.abstractmethod
    def mapFeatures(self, original_data, pathways):
        """Abstract method.
           Implement this method when inheriting from this class.
           Carries out the actual feature mapping.

           :param original_data: the original data set of which to map the feature space.
           :type original_data: :class:`pandas.DataFrame`
           :param pathways: dict of pathway names as keys and corresponding pathway :class:`pypath.Network` objects as values
           :type pathways: dict
           :returns: the transformed data set with new feature values
           :rtype: :class:`pandas.DataFrame`
           """
        pass

    def getUnlabeledData(self, dataset):
        """Removes the labels from the data set.

           :param dataset: data set from which to remove the labels.
           :type dataset: :class:`pandas.DataFrame`
           :returns: data set without labels.
           :rtype: :class:`pandas.DataFrame`
           """
        return dataset.loc[:, dataset.columns != "classLabel"]

    def getLabels(self, dataset):
        """Gets the dataset labels.

           :param dataset: data set from which to extract the labels.
           :type dataset: :class:`pandas.DataFrame`
           :returns: label vector of the data set.
           :rtype: :class:`pandas.Series`
           """
        return dataset.iloc[:,0]

    def getFeatures(self, dataset):
        """Gets the features of a data set.

           :param dataset: data set from which to extract the features.
           :type dataset: :class:`pandas.DataFrame`
           :returns: feature vector of the data set.
           :rtype: :class:`pandas.Series`
           """
        return dataset.columns[1:]

    def getSamples(self, dataset):
        """Gets all samples in a data set.

           :param dataset: data set from which to extract the samples.
           :type dataset: :class:`pandas.DataFrame`
           :returns: list of samples from the data set.
           :rtype: list
           """
        return dataset.index.tolist()

    def getPathwayGenes(self, pathway, genes):
        """Returns the intersection of a given set of genes and the genes contained in a given pathway.

           :param pathway: pathway object from which to get the genes.
           :type pathway: :class:`pypath.Network`
           :param genes: list of gene names.
           :type genes: list of str
           :returns: list of genes that are contained in both the pathway and the gene list.
           :rtype: list of str
           """
        pathway_genes = pathway.nodes_by_label
        contained_pathway_genes = list(set(pathway_genes.keys()) & set(genes))

        return contained_pathway_genes

class CORGSActivityMapper(FeatureMapper):
    """Pathway mapper that implements the strategy described by Lee et al.: "Inferring Pathway Activity toward Precise Disease Classification"
       Identifies CORGS genes for every pathway: uses random search to find the minimal set of genes for which the pathway activity score is maximal.
       First, every sample receives an activity score, which is the average expression level of the (CORGS) genes / number of genes.
       The computed activity scores are then used for f-testing with the class labels, and the p-values are the new pathway feature values.
       These steps are executed again and again until the p-values are not decreasing anymore.
       """

    def __init__(self, ):
        super().__init__()

    def getANOVAscores(self, data, labels):
        """Applies ANOVA f-test to test the association/correlation of a feature (pathway) with a given label.
           The feature has activity scores (computed from CORGS genes) for every sample, which are to be tested for the labels.

           :param data: the data set which to test for correlation with the labels (typically feature scores of a pathway for samples).
           :type data: :class:`pandas.DataFrame`
           :param labels: class labels to use for f-test.
           :type labels: :class:`pandas.Series`

           :returns: series of p-values for every sample.
           :rtype: :class:`pandas.Series`
           """
        le = preprocessing.LabelEncoder()
        numeric_labels = le.fit_transform(labels)

        # run ANOVA (if we have just 2 classes, ANOVA is equivalent to the t-test)
        selector = SelectKBest(f_classif, k="all")

        if (isinstance(data, pd.Series)):
            genes = data.name
            data = data.values.reshape(-1, 1)
        else:
            genes = data.columns
        selector.fit_transform(data, numeric_labels)
        pvals = pd.Series(selector.pvalues_, index=genes)

        return pvals

    def computeActivityScore(self, sampleExpressionLevels):
        """Computes the activity score of a given set of genes for a specific sample.
           The activity score of a sample is the mean expression value of the given genes divided by the overall number of given genes.

           :param sampleExpressionLevels: data set containing expression levels from a given set of genes for samples.
           :type sampleExpressionLevels: :class:`pandas.DataFrame`
           :returns: activity scores for the given samples.
           :rtype: :class:`pandas.Series`
           """
        #activityScore for a sample is the average expression level of the genes / number of genes
        x = sampleExpressionLevels.mean() / len(sampleExpressionLevels)
        return x

    def computeActivityVector(self, expressionLevels):
        """Computes the activity score of a given set of genes for a all samples.

           :param expressionLevels: input data set of expression levels for a given set of (CORGS) genes.
           :type expressionLevels: :class:`pandas.DataFrame`
           :returns: instance of a feature selector implementation.
           :rtype: :class:`pandas.DataFrame` or inheriting class
           """

        activityVector = expressionLevels.apply(self.computeActivityScore, axis = 1)

        return activityVector


    def mapFeatures(self, original_data, pathways):
        """Carries out the actual feature mapping.
           Follows the strategy described by Lee et al.: "Inferring Pathway Activity toward Precise Disease Classification"
           Identifies CORGS genes for every pathway: uses random search to find the minimal set of genes for which the pathway activity score is maximal.
           First, every sample receives an activity score, which is the average expression level of the (CORGS) genes / number of genes.
           The computed activity scores are then used for f-testing with the class labels, and the p-values are the new pathway feature values.
           These steps are executed again and again until the p-values are not decreasing anymore.

           :param original_data: the original data set of which to map the feature space.
           :type original_data: :class:`pandas.DataFrame`
           :param pathways: dict of pathway names as keys and corresponding pathway :class:`pypath.Network` objects as values
           :type pathways: dict
           :returns: the transformed data set with new feature values
           :rtype: :class:`pandas.DataFrame`
           """
        # create pathway activity score S(G) for pathway x and sample y:
        # find minimal set of genes G so that S(G) is locally maximal
        unlabeledData = self.getUnlabeledData(original_data)
        genes = self.getFeatures(original_data)
        samples = self.getSamples(original_data)
        labels = self.getLabels(original_data)

        # create a new dataframe that has pathways as features
        pathways_scores = {}
        pathways_scores["Unnamed: 0"] = samples
        classLabels = pd.DataFrame(original_data.loc[:, "classLabel"])

        # for every pathway, compute activity score for every sample
        for pathwayname in pathways.keys():
            # 1. map genes to network
            pathway = pathways[pathwayname]
            pathwaygenes = self.getPathwayGenes(pathway, genes)
            if (len(pathwaygenes) == 0):
                # if none of the genes in the pathway are in the data, just set the pathwayscore to 0
                utils.logWarning(
                    "WARNING: No genes of pathway " + pathwayname + " found in dataset for feature mapping. Assign activity score of 0.0 to all samples.")
                corgs_activities = [0.0] * len(samples)
                continue

            #2. take top scored gene as seed gene and compute S(gene)
            k = 0
            #set initial scores to make sure we get at least one run
            score_k1 = 0
            score_k = -1
            max_k = len(pathwaygenes)
            #repeat while S(k+1) > S(k), k = #corgs genes
            # stop if we have already included all genes of pathway
            while (score_k1 > score_k) and (k <= max_k):
                #former k+1 score is now our k score
                score_k = score_k1
                corgs_genes = pathwaygenes[:k+1]
                corgs_activities = self.computeActivityVector(unlabeledData.loc[:,corgs_genes])
                score_k1 = self.getANOVAscores(corgs_activities, labels)[0]

                k += 1
            # once greedy search has finished, collect activity scores as new pathway feature values
            pathways_scores[pathwayname] = corgs_activities

        # create final dataframe with pathways as features
        pathwaydata = pd.DataFrame.from_dict(data=pathways_scores)
        pathwaydata = pathwaydata.set_index("Unnamed: 0")
        # add class labels to dataset
        mappedData = classLabels.merge(pathwaydata, right_index = True, left_index = True)

        # 4. return new features
        return mappedData




class PathwayActivityMapper(FeatureMapper):
    """Pathway mapper that implements a strategy that is related to Vert and Kanehisa's strategy: Vert, Jean-Philippe, and Minoru Kanehisa. "Graph-driven feature extraction from microarray data using diffusion kernels and kernel CCA." NIPS. 2002.
       Computes pathway activity scores for every sample and pathway as new feature values.
       The feature value is the average of: expression level weighted by gene variance and neighbor correlation score)
       """
    def __init__(self, ):
        super().__init__()

    def getAverageCorrelation(self, correlations, gene, neighbors):
        """Computes the average correlation from the correlations of a given gene and its neighbors.

           :param correlations: correlation matrix of all genes.
           :type correlations: :class:`pandas.DataFrame`
           :param gene: gene name whose average neighbor correlation to compute.
           :type gene: str
           :param neighbors: list of gene names that are neighbors of the given gene.
           :type neighbors: list of str
           :returns: average correlation value.
           :rtype: float
           """
        containedNeighbors = list(set(neighbors) & set(correlations.columns))
        if len(containedNeighbors) == 0:
            return 0
        else:
            entries = correlations.loc[gene, containedNeighbors]
            return entries.mean()

    def computeGeneVariances(self, data):
        """Computes the variances for every gene across all samples.

           :param data: data set with expression values.
           :type data: :class:`pandas.DataFrame`
           :returns: variance for every gene.
           :rtype: :class:`pandas.Series`
           """
        selector = VarianceThreshold()
        selector.fit_transform(data)
        return selector.variances_



    def mapFeatures(self, original_data, pathways):
        """Executes the actual feature mapping procedure.
           A feature value  is the average of (for every gene in a pathway): (expression level weighted by gene variance and neighbor correlation score)

           :param original_data: the original data set of which to map the feature space.
           :type original_data: :class:`pandas.DataFrame`
           :param pathways: dict of pathway names as keys and corresponding pathway :class:`pypath.Network` objects as values
           :type pathways: dict
           :returns: the transformed data set with new feature values
           :rtype: :class:`pandas.DataFrame`
           """
        #create pathway activity score for pathway x and sample y: average of all (gene expressions weighted by gene variance and neighbor correlations)
        # compute gene variances
        unlabeledData = self.getUnlabeledData(original_data)
        genes = self.getFeatures(original_data)
        samples = self.getSamples(original_data)

        variances = self.computeGeneVariances(unlabeledData)
        vars = pd.Series(variances, genes)
        # compute correlation scores for genes
        correlations = unlabeledData.corr(method="pearson")

        # create a new dataframe that has pathways as features
        pathways_scores = {}
        pathways_scores["Unnamed: 0"] = samples
        classLabels = pd.DataFrame(original_data.loc[:,"classLabel"])

        # for every pathway, compute activity score for every sample
        # set pathways to the correct index as provided in the ranking
        for pathwayname in pathways.keys():
            # 2. map genes to network
            pathway = pathways[pathwayname]
            pathwaygenes = self.getPathwayGenes(pathway, genes)


            #3. precompute variance and average correlations for every gene in the pathway
            scoreparts = {}
            for gene in pathwaygenes:
                variance = vars.loc[gene]
                geneNeighbors = pathway.partners(gene)
                neighborNames = [neighbor.label for neighbor in geneNeighbors]
                average_correlations = self.getAverageCorrelation(correlations, gene, neighborNames)
                scoreparts[gene] = variance * average_correlations

            # 4. compute pathway activity score for every sample
            prescores = pd.Series(scoreparts)
            pathwayscores = []
            if (len(pathwaygenes) == 0):
                # if none of the genes in the pathway are in the data, just set the pathwayscore to 0
                utils.logWarning("WARNING: No genes of pathway " + pathwayname + " found in dataset. Assign activity score of 0.0 to all samples.")
                pathwayscores = [0.0] * len(samples)
            else:
                for sample in samples:
                    expression_values = original_data.loc[sample, pathwaygenes]
                    score = expression_values * prescores.loc[pathwaygenes]
                    # activity score for pathway x and sample y: average of all (gene expressions weighted by gene variance and neighbor correlations)
                    activityScore = score.mean()
                    pathwayscores.append(activityScore)

            pathways_scores[pathwayname] = pathwayscores


        # create final dataframe with pathways as features
        pathwaydata = pd.DataFrame.from_dict(data=pathways_scores)
        pathwaydata = pathwaydata.set_index("Unnamed: 0")

        #add class labels to dataset
        mappedData = classLabels.merge(pathwaydata, left_index = True, right_index = True)

        # 4. return new features
        return mappedData
