package de.hpi.bmg;

import weka.core.Instances;
import weka.core.converters.CSVLoader;

import java.io.File;
import java.io.IOException;

/**
 * Class for loading a data set from a file.
 * Used by classes WEKA_Evaluator and WEKA_FeatureSelector.
 */
public class DataLoader {


    String sourceFile;

    Instances data;

    /**
     * Constructor method.
     * Loads the data from the specified source file and stores it in the data class attribute.
     *
     * @param sourceFile absolute path of the input file from which to load the data.
     * @param separator  separator to use for file reading, e.g a comma.
     */
    public DataLoader(String sourceFile, String separator) {
        this.sourceFile = sourceFile;
        loadData(separator);
    }

    /**
     * Returns the loaded data set.
     *
     * @return the data set.
     */
    public Instances getData() {
        return data;
    }

    /**
     * Carries out the actual data loading.
     * Stores the loaded data set in the data class attribute.
     *
     * @param separator separator to use for file reading, e.g. a comma.
     */
    private void loadData(String separator) {

        CSVLoader loader = new CSVLoader();
        loader.setFieldSeparator(separator);
        try {
            loader.setSource(new File(this.sourceFile));
            this.data = loader.getDataSet();
        } catch (IOException e) {
            e.printStackTrace();
            // see https://opensource.apple.com/source/Libc/Libc-320/include/sysexits.h
            System.exit(66);
        }
    }

}
