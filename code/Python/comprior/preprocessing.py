import pandas as pd
from abc import abstractmethod
import benchutils, os, time

class Preprocessor:
    """Super class of all preprocessor implementations.
       Inherit from this class and implement :meth:`preprocessing.Preprocessor.preprocess()` if you want to add a new preprocessor class.

       :param input: absolute path to the input file.
       :type input: str
       :param metadata: absolute path to the metadata file.
       :type metadata: str
       :param output: absolute path to the output directory.
       :type output: str
       """

    def __init__(self, input, metadata, output):
        self.input = input
        self.metadata = metadata
        self.output = output
        super().__init__()

    @abstractmethod
    def preprocess(self):
        """Abstract method.
           Interface method that is invoked externally to trigger preprocessing.

           :return: absolute path to the preprocessed output file.
           :rtype: str
           """
        pass

class MappingPreprocessor(Preprocessor):
    """Maps the input data set to a desired format.

       :param input: absolute path to the input file.
       :type input: str
       :param output: absolute path to the output directory.
       :type output: str
       :param currentFormat: current identifier format.
       :type currentFormat: str
       :param desiredFormat: desired identifier format.
       :type desiredFormat: str
       :param labeled: boolean value if the input data is labeled.
       :type labeled: bool
       """

    def __init__(self, input, output, currentFormat, desiredFormat, labeled):
        self.currentFormat = currentFormat
        self.desiredFormat = desiredFormat
        self.labeled = labeled
        super().__init__(input, None, output)

    def preprocess(self):
        """Maps the identifiers in the input dataset to the desired format that was specified when constructing the preprocessor.

           :return: absolute path to the mapped file.
           :rtype: str
           """
        inputMatrix = pd.read_csv(self.input, index_col = 0)

        original_filename = self.input.split("/")[-1]
        mapped_filename = "mapped_" + self.desiredFormat + "_" + original_filename
        output = self.input
        output_filepath =  "/".join(self.input.split("/")[0:-1])
        #as the DataFormatter always transposes the data before any further processing, we can expect all genes to be in the columns
        genesInColumn = "true"
        #only map genes if the current format is not the desired format
        if (self.currentFormat != self.desiredFormat):
            output = output_filepath + "/" + mapped_filename
            benchutils.mapDataMatrix(inputMatrix, genesInColumn, self.currentFormat, self.desiredFormat, output, self.labeled)

        return output

class FilterPreprocessor(Preprocessor):
    """Filters features or samples above a user-defined threshold of missing values.

       :param input: absolute path to the input file.
       :type input: str
       :param metadata: absolute path to the metadata file.
       :type metadata: str
       :param output: absolute path to the output directory.
       :type output: str
       :param config: configuration parameter for preprocessing as specified in the config file.
       :type config: str
       """
    def __init__(self, input, metadata, output):
        self.config = benchutils.getConfig("Preprocessing")
        super().__init__(input, metadata, output)

    def preprocess(self):
        """Depending on what is specified in the config file, filter samples and/or features.
           Remove all samples/features that have missing values above the threshold specified in the config.

           :return: absolute path to the filtered output file.
           :rtype: str
           """
        filtered_data = pd.read_csv(self.input)

        if self.config.getboolean("filterMissingsInGenes"):
            # first filter out the genes that have more missings than threshold
            filtered_data = self.filterMissings(self.config["threshold"], filtered_data)
        if self.config.getboolean("filterMissingsInSamples"):
            # second transpose matrix and filter out samples that have more missings than threshold
            filtered_samples = self.filterMissings(self.config["threshold"], filtered_data.T)
            filtered_data = filtered_samples.T

        # transpose back into original orientation and save
        filePrefix = self.input.split("/")[-1].split(".")[
            0]  # split path by / to receive filename, split filename by . to receive filename without ending
        filename = self.output + filePrefix + "_filtered.csv"
        filtered_data.to_csv(filename, index=False)
        return filename

    def filterMissings(self, threshold, data):
        """Filter the data for entries that have missing information above the given threshold.

           :param threshold: maximum percentage of allowed missing items as string.
           :type threshold: str
           :param data: a DataFrame to be filtered
           :type data: :class:`pandas.DataFrame`
           :return: filtered DataFrame.
           :rtype: :class:`pandas.DataFrame`
           """

        #replace NAs by 0 for counting
        data.fillna(0).astype(bool).sum(axis=1)

        filtered_columns = data.columns


        #find out threshold, i.e. minimum number of non-zero in real numbers
        rowNumber = data.shape[0]
        min_nonZeros = int(rowNumber - ((rowNumber * int(threshold))/100))

        zero_counts = data.astype(bool).sum(axis=0)

        for columnID, nonZeros in zero_counts.items():
            if nonZeros <= min_nonZeros:
                filtered_columns = filtered_columns.drop(columnID)


        return data[filtered_columns]

