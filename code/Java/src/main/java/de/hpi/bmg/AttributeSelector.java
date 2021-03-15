package de.hpi.bmg;

import com.opencsv.CSVWriter;
import weka.attributeSelection.*;
import weka.core.Instances;

import java.io.*;
import java.util.logging.Logger;

/**
 * Selector class that carries out the actual feature selection procedure.
 * Invoked by
 */
public class AttributeSelector {

    private final static Logger LOGGER = Logger.getLogger(AttributeSelector.class.getName());

    private String selectionMethod;
    private Instances data;
    private AttributeSelection attributeSelection;

    /**
     * Constructor method.
     *
     * @param data the input data set from which to select the features.
     * @param selectionMethod name of the feature selector to apply.
     */
    public AttributeSelector(Instances data, String selectionMethod){

        this.data = data;
        this.selectionMethod = selectionMethod;

    }

    /**
     * Do the actual feature selection.
     * Based on the selector name, create corresponding instances of classes provided by WEKA and generate a feature ranking.
     */
    public void selectAttributes() {
        ASEvaluation eval;

        switch (this.selectionMethod) {
            case "SVMpRFE":
                //the default kernel for WEKAs SVMAttributeEval is a poly kernel (as defined in class SMO)
                eval = new SVMAttributeEval();

                ((SVMAttributeEval) eval).setPercentThreshold(10);

                ((SVMAttributeEval) eval).setPercentToEliminatePerIteration(10);

                break;

            case "GainRatio":

                eval = new GainRatioAttributeEval();

                break;

            case "ReliefF":

                eval = new ReliefFAttributeEval();

                break;

            default:

                eval = new InfoGainAttributeEval();

        }

        Ranker ranker = new Ranker();

        this.attributeSelection = new AttributeSelection();

        this.attributeSelection.setEvaluator(eval);
        this.attributeSelection.setSearch(ranker);

        // perform attribute selection

        long begin = System.currentTimeMillis();

        try {
            this.attributeSelection.SelectAttributes(data);
        } catch (Exception e) {
            e.printStackTrace();
        }

        long end = System.currentTimeMillis();

        long dt = end - begin;

        LOGGER.info("" + dt + "," + this.selectionMethod);
    }

    /**
     * Creates a feature ranking list and stores it in the specified file.
     *
     * @param saveLocation absolute path to the output file in which to store the ranking.
     */
    public void saveSelectedAttributes(String saveLocation) {

        try {


            CSVWriter writer = new CSVWriter(new FileWriter(saveLocation + "/" + this.selectionMethod + ".csv"), '\t');

            String[] header = {"attributeName","score"};

            writer.writeNext(header);

            double[][] rankedAttributes = this.attributeSelection.rankedAttributes();

            for (int i = 0; i < rankedAttributes.length; i++) {

                String attributeName = data.attribute((int) rankedAttributes[i][0]).name();

                String score = "" + rankedAttributes[i][1];

                String[] entry = {attributeName, score};

                writer.writeNext(entry);
            }

            writer.close();

        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}
