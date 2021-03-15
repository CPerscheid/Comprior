package de.hpi.bmg;

import com.opencsv.CSVWriter;
import org.apache.commons.lang3.ArrayUtils;
import weka.classifiers.AbstractClassifier;
import weka.classifiers.bayes.NaiveBayes;
import weka.classifiers.functions.Logistic;
import weka.classifiers.functions.SMO;
import weka.classifiers.lazy.IBk;
import weka.classifiers.trees.J48;
import weka.classifiers.trees.RandomForest;
import weka.core.Instances;

import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.HashMap;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.logging.Logger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Entry point class for running classification on a data set using only the top 1 up to k features (one classification round per k).
 * Invoke the jar of this java file to start the classification procedure (see an example in :class:`evaluation.ClassificationEvaluator` how to do that).
 * Uses class:`DataLoader` to load input data set and class:`Analyzer` to run the actual classification procedure (and compute evaluation metrics).
 * Summarizes results from all classifiers and all input data sets (depending on how many features were used) and writes them into output files.
 */
public class WEKA_Evaluator {

    private final static Logger LOGGER = Logger.getLogger(WEKA_Evaluator.class.getName());

    /**
     * Process some of the command line parameters (for classifiers, metrics, and input data set locations).
     * Invokes classification procedure for every subdirectory (=selection method) that is contained in the input directory.
     *
     * @param args the parameters provided when invoking the jar. Provide the following parameters:
     *             - absolute path of the directory containing the reduced input data set files (one subdirectory per selection approach).
     *             - absolute path of the output directory (where to write all evaluation results).
     *             - minimum number of features to use for classification.
     *             - maximum number of features to use for classification.
     *             - k param for k-fold cross validation.
     *             - a string of classifiers, separated by a comma (e.g. "SVM,KNN3,KNN5").
     *             - a string of metrics to compute, separated by a comma (e.g. "accuracy,specificity,precision").
     */
    public static void main(String[] args) {

        System.out.println("In WEKA-Evaluator");

        //get reduced data set locations
        File folder = new File(args[0]);
        //the input path should only contain directories - one for each method
        File[] listOfDirs = folder.listFiles();

        //get classifiers from input
        String classifierParams = args[5];
        String[] classifiers = classifierParams.split(",");
        //get metrics to use from input
        String metricParams = args[6];
        String[] metrics = metricParams.split(",");

        for (File methodDir : listOfDirs) {
            System.out.print(methodDir.getAbsolutePath());

            classifyAndEvaluate(methodDir.getName(), methodDir.getAbsolutePath(), new File(args[1], methodDir.getName()).getAbsolutePath(),
                        Integer.parseInt(args[2]), Integer.parseInt(args[3]),  Integer.parseInt(args[4]), classifiers, metrics);
        }
    }