class DataTransformationPreprocessor(Preprocessor):
    """Transform the input data to have features in the columns for subsequent processing.

       :param input: absolute path to the input file.
       :type input: str
       :param metadata: absolute path to the metadata file.
       :type metadata: str
       :param output: absolute path to the output directory.
       :type output: str
       :param dataSeparator: delimiter to use when parsing the input file.
       :type dataSeparator: str
       """
    def __init__(self, input, metadata, output, dataSeparator):
        self.transposeMatrix = not benchutils.getConfigBoolean("Dataset", "genesInColumns")
        self.dataSeparator = dataSeparator
        super().__init__(input, metadata, output)

    def preprocess(self):
        """If not already so, transpose the input data to have the features in the columns.

           :return: absolute path to the correctly formatted output file.
           :rtype: str
           """
        df = pd.read_csv(self.input, sep=self.dataSeparator, index_col = 0)
        #ATTENTION: this processing assumes that the data is formatted in a way that header and index are automatically recognized. remove trailing commas/separators at first line of the file for this to be achieved
        if self.transposeMatrix:
            df = df.T

        filePrefix = self.input.split("/")[-1].split(".")[
            0]  # split path by / to receive filename, split filename by . to receive filename without ending
        filename = self.output + filePrefix + "_transposed.csv"

        df.to_csv(filename)
        return filename

class MetaDataPreprocessor(Preprocessor):
    """Add labels to input data.
       Get labels from meta data attribute that was specified in the user config.

       :param input: absolute path to the input file.
       :type input: str
       :param metadata: absolute path to the metadata file.
       :type metadata: str
       :param output: absolute path to the output directory.
       :type output: str
       :param dataSeparator: delimiter to use when parsing the input and metadata file.
       :type dataSeparator: str
       :param diseaseColumn: column name of the class labels.
       :type diseaseColumn: str
       :param transposeMetadataMatrix: boolean value if the identifier names are located in the columns, as specified in the config file.
       :type transposeMetadataMatrix: bool
       """
    def __init__(self, input, metadata, output, separator):
        self.diseaseColumn = benchutils.getConfigValue("Dataset", "classLabelName")
        self.transposeMetadataMatrix = not benchutils.getConfigBoolean("Dataset", "metadataIDsInColumns")
        self.separator = separator
        super().__init__(input, metadata, output)

    def preprocess(self):
        """Labels all samples of a data set.
           Labels are taken from the corresponding metadata file and the metadata attribute that was specified in the config file.
           Samples without metadata information well be assigned to class "NotAvailable".

           :return: absolute path to the labeled data set.
           :rtype: str
           """
        df = pd.read_csv(self.input, index_col = 0)
        diseaseCodes = pd.read_csv(self.metadata, sep = self.separator, index_col = 0, quotechar = '"')

        diseaseColumn = []

        if self.transposeMetadataMatrix:
            diseaseCodes = diseaseCodes.T

        #iterate through all sample IDs and select the corresponding disease/annotation from the metadata for it
        for sample in df.index:
            try:
                diseaseCode = diseaseCodes[sample][self.diseaseColumn]
            except:
                diseaseCode = "NotAvailable"
                print("No classLabel code found for sample " + str(sample) + ". Assign class NotAvailable.")
            diseaseColumn.append(diseaseCode)

        df.insert(0, column="classLabel", value=diseaseColumn)

        df_without_missings = df.dropna(subset=['classLabel'])
        filePrefix = self.input.split("/")[-1].split(".")[
            0]  # split path by / to receive filename, split filename by . to receive filename without ending
        filename = self.output + filePrefix + "_withClassLabels.csv"
        df_without_missings.to_csv(filename)
        return filename

####### PREPROCESSOR: moves a dataset into its respective folder #######
class DataMovePreprocessor(Preprocessor):
    """Moves the input data set to the specified location.

       :param input: absolute path to the input file.
       :type input: str
       :param output: absolute path to the output directory.
       :type output: str
       """

    def __init__(self, input, output):
        super().__init__(input, None, output)

    def preprocess(self):
        """Moves a file (self.input) to another location (self.output).
           Typically used at the end of preprocessing, when the final data set is moved to a new location for the actual analysis.

           :return: absolute path to the new file location.
           :rtype: str
           """
        os.system("cp " + self.input + " " + self.output)
        return self.output


