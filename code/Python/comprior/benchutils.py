import os, configparser, logging
import pandas as pd
import subprocess
import knowledgebases as kbs

metricScales = {
    "kappa": (-1, 1),
    "accuracy": (0, 100),
    "AUROC": (0,1),
    "sensitivity": (0,1),
    "specificity": (0,1),
    "F1": (0,1),
    "matthewcoef": (-1,1),
    "precision": (0,1)
}

##### CONFIG #####
config = None
LOGGER_NAME = "Comprior"

def loadConfig(path):
    """Loads the config files.

       :param path: absolute path or list of absolute paths to the config files. For multiple config files specifying the same parameters, the ones from the last config file in the list will be used.
       :type path: str or list of str
       """
    global config
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read(path)

    #check dependencies
    if int(getConfigValue("Gene Selection - General", "selectKgenes")) < int(getConfigValue("Evaluation", "topKmax")):
       raise Exception("selectKgenes param in Gene Selection config is smaller than topKmax param from Evaluation (topKgenes must be >= topKmax). Stop here.")


def getConfig(category):
    """Get the config entries for a particular category.

       :param category: category name.
       :type category: str
       :return: all parameters for that config category
       :rtype: dict
       """
    global config
    return config[category]

def getConfigValue(category, identifier):
    """Get the value for a given config parameter.

       :param category: the parameter's category name.
       :type category: str
       :param identifier: the parameter name.
       :type identifier: str
       :return: the parameter value.
       :rtype: str
       """
    global config
    return config[category][identifier]

def getConfigBoolean(category, identifier):
    """Get the boolean value for a given config parameter.

       :param category: the parameter's category name.
       :type category: str
       :param identifier: the parameter name.
       :type identifier: str
       :return: the parameter boolean value.
       :rtype: bool
       """
    global config
    return config.getboolean(category, identifier)

##### FILE READING AND WRITING #####
def loadRanking(rankingFile):
    """Load a feature ranking from a file.

       :param rankingFile: absolute path to the file containing a feature ranking.
       :type rankingFile: str
       :return: the feature ranking as a DataFrame.
       :rtype: :class:`pandas.DataFrame`
       """
    try:
        ranking = pd.read_csv(rankingFile, sep = "\t")
    except:
        #in case ranking is empty, just create an empty dataframe
        ranking = pd.DataFrame(columns = ["attribute", "score"])

    return ranking

##### DIRECTORY MANAGEMENT #####
def createOrClearDirectory(directoryLocation):
    """If the provided directory location is already existing, remove all files in that directory.
       Create a new directory otherwise.

       :param directoryLocation: absolute path to the directory that must be cleared or created.
       :type directoryLocation: str
       """
    # create directory if not already existing
    if not os.path.isdir(directoryLocation):
        createDirectory(directoryLocation)
    else:
        for file in os.listdir(directoryLocation):
            if file == ".gitignore":
                continue
            os.remove(os.path.join(directoryLocation,file))

def createDirectory(directoryLocation):
    """Creates a directory.

       :param directoryLocation: absolute path to the directory to be created.
       :type directoryLocation: str
       """
    try:
        os.makedirs(directoryLocation)
    except:
        return

def removeDirectoryContent(directoryLocation):
    """Remove the files inside a directory.

       :param directoryLocation: absolute path to the directory that must be cleared.
       :type directoryLocation: str
       """
    try:
        filelist = [f for f in os.listdir(directoryLocation)]
        for f in filelist:
            if f == ".gitignore":
                continue
            removeFile(directoryLocation + f)
    except:
        #no directory to delete
        return

def removeFile(file):
    """Delete a file.

       :param file: absolute path to the file that must be deleted.
       :type file: str
       """
    #try:
    os.remove(file)
    #except:
    #    return #No FILE to delete

    #remove all intermediate and result files before running anything new
