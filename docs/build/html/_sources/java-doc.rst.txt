Java Code Documentation
========================

Feature Selection
-----------------

.. java:package:: de.hpi.bmg

.. java:type:: public class WEKA_FeatureSelector

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/Java/src/main/java/de/hpi/bmg/WEKA_FeatureSelector.java
      :language: R

    .. raw:: html

      </details>

    Entry point class for running a feature selector on a data set.
    Invoke the jar of this java file to carry out feature selection procedure.
    Is invoked by during feature selection by :class:`featureselection.InfoGainSelector`.

  .. java:method:: public static void main(String[] args)
    :outertype: WEKA_FeatureSelector

    Loads the input data set and creates selector objects based on the provided list of feature selector names.
    Invokes feature selection procedures for all selectors and writes the results to the output directory, one file per selector.

    :param args: The parameters provided when invoking the jar. Provide the following parameters: a) the absolute path to the input data set, b) the absolute path to the output directory (where to write the feature rankings), and c) a string of feature selectors to run, separated by a comma (e.g. "InfoGain,ReliefF").

.. java:type:: public class DataLoader

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/Java/src/main/java/de/hpi/bmg/DataLoader.java
      :language: R

    .. raw:: html

      </details>

    Class for loading a data set from a file.
    Used by classes :java:type:`WEKA_FeatureSelector` and :java:type:`WEKA_Evaluator`.

    .. java:field::  Instances data
       :outertype: DataLoader

    .. java:field::  String sourceFile
       :outertype: DataLoader

    .. java:constructor:: public DataLoader(String sourceFile, String separator)
       :outertype: DataLoader

       Constructor method.
       Loads the data from the specified source file and stores it in the data class attribute.

       :param sourceFile: absolute path of the input file from which to load the data.
       :param separator:  separator to use for file reading, e.g a comma.

    .. java:method:: public Instances getData()
       :outertype: DataLoader

       Returns the loaded data set.

       :return: the data set.


    .. java:method:: private void loadData(String separator)
       :outertype: DataLoader

       Carries out the actual data loading.
       Stores the loaded data set in the data class attribute.

       :param separator: separator to use for file reading, e.g. a comma.


.. java:type:: public class AttributeSelector

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/Java/src/main/java/de/hpi/bmg/AttributeSelector.java
      :language: R

    .. raw:: html

      </details>

    Selector class that carries out the actual feature selection procedure.
    Used by :java:type:`WEKA_FeatureSelector`.

    .. java:constructor:: public AttributeSelector(Instances data, String selectionMethod)
      :outertype: AttributeSelector

      Constructor method.

      :param data: the input data set from which to select the features.
      :param selectionMethod: name of the feature selector to apply.

    .. java:method:: public void saveSelectedAttributes(String saveLocation)
      :outertype: AttributeSelector

      Create a feature ranking list and stores it in the specified file.

      :param saveLocation: absolute path to the output file in which to store the ranking

    .. java:method:: public void selectAttributes()
      :outertype: AttributeSelector

      Do the actual feature selection.
      Based on the selector name, create corresponding instances of classes provided by WEKA and generate a feature ranking.



Evaluation
------------

.. java:type:: public class WEKA_Evaluator

  .. raw:: html

    <details>
    <summary style="color:green;"><font size="-1">[sources]</font></summary>

  .. literalinclude:: ../../code/Java/src/main/java/de/hpi/bmg/WEKA_Evaluator.java
    :language: R

  .. raw:: html

    </details>

  Entry point class for running classification on a data set using only the top 1 up to k features (one classification round per k).
  Is invoked by :class:`evaluation.ClassificationEvaluator` to start the classification procedure.
  Uses :java:type:`DataLoader` to load input data set and :java:type:`Analyzer` to run the actual classification procedure (and compute evaluation metrics).
  Summarizes results from all classifiers and all input data sets (depending on how many features were used) and writes them into output files.


  .. java:method:: public static void main(String[] args)
    :outertype: WEKA_Evaluator

    Process some of the command line parameters (for classifiers, metrics, and input data set locations).
    Invokes classification procedure for every subdirectory (=selection method) that is contained in the input directory.

    :param args: the parameters provided when invoking the jar. Provide the following parameters: a) the absolute path of the directory containing the reduced input data set files (one subdirectory per selection approach), b) the absolute path of the output directory (where to write all evaluation results), c) the minimum number of features to use for classification, d) the maximum number of features to use for classification, e) number of folds for cross validation, f) a string of classifiers, separated by a comma (e.g. "SVM,KNN3,KNN5"), and g) a string of metrics to compute, separated by a comma (e.g. "accuracy,specificity,precision").


  .. java:method:: private static void classifyAndEvaluate(String selectionMethod, String reducedDatasetLocation, String resultLocation, int topKmin, int topKmax, int numFolds, String[] classifiers, String[] evalMetrics)
    :outertype: WEKA_Evaluator

    Runs the overall classification procedure for all feature set sizes of a particular selection approach.
    Creates the specified classifier objects and filewriters for the results.
    For every feature set size from topKmin to topKmax, invoke an instance of :java:type:`Analyzer` to carry out the actual classification and compute the metrics.

    :param selectionMethod: the name of the feature selection method that generated the feature sets to evaluate.
    :param reducedDatasetLocation: absolute path to the directory containing the reduced input files (with increasing feature set sizes) for classification.
    :param resultLocation: absolute path to the output file to which to write the classification results.
    :param topKmin: minimum number of features to use.
    :param topKmax: maximum number of features to use.
    :param numFolds: k parameter for k-fold cross validation.
    :param classifiers: a list of classifier names to use for classification.
    :param evalMetrics: a list of metric names compute for the classification results.


.. java:type:: public class Analyzer

  .. raw:: html

    <details>
    <summary style="color:green;"><font size="-1">[sources]</font></summary>

  .. literalinclude:: ../../code/Java/src/main/java/de/hpi/bmg/Analyzer.java
    :language: R

  .. raw:: html

    </details>

  Carries out the actual k-fold cross validation on the specified classifiers.
  Computes the desired evaluation metrics.
  Uses WEKA.
  Invoked by :java:type:`WEKA_Evaluator`.

   .. java:constructor:: public Analyzer(Instances data)
      :outertype: Analyzer

      Constructor method.

      :param data: the data set to use for classification.
      :return: An instance of :java:type:`Analyzer`.

   .. java:method:: public HashMap<String, String> trainAndEvaluateWithTopKAttributes(int numberOfAttributesRetained, int numFolds, AbstractClassifier[] classifiers, String[] metrics)
      :outertype: Analyzer

      Runs the actual classification procedure.
      Uses WEKA to run multiple classifiers (originally specified in config file) in a k-fold cross validation manner.
      Computes standard evaluation metrics as required afterwards.

      :param numberOfAttributesRetained: the data set to use for classification.
      :param numFolds: number of folds for cross validation.
      :param classifiers: a list of classifier objects to use for classification.
      :param metrics: a list of names of evaluation metrics to compute for the results.
      :return: the evaluation results as HashMap with the metric name as identifier and metric results (across classifiers and average) as values.
