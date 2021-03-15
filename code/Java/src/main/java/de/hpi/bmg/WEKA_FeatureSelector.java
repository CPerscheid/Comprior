package de.hpi.bmg;

import weka.core.Instances;

import java.util.ArrayList;
import java.util.List;

/**
 * Entry point class for running a feature selector on a data set.
 * Invoke the jar of this java file to carry out feature selection procedure (see an example in :class:`featureselection.InfoGainSelector` how to do that).
 */
public class WEKA_FeatureSelector {

    /**
     * Loads the input data set and creates selector objects based on the provided list of feature selector names.
     * Invokes feature selection procedures for all selectors and writes the results to the output directory, one file per selector.
     *
     * @param args the parameters provided when invoking the jar. Provide the following parameters:
     *             - absolute path to the input data set.
     *             - absolute path to the output directory (where to write the feature rankings).
     *             - a string of feature selectors, separated by a comma (e.g. "InfoGain,ReliefF").
     */
    public static void main(String[] args) {

        DataLoader dl = new DataLoader(args[0], ",");

        Instances data = dl.getData();

        //delete sample column
        data.deleteAttributeAt(0);
        //System.out.print(data);
        //set classLabel column to classIndex column
        data.setClassIndex(0);
        //System.out.print(data.classAttribute());

        List<String> attributeSelectionMethods = new ArrayList<String>();

        for (int i=2; i < args.length; i++) {
            attributeSelectionMethods.add(args[i]);
        }

        for (String asMethod : attributeSelectionMethods) {

            AttributeSelector as = new AttributeSelector(data, asMethod);

            as.selectAttributes();
            //System.out.print(asMethod);

            as.saveSelectedAttributes(args[1]);
        }

    }

}