def cleanupResults():
    """Remove all intermediate files from former runs, e.g. generated during preprocessing or mapping.
       """
    removeDirectoryContent(getConfigValue("General", "preprocessing"))
    removeDirectoryContent(getConfigValue("General", "preprocessing") + "preprocessed/")
    removeDirectoryContent(getConfigValue("General", "preprocessing") + "ready/")
    removeDirectoryContent(getConfigValue("General", "crossVal_preprocessing") + "preprocessed/")
    removeDirectoryContent(getConfigValue("General", "crossVal_preprocessing") + "ready/")
    removeDirectoryContent(getConfigValue("General", "externalKbDir"))
    removeDirectoryContent(getConfigValue("General", "intermediateDir") + "identifierMappings/")
    removeDirectoryContent(getConfigValue("General", "intermediateDir"))

##### LOGGING #####

def createLogger(outputPath):
    """Create a logger for Comprior. Creates two handlers for this logger: one for console output that only contains high-level status update logs and error messages.
       Warnings and other tracing information is written to an extra log file.

       :param outputPath: absoulte path to where the log file will be stored.
       :type outputPath: String
       """
    FORMAT_STR = '%(asctime)s %(message)s'
    LOG_FILE = outputPath + "/" + LOGGER_NAME + ".log"

    #create logger and set default level to debug
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.setLevel(logging.DEBUG)
    formatter = logging.Formatter(FORMAT_STR)

    #add handler to write log to file at custom level
    fh = logging.FileHandler(LOG_FILE)
    fh.name = 'File Logger'
    fh.level = logging.DEBUG
    fh.formatter = formatter
    LOGGER.addHandler(fh)

    #add handler to write log to console output at custom level
    ch = logging.StreamHandler()
    ch.name = 'Console Logger'
    ch.level = logging.WARNING
    ch.formatter = formatter
    LOGGER.addHandler(ch)

def logDebug(message):
    """Write a log at debug level.

       :param message: the log message to print.
       :type message: String
       """
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.debug(message)

def logInfo(message):
    """Write a log at info level.

       :param message: the log message to print.
       :type message: String
       """
    #we do want to have the status updates in our console output but not the warnings, but info level is lower than warning level
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.critical(message)

def logWarning(message):
    """Write a log at warning level.

       :param message: the log message to print.
       :type message: String
       """
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.warning(message)

def logError(message):
    """Write a log at error level.

       :param message: the log message to print.
       :type message: String
       """
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.error(message)

def createTimeLog():
    """Create the data structure for tracing runtimes of feature selection approaches.

       :return: the logging data structure.
       :rtype: :class:`pandas.DataFrame`
       """

    return pd.DataFrame(columns = ["Description", "Start", "End", "Duration"])

def flushTimeLog(timeLogs, outputFilePath):
    """Write the whole log (of runtimes) to a file.

       :param timeLogs: the logs in a DataFrame.
       :type timeLogs: :class:`pandas.DataFrame`
       :param outputFilePath: absolute path to the log file.
       :type outputFilePath: str
       """
    timeLogs.to_csv(outputFilePath, index = False, sep = "\t")

def logRuntime(timeLogs, start, end, message):
    """Write a runtime log entry and add it to the runtime log data structure.

       :param timeLogs: logs to which the new entry should be added
       :type timeLogs: :class:`pandas.DataFrame`
       :param start:  starting time.
       :type start: str
       :param end:  ending time.
       :type end: str
       :param message: description of that entry.
       :type message: str
       :return: updated logs.
       :rtype: :class:`pandas.DataFrame`
       """
    duration = end - start
    log = pd.DataFrame(data = [[message, start, end, duration]], columns = ["Description", "Start", "End", "Duration"] )
    return timeLogs.append(log, ignore_index = True)

##### R/JAVA CODE HANDLING #####

