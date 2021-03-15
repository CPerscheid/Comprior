package de.hpi.bmg;

import weka.classifiers.Evaluation;
import weka.classifiers.trees.J48;
import weka.classifiers.bayes.NaiveBayes;
import weka.classifiers.functions.Logistic;
import weka.classifiers.functions.SMO;
import weka.classifiers.lazy.IBk;
import weka.classifiers.trees.RandomForest;
import weka.core.Instances;
import java.io.IOException;
import java.util.logging.Logger;
import weka.classifiers.AbstractClassifier;
import java.util.HashMap;

import java.util.Random;

/**
 * Carries out the actual k-fold cross validation on the specified classifiers.
 * Computes the desired evaluation metrics.
 * Uses WEKA.
 */
public class Analyzer {
    private Instances data;

    private final static Logger LOGGER = Logger.getLogger(Analyzer.class.getName());

    /**
     * Constructor method.
     *
     * @param data the data set to use for classification.
     * @return An instance of Analyzer.
     */
    public Analyzer(Instances data) {
        this.data = data;
    }

    /**
     * Runs the actual classification procedure.
     * Uses WEKA to run multiple classifiers (originally specified in config file) in a k-fold cross validation manner.
     * Computes standard evaluation metrics as required afterwards.
     *
     * @param numberOfAttributesRetained the data set to use for classification.
     * @param numFolds number of folds for cross validation.
     * @param classifiers a list of classifier objects to use for classification.
     * @param metrics a list of names of evaluation metrics to compute for the results.
     * @return the evaluation results as class:HashMap with the metric name as identifier and metric results (across classifiers and average) as values.
     */
    public  HashMap<String, String> trainAndEvaluateWithTopKAttributes(int numberOfAttributesRetained, int numFolds, AbstractClassifier[] classifiers, String[] metrics) {


        HashMap<String, String> returnStrings = new HashMap<String, String>();
        HashMap<String, Double> sums = new HashMap<String, Double>();
        Evaluation eval = null;

        //initialize maps for return strings and average computations
        for (String metric : metrics){
            String startString = Integer.toString(numberOfAttributesRetained);
            returnStrings.put(metric, startString);
            sums.put(metric, 0.0);
        }

        try {
            eval = new Evaluation(this.data);

            double sum = 0.0d;

            //AbstractClassifier analyzer = null;

            for (AbstractClassifier analyzer : classifiers){

                //run the analysis
                eval.crossValidateModel(analyzer, this.data, numFolds, new Random(1));
                for (String metric : metrics) {
                    String returnString = returnStrings.get(metric);
                    double metricVal = 0.0;
                    switch (metric) {
                        case "accuracy":
                            metricVal = eval.pctCorrect();
                            break;
                        case "kappa":
                            metricVal = eval.kappa();
                            break;
                        case "AUROC":
                            metricVal = eval.weightedAreaUnderROC();
                            break;
                        case "sensitivity":
                            metricVal = eval.weightedTruePositiveRate();
                            break;
                        case "specificity":
                            metricVal = eval.weightedTrueNegativeRate();
                            break;
                        case "F1":
                            metricVal = eval.weightedFMeasure();
                            break;
                        case "matthewcoef":
                            metricVal = eval.weightedMatthewsCorrelation();
                            break;
                        case "precision":
                            metricVal = eval.weightedPrecision();
                            break;
                    }
                    returnString += "\t" + String.valueOf(metricVal);
                    returnStrings.put(metric, returnString);
                    //update overall sum for average computation
                    sum = sums.get(metric);
                    sums.put(metric, sum + metricVal);
                }
            }

            for (String metric : metrics){
                String returnString = returnStrings.get(metric);
                returnString += "\t" + (sums.get(metric) / classifiers.length);
                returnStrings.put(metric, returnString);
            }

            //System.out.println(eval.toSummaryString(true));

        } catch (Exception e) {
            e.printStackTrace();
        }
        return returnStrings;
    }
}