    /**
     * Runs the overall classification procedure for all feature set sizes of a particular selection approach.
     * Creates the specified classifier objects and filewriters for the results.
     * For every feature set size from topKmin to topKmax, invoke an instance of :class:`Analyzer`to carry out the actual classification and compute the metrics.
     *
     * @param selectionMethod the name of the feature selection method that generated the feature sets to evaluate.
     * @param reducedDatasetLocation absolute path to the directory containing the reduced input files (with increasing feature set sizes) for classification.
     * @param resultLocation absolute path to the output file to which to write the classification results.
     * @param topKmin minimum number of features to use.
     * @param topKmax maximum number of features to use.
     * @param numFolds k parameter for k-fold cross validation.
     * @param classifiers a list of classifier names to use for classification.
     * @param evalMetrics a list of metric names compute for the classification results.
     */
    private static void classifyAndEvaluate(String selectionMethod, String reducedDatasetLocation, String resultLocation, int topKmin, int topKmax, int numFolds, String[] classifiers, String[] evalMetrics) {
        LOGGER.info(Integer.toString(Array.getLength(evalMetrics)));
        LOGGER.info(reducedDatasetLocation);
        LOGGER.info(selectionMethod);
        LOGGER.info(reducedDatasetLocation);
        LOGGER.info(resultLocation);

        HashMap<String, CSVWriter> writers = new HashMap<String, CSVWriter>();
        try {
            AbstractClassifier[] classifierObjects = null;
            AbstractClassifier analyzer = null;
            String[] classifierNames = null;
            //create desired classifiers
            for (String method : classifiers) {
                switch (method) {
                    case "SMO":
                        analyzer = new SMO();
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "SMO");
                        break;
                    case "LR":
                        analyzer = new Logistic();
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "LR");
                        break;
                    case "KNN3":
                        analyzer = new IBk();
                        ((IBk) analyzer).setKNN(3);
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "KNN3");
                        break;
                    case "KNN5":
                        analyzer = new IBk();
                        ((IBk) analyzer).setKNN(5);
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "KNN5");
                        break;
                    case "NB":
                        analyzer = new NaiveBayes();
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "NB");
                        break;
                    case "C4.5":
                        analyzer = new J48();
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "C4.5");
                        break;
                    case "RF":
                        analyzer = new RandomForest();
                        classifierObjects = (AbstractClassifier[]) ArrayUtils.addAll(classifierObjects, analyzer);
                        classifierNames = (String[]) ArrayUtils.addAll(classifierNames, "RF");
                        break;
                    default:
                        LOGGER.info(method + " is no valid classifier/analysis module. Do nothing.");
                        continue;
                }

            }

            for (String metric : evalMetrics){
                String filePath = resultLocation + "_" + metric + ".csv";
                writers.put(metric, new CSVWriter(new FileWriter(filePath), '\t', CSVWriter.NO_QUOTE_CHARACTER,
                                    CSVWriter.DEFAULT_ESCAPE_CHARACTER,
                                    CSVWriter.DEFAULT_LINE_END));

                String [] attributes = {"#ofAttributes"};
                String [] average = {"average"};
                String[] headerstart = (String[]) ArrayUtils.addAll(attributes, classifierNames);
                String[] header = (String[]) ArrayUtils.addAll(headerstart, average);
                writers.get(metric).writeNext(header);
            }

            File folder = new File(reducedDatasetLocation);
            File[] listOfDirs = folder.listFiles();

            for (int k = topKmin; k <= topKmax; k++) {
                String datasetFile = "";
                //get the file with k in its name and load its content
                datasetFile = reducedDatasetLocation + "/top" + String.valueOf(k) + "features_" + selectionMethod + ".csv";
                LOGGER.info("###################################");
                LOGGER.info(datasetFile);
                if (new File(datasetFile).isFile()){
                    DataLoader dl = new DataLoader(datasetFile, "\t");
                    Instances data = dl.getData();
                    data.deleteAttributeAt(0);
                    data.setClassIndex(0);
                    Analyzer ce = new Analyzer(data);


                    LOGGER.info(": Starting classification evaluation with models " + Arrays.toString(classifierNames) + " with k of " + k + " [" + datasetFile + "]");

                    HashMap<String, String> results = ce.trainAndEvaluateWithTopKAttributes(k, numFolds, classifierObjects, evalMetrics);
                    for (String metric : writers.keySet()) {
                        CSVWriter writer = writers.get(metric);
                        String resultLine = results.get(metric);
                        String[] line = resultLine.split("\t");
                        writer.writeNext(line);
                        //writer.flush();
                    }
                }
                else {
                    LOGGER.info("No rankings found for k = " + Integer.toString(k) + ". Stop classification for " + selectionMethod + ".");
                    break;
                }
                LOGGER.info(": Finished classification evaluation with models " +  Arrays.toString(classifiers) + " with k of " + k + " [" + datasetFile + "]");
            }

            //close all open file writers
            for (String metric : evalMetrics) {
                writers.get(metric).close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