def runRCommand(rConfig, scriptName, params):
    """Run external R code.

       :param rConfig: R config parameters (store paths to Rscript and the R code).
       :type rConfig: dict
       :param scriptName: name of the R script to be executed.
       :type scriptName: str
       :param params: list of parameters that will be forwarded to the R script.
       :type params: list of str
       """
    args = [rConfig["RscriptLocation"], scriptName]
    args.extend(params)
    logDebug("DEBUG: Invoking R script with command: " + " ".join(args))
    p = subprocess.Popen(args, cwd=rConfig["code"], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = p.communicate()
    err = err.decode("utf-8")
    out = out.decode("utf-8")
    #make sure only the important messages are shown in the console output
    if (err != ""):
        if (("halt" in err) or ("Error" in err)):
            logWarning("WARNING: Something went wrong in this R script: " + err)
        else:
            logDebug(err)

    if (out != ""):
        logDebug(out)


def runJavaCommand(javaConfig, scriptName, params):
    """Run external Java code.

       :param javaConfig: java config parameters (store paths to java and the java code).
       :type javaConfig: dict
       :param scriptName: name of the jar to be executed.
       :type scriptName: str
       :param params: list of parameters that will be forwarded to the jar.
       :type params: list of str
       """
    args = [javaConfig["JavaLocation"], "-jar", javaConfig["code"] + scriptName]
    args.extend(params)
    logDebug("DEBUG: Invoking Java code with command: " + " ".join(args))

    p = subprocess.Popen(args, cwd=javaConfig["code"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    err = err.decode("utf-8")
    out = out.decode("utf-8")
    if (err != ""):
        if (("halt" in err) or ("Error" in err)):
            logWarning("WARNING: Something went wrong in this R script: " + err)
        else:
            logDebug(err)

    if (out != ""):
        logDebug(out)


def mapIdentifiers(itemList, originalFormat, desiredFormat):
    """Write a log entry and add it to the log data structure.

       :param itemList: list of identifiers, e.g. gene names, to be mapped
       :type itemList: list of str
       :param originalFormat:  current format of the identifiers.
       :type originalFormat: str
       :param desiredFormat:  desired format to which the identifiers should be mapped.
       :type desiredFormat: str
       :return: mapping table where every item from itemList is now mapped to desiredFormat.
       :rtype: :class:`pandas.DataFrame`
       """

    mapping = retrieveMappings(itemList, originalFormat, desiredFormat)
    return mapping


def mapGeneList(genes, originalFormat, desiredFormat, outputFile):
    """Map a list of genes to the desired format.

       :param genes: list of gene names to be mapped
       :type genes: list of str
       :param originalFormat:  current format of the gene names.
       :type originalFormat: str
       :param desiredFormat:  desired format to which the gene names should be mapped.
       :type desiredFormat: str
       :param outputFile:  absolute path to the output file in which the mapping should be stored.
       :type outputFile: str
       :return: list of mapped gene names.
       :rtype: list of str
       """
    mapping = mapIdentifiers(genes, originalFormat, desiredFormat)
    mapped_genes = mapping[desiredFormat]
    mapped_genes.to_csv(outputFile)

    return mapped_genes


def mapRanking(ranking, originalFormat, desiredFormat, outputFile):
    """Map the feature names of a ranking to the desired format.

       :param ranking: DataFrame of the ranking.
       :type ranking: :class:`pandas.DataFrame`
       :param originalFormat:  current format of the feature names in the ranking.
       :type originalFormat: str
       :param desiredFormat:  desired format to which the feature names should be mapped.
       :type desiredFormat: str
       :param outputFile:  absolute path to the output file in which the mapped feature ranking should be stored.
       :type outputFile: str
       :return: mapped feature ranking.
       :rtype: :class:`pandas.DataFrame`
       """
    first_col = ranking.columns[0]
    items = list(ranking[first_col])
    mapping = mapIdentifiers(items, originalFormat, desiredFormat)
    mapped_ranking = mapping.merge(ranking, right_on=ranking.columns[0], left_on=originalFormat)
    # sort by orderColumn, e.g. the score
    mapped_ranking = mapped_ranking.sort_values(by="score", ascending=False)
    # drop duplicate items (n:1, when two identifiers were mapped to the same name)
    mapped_ranking = mapped_ranking.drop_duplicates(subset=[desiredFormat], keep="first")
    # drop original attributeName column that contained probeset IDs
    cols = list(mapped_ranking.columns)
    cols.remove(cols[0])
    cols.remove(cols[1])
    mapped_ranking = mapped_ranking[cols]
    # rename first column with new Gene IDs to have original column name
    cols[0] = first_col
    mapped_ranking.columns = cols
    mapped_ranking.to_csv(outputFile)

    return mapped_ranking


def retrieveMappings(itemList, originalFormat, desiredFormat):
    """Query the knowledge base to map the identifiers.
       We have mapping via BiomaRt and gConvert available.
       gConvert is currently used because BiomaRt is unstable and blocks when parallel queries are sent.

       :param itemList: list of identifier names to be mapped
       :type itemList: list of str
       :param originalFormat:  current format of the identifiers.
       :type originalFormat: str
       :param desiredFormat:  desired format to which the identifiers should be mapped.
       :type desiredFormat: str
       :return: mapping table for all identifiers.
       :rtype: :class:`pandas.DataFrame`
       """
    # create directory and paths for mapped gene rankings
    kbs_factory = kbs.KnowledgeBaseFactory()
    mart = kbs_factory.createKnowledgeBase("gConvert")
    # mart = kbs_factory.createKnowledgeBase("Biomart")
    mapping = mart.mapItems(itemList, originalFormat, desiredFormat)
    return mapping


def mapDataMatrix(inputMatrix, genesInColumns, originalFormat, desiredFormat, outputFile, labeled):
    """Map the features of a data set to the desired format.

       :param inputMatrix: DataFrame of the ranking.
       :type inputMatrix: :class:`pandas.DataFrame`
       :param genesInColumns: if the genes/features are located in the columns.
       :type genesInColumns: bool
       :param originalFormat:  current format of the feature names in the data set.
       :type originalFormat: str
       :param desiredFormat:  desired format to which the feature names should be mapped.
       :type desiredFormat: str
       :param outputFile:  absolute path to the output file in which the mapped data set should be stored.
       :type outputFile: str
       :param labeled:  if the data matrix is additionally labeled.
       :type labeled: bool
       :return: mapped data set.
       :rtype: :class:`pandas.DataFrame`
       """

    if labeled:
        items = list(inputMatrix.columns[1:])
        labels = inputMatrix.iloc[:, 0]
    else:
        items = list(inputMatrix.columns)
    mapping = mapIdentifiers(items, originalFormat, desiredFormat)
    if genesInColumns:
        # transpose matrix so that genes are in a single column that can be joined
        matrix = inputMatrix.transpose()
    mapped_matrix = mapping.merge(matrix, right_on=matrix.index, left_on=originalFormat)

    # drop duplicates items (1:n; when one identifier was mapped to multiple names), as otherwise we introduce redundancy to the data
    mapped_matrix = mapped_matrix.drop_duplicates(subset=[originalFormat], keep="first")
    # drop duplicates items (n:1; when multiple identifier were mapped to the same name), as otherwise we have duplicate column names
    mapped_matrix = mapped_matrix.drop_duplicates(subset=[desiredFormat], keep="first")
    # drop original attributeName column that contained probeset IDs
    mapped_matrix = mapped_matrix[mapped_matrix.columns[1:]]
    mapped_matrix = mapped_matrix.set_index(desiredFormat)
    final_matrix = mapped_matrix.transpose()
    if labeled:
        final_matrix = labels.to_frame().merge(final_matrix, left_index = True, right_index = True)

    final_matrix.to_csv(outputFile)
    return final_matrix