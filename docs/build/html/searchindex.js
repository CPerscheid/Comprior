Search.setIndex({docnames:["architecture","comprior","configparams","howtos","index","inputdata","installation","java-doc","outputstructure","r-doc"],envversion:55,filenames:["architecture.rst","comprior.rst","configparams.rst","howtos.rst","index.rst","inputdata.rst","installation.rst","java-doc.rst","outputstructure.rst","r-doc.rst"],objects:{"":{benchutils:[1,5,0,"-"],evaluation:[1,5,0,"-"],featureselection:[1,5,0,"-"],knowledgebases:[1,5,0,"-"],pipeline:[1,5,0,"-"],preprocessing:[1,5,0,"-"]},"de.hpi":{bmg:[7,0,1,""]},"de.hpi.bmg":{Analyzer:[7,1,1,""],AttributeSelector:[7,1,1,""],DataLoader:[7,1,1,""],WEKA_Evaluator:[7,1,1,""],WEKA_FeatureSelector:[7,1,1,""]},"de.hpi.bmg.Analyzer":{"Analyzer(Instances)":[7,2,1,""],"trainAndEvaluateWithTopKAttributes(int, int, AbstractClassifier[], String[])":[7,3,1,""]},"de.hpi.bmg.AttributeSelector":{"AttributeSelector(Instances, String)":[7,2,1,""],"saveSelectedAttributes(String)":[7,3,1,""],"selectAttributes()":[7,3,1,""]},"de.hpi.bmg.DataLoader":{"DataLoader(String, String)":[7,2,1,""],"getData()":[7,3,1,""],"loadData(String)":[7,3,1,""],data:[7,4,1,""],sourceFile:[7,4,1,""]},"de.hpi.bmg.WEKA_Evaluator":{"classifyAndEvaluate(String, String, String, int, int, int, String[], String[])":[7,3,1,""],"main(String[])":[7,3,1,""]},"de.hpi.bmg.WEKA_FeatureSelector":{"main(String[])":[7,3,1,""]},"evaluation.AnnotationEvaluator":{computeOverlap:[1,8,1,""],countAnnotationPercentages:[1,8,1,""],evaluate:[1,8,1,""],loadAnnotationFiles:[1,8,1,""]},"evaluation.AttributeRemover":{loadTopKRankings:[1,8,1,""],removeAttributesFromDataset:[1,8,1,""],removeUnusedAttributes:[1,8,1,""]},"evaluation.ClassificationEvaluator":{evaluate:[1,8,1,""]},"evaluation.CrossEvaluator":{evaluate:[1,8,1,""]},"evaluation.DatasetEvaluator":{evaluate:[1,8,1,""]},"evaluation.Evaluator":{computeKendallsW:[1,8,1,""],drawLinePlot:[1,8,1,""],evaluate:[1,8,1,""],loadRankings:[1,8,1,""]},"evaluation.KnowledgeBaseEvaluator":{checkCoverage:[1,8,1,""],checkPathwayCoverage:[1,8,1,""],createKnowledgeBases:[1,8,1,""],drawBarPlot:[1,8,1,""],drawBoxPlot:[1,8,1,""],evaluate:[1,8,1,""]},"evaluation.RankingsEvaluator":{computeFoldChangeDiffs:[1,8,1,""],computeKendallsWScores:[1,8,1,""],computePValue:[1,8,1,""],drawBoxPlot:[1,8,1,""],evaluate:[1,8,1,""],generateOverlaps:[1,8,1,""],loadGeneRanks:[1,8,1,""]},"featureselection.AnovaSelector":{runSelector:[1,8,1,""]},"featureselection.CORGSActivityMapper":{computeActivityScore:[1,8,1,""],computeActivityVector:[1,8,1,""],getANOVAscores:[1,8,1,""],mapFeatures:[1,8,1,""]},"featureselection.CombiningSelector":{getExternalGenes:[1,8,1,""],getName:[1,8,1,""],selectFeatures:[1,8,1,""]},"featureselection.ExtensionSelector":{selectFeatures:[1,8,1,""]},"featureselection.FeatureMapper":{getFeatures:[1,8,1,""],getLabels:[1,8,1,""],getPathwayGenes:[1,8,1,""],getSamples:[1,8,1,""],getUnlabeledData:[1,8,1,""],mapFeatures:[1,8,1,""]},"featureselection.FeatureSelector":{disableLogFlush:[1,8,1,""],enableLogFlush:[1,8,1,""],getData:[1,8,1,""],getFeatures:[1,8,1,""],getLabels:[1,8,1,""],getName:[1,8,1,""],getTimeLogs:[1,8,1,""],getUniqueLabels:[1,8,1,""],getUnlabeledData:[1,8,1,""],selectFeatures:[1,8,1,""],setParams:[1,8,1,""],setTimeLogs:[1,8,1,""],writeRankingToFile:[1,8,1,""]},"featureselection.FeatureSelectorFactory":{instance:[1,9,1,""]},"featureselection.InfoGainSelector":{createParams:[1,8,1,""]},"featureselection.JavaSelector":{createParams:[1,8,1,""],selectFeatures:[1,8,1,""]},"featureselection.KBweightedSelector":{combineRankings:[1,8,1,""],computeExternalRankings:[1,8,1,""],computeStatisticalRankings:[1,8,1,""],getName:[1,8,1,""],selectFeatures:[1,8,1,""],updateScores:[1,8,1,""]},"featureselection.KbSelector":{selectFeatures:[1,8,1,""],updateScores:[1,8,1,""]},"featureselection.LassoPenalty":{computeExternalRankings:[1,8,1,""],createParams:[1,8,1,""],getName:[1,8,1,""],selectFeatures:[1,8,1,""]},"featureselection.LassoSelector":{prepareOutput:[1,8,1,""],runSelector:[1,8,1,""]},"featureselection.MRMRSelector":{createParams:[1,8,1,""]},"featureselection.NetworkActivitySelector":{selectPathways:[1,8,1,""]},"featureselection.NetworkSelector":{getName:[1,8,1,""],selectFeatures:[1,8,1,""],selectPathways:[1,8,1,""],writeMappedFile:[1,8,1,""]},"featureselection.PathwayActivityMapper":{computeGeneVariances:[1,8,1,""],getAverageCorrelation:[1,8,1,""],mapFeatures:[1,8,1,""]},"featureselection.PostFilterSelector":{selectFeatures:[1,8,1,""]},"featureselection.PreFilterSelector":{selectFeatures:[1,8,1,""]},"featureselection.PriorKnowledgeSelector":{collectAlternativeSearchTerms:[1,8,1,""],getName:[1,8,1,""],getSearchTerms:[1,8,1,""],selectFeatures:[1,8,1,""]},"featureselection.PythonSelector":{prepareInput:[1,8,1,""],prepareOutput:[1,8,1,""],runSelector:[1,8,1,""],selectFeatures:[1,8,1,""]},"featureselection.RSelector":{createParams:[1,8,1,""],selectFeatures:[1,8,1,""]},"featureselection.RandomForestSelector":{prepareOutput:[1,8,1,""],runSelector:[1,8,1,""]},"featureselection.RandomSelector":{selectFeatures:[1,8,1,""]},"featureselection.ReliefFSelector":{createParams:[1,8,1,""]},"featureselection.SVMRFESelector":{createParams:[1,8,1,""]},"featureselection.Variance2Selector":{prepareOutput:[1,8,1,""],runSelector:[1,8,1,""]},"featureselection.VarianceSelector":{createParams:[1,8,1,""]},"featureselection.WrapperSelector":{createClassifier:[1,8,1,""],createSelector:[1,8,1,""],prepareOutput:[1,8,1,""],runSelector:[1,8,1,""]},"knowledgebases.BioMART":{getGeneScores:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""],mapItems:[1,8,1,""]},"knowledgebases.DISGENET":{getVersion:[1,8,1,""],query:[1,8,1,""]},"knowledgebases.Disgenet":{getGeneScores:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""]},"knowledgebases.ENRICHR":{"export":[1,8,1,""],addlist:[1,8,1,""],genemap:[1,8,1,""]},"knowledgebases.Enrichr":{annotateGene:[1,8,1,""],annotateGenes:[1,8,1,""],downloadEnrichedTerms:[1,8,1,""],enrichGeneset:[1,8,1,""],getGeneScores:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""]},"knowledgebases.GCONVERT":{query:[1,8,1,""]},"knowledgebases.Gconvert":{getGeneScores:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""],mapItems:[1,8,1,""]},"knowledgebases.KEGGPathwayParser":{parsePathway:[1,8,1,""],readInteractions:[1,8,1,""]},"knowledgebases.Kegg":{getGeneScores:[1,8,1,""],getPathwayNames:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""]},"knowledgebases.KnowledgeBase":{getGeneScores:[1,8,1,""],getName:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""],hasGenes:[1,8,1,""],hasPathways:[1,8,1,""]},"knowledgebases.KnowledgeBaseFactory":{instance:[1,9,1,""]},"knowledgebases.OpenTargets":{getAssociations:[1,8,1,""],getGeneScores:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""]},"knowledgebases.PATHWAYCOMMONSWS":{default_extension:[1,9,1,""],get:[1,8,1,""],getVersion:[1,8,1,""],search:[1,8,1,""]},"knowledgebases.PathwayParser":{parsePathway:[1,8,1,""]},"knowledgebases.Pathwaycommons":{getGeneScores:[1,8,1,""],getRelevantGenes:[1,8,1,""],getRelevantPathways:[1,8,1,""],readPathway:[1,8,1,""]},"knowledgebases.UMLS":{getCUIs:[1,8,1,""]},"knowledgebases.UMLS_AUTH":{instance:[1,9,1,""]},"pipeline.Pipeline":{assignColors:[1,8,1,""],evaluateBiomarkers:[1,8,1,""],evaluateInputData:[1,8,1,""],evaluateKnowledgeBases:[1,8,1,""],executePipeline:[1,8,1,""],loadConfig:[1,8,1,""],prepareDirectories:[1,8,1,""],prepareExecution:[1,8,1,""],preprocessData:[1,8,1,""],runFeatureSelector:[1,8,1,""],selectFeatures:[1,8,1,""]},"preprocessing.DataMovePreprocessor":{preprocess:[1,8,1,""]},"preprocessing.DataTransformationPreprocessor":{preprocess:[1,8,1,""]},"preprocessing.FilterPreprocessor":{filterMissings:[1,8,1,""],preprocess:[1,8,1,""]},"preprocessing.MappingPreprocessor":{preprocess:[1,8,1,""]},"preprocessing.MetaDataPreprocessor":{preprocess:[1,8,1,""]},"preprocessing.Preprocessor":{preprocess:[1,8,1,""]},DataCharacteristicsPlotting:{R:[9,10,1,"-"]},FS_LassoPenalty:{R:[9,10,1,"-"]},FS_Variance:{R:[9,10,1,"-"]},FS_mRMR:{R:[9,10,1,"-"]},IdentifierMapping:{R:[9,10,1,"-"]},UpsetDiagramCreation:{R:[9,10,1,"-"]},benchutils:{cleanupResults:[1,6,1,""],createDirectory:[1,6,1,""],createLog:[1,6,1,""],createOrClearDirectory:[1,6,1,""],flushLog:[1,6,1,""],getConfig:[1,6,1,""],getConfigBoolean:[1,6,1,""],getConfigValue:[1,6,1,""],loadConfig:[1,6,1,""],loadRanking:[1,6,1,""],log:[1,6,1,""],mapDataMatrix:[1,6,1,""],mapGeneList:[1,6,1,""],mapIdentifiers:[1,6,1,""],mapRanking:[1,6,1,""],removeDirectoryContent:[1,6,1,""],removeFile:[1,6,1,""],retrieveMappings:[1,6,1,""],runJavaCommand:[1,6,1,""],runRCommand:[1,6,1,""]},evaluation:{AnnotationEvaluator:[1,7,1,""],AttributeRemover:[1,7,1,""],ClassificationEvaluator:[1,7,1,""],CrossEvaluator:[1,7,1,""],DatasetEvaluator:[1,7,1,""],Evaluator:[1,7,1,""],KnowledgeBaseEvaluator:[1,7,1,""],RankingsEvaluator:[1,7,1,""]},featureselection:{AnovaSelector:[1,7,1,""],CORGSActivityMapper:[1,7,1,""],CombiningSelector:[1,7,1,""],ExtensionSelector:[1,7,1,""],FeatureMapper:[1,7,1,""],FeatureSelector:[1,7,1,""],FeatureSelectorFactory:[1,7,1,""],InfoGainSelector:[1,7,1,""],JavaSelector:[1,7,1,""],KBweightedSelector:[1,7,1,""],KbSelector:[1,7,1,""],LassoPenalty:[1,7,1,""],LassoSelector:[1,7,1,""],MRMRSelector:[1,7,1,""],NetworkActivitySelector:[1,7,1,""],NetworkSelector:[1,7,1,""],PathwayActivityMapper:[1,7,1,""],PostFilterSelector:[1,7,1,""],PreFilterSelector:[1,7,1,""],PriorKnowledgeSelector:[1,7,1,""],PythonSelector:[1,7,1,""],RSelector:[1,7,1,""],RandomForestSelector:[1,7,1,""],RandomSelector:[1,7,1,""],ReliefFSelector:[1,7,1,""],SVMRFESelector:[1,7,1,""],Variance2Selector:[1,7,1,""],VarianceSelector:[1,7,1,""],WrapperSelector:[1,7,1,""]},knowledgebases:{BioMART:[1,7,1,""],DISGENET:[1,7,1,""],Disgenet:[1,7,1,""],ENRICHR:[1,7,1,""],Enrichr:[1,7,1,""],GCONVERT:[1,7,1,""],Gconvert:[1,7,1,""],KEGGPathwayParser:[1,7,1,""],Kegg:[1,7,1,""],KnowledgeBase:[1,7,1,""],KnowledgeBaseFactory:[1,7,1,""],OpenTargets:[1,7,1,""],PATHWAYCOMMONSWS:[1,7,1,""],PathwayParser:[1,7,1,""],Pathwaycommons:[1,7,1,""],UMLS:[1,7,1,""],UMLS_AUTH:[1,7,1,""]},pipeline:{Pipeline:[1,7,1,""]},preprocessing:{DataMovePreprocessor:[1,7,1,""],DataTransformationPreprocessor:[1,7,1,""],FilterPreprocessor:[1,7,1,""],MappingPreprocessor:[1,7,1,""],MetaDataPreprocessor:[1,7,1,""],Preprocessor:[1,7,1,""]}},objnames:{"0":["java","package","Java package"],"1":["java","type","Java type"],"10":["rst","directive","reStructuredText directive"],"2":["java","constructor","Java constructor"],"3":["java","method","Java method"],"4":["java","field","Java field"],"5":["py","module","Python module"],"6":["py","function","Python function"],"7":["py","class","Python class"],"8":["py","method","Python method"],"9":["py","attribute","Python attribute"]},objtypes:{"0":"java:package","1":"java:type","10":"rst:directive","2":"java:constructor","3":"java:method","4":"java:field","5":"py:module","6":"py:function","7":"py:class","8":"py:method","9":"py:attribute"},terms:{"00lock":6,"00new":6,"abstract":[0,1,3],"boolean":[1,3,9],"break":7,"case":[1,7],"catch":7,"class":[1,2,4,5,7,9],"default":[1,2,3,6,7,9],"export":[1,6],"final":[1,2,7,9],"float":1,"function":[0,1,2,4,6,7,9],"import":[1,7],"int":[1,2,7],"long":7,"new":[1,2,4,7],"null":[7,9],"public":7,"return":[1,3,7,9],"short":1,"static":7,"super":[1,3],"switch":7,"true":[1,2,3,7,9],"try":[6,7,8,9],"var":6,"void":7,"while":[1,6],AND:1,For:[1,6,7,9],IDs:[1,2,9],MDS:[1,9],NOS:5,One:3,SFS:[1,2],Such:3,The:[0,1,3,5,6,7,9],Then:1,There:[1,6],These:[1,3],Tos:4,Use:1,Used:[1,7],Uses:[1,7,9],Using:6,Will:1,With:1,__init__:3,_valid_format:1,abl:1,about:1,abov:[1,2,3,6],absolut:[1,3,7,9],abstractclassifi:7,access:[1,2,4,6],accidenti:1,accord:1,accordingli:[1,5],accuraci:[2,7],achiev:3,across:[1,7,9],activ:[1,2,8],actual:[0,1,2,3,7,8],adapt:[1,3,6,8,9],add:[1,2,4,6,7,8,9],addal:7,added:[1,8],adding:[3,6],addit:[1,3],addition:[1,3],addlist:1,advis:1,aes:9,affy_hg_u133_plus_2:2,afterward:[1,7],again:1,aggreg:1,algorithm:2,all:[0,1,2,3,6,7,8,9],allow:1,alreadi:[1,2,3,6,8],also:[1,2,6,8],altern:[1,2],alternativesearchterm:[1,2],although:[1,9],altough:1,alwai:[1,3,5,6],amd64:6,among:1,analys:[1,3],analysi:[1,2,7],analyz:[1,7,8],ani:[1,2,3,6],annot:[1,2,8],annotategen:1,annotation_overlap:2,annotation_percentag:2,annotationevalu:[1,9],annotationsdir:2,annotationspercentag:1,anoth:[1,4],anova:[1,2],anovaselector:1,anymor:[1,3],apach:[6,7],api:[1,2,3],apikei:2,appl:7,appli:[1,2,6,7],applic:1,approach:[1,2,4,7,8,9],apt:6,arbitrarili:5,architectur:[1,4],archiv:6,arg:[3,7,9],argument:9,arrai:[1,7],arraylist:7,arrayutil:7,asevalu:7,asmethod:7,aspect:1,assess:1,assign:1,assigncolor:1,associ:[1,2,3],associationscor:2,assocscor:1,attent:5,attribut:[1,7,9],attributenam:[7,9],attributeremov:1,attributeselect:7,attributeselectionmethod:7,attributeselector:7,auroc:[2,7],auth:1,auth_endpoint:2,authent:[1,2],automat:[1,2],avail:[1,2,3,6],averag:[1,2,7],average_foldchang:2,avoid:1,axi:1,backend:6,backgroundtyp:1,bar:[1,9],base:[0,1,2,4,5,6,7,8,9],baselin:1,basenam:9,bash:6,bay:[2,7],becaus:[1,6,9],becom:1,been:1,befor:[1,2,6],begin:[6,7,9],below:[0,3],benchmark:1,benchutil:[3,4],between:2,biit:[1,2],bin:6,binari:6,binary_sif:1,bioinformat:9,biolog:1,biomart:[1,4,9],biomed:1,biopax:1,bioservic:[0,1,3],blank:5,block:[1,9],bmg:7,bool:1,both:[1,6],box:[1,2,9],boxpl:9,boxplot:9,brca1:5,brca2:5,brca:5,breast:2,brew:6,brief:2,btaa776:9,build:[1,8],call:[3,9],can:[1,2,3,5,6,9],cancer:2,cannot:6,carcinoma:5,care:1,carri:[1,7],categor:1,categori:1,cbind:9,cca:1,cento:6,cflag:6,chang:[1,2,6],charact:1,characterist:[8,9],check:[1,3,6,9],checkcoverag:1,checkpathwaycoverag:1,child:1,choos:2,chosen:5,chuang:1,chunk:9,chunksiz:9,classattribut:7,classic:9,classif:[1,4,7,8],classifi:[1,2,7],classificationconfig:1,classificationevalu:[1,7],classifiernam:7,classifierobject:7,classifierparam:7,classifyandevalu:7,classindex:7,classlabel:[7,9],classlabelnam:[2,5],classsif:2,clean:1,cleanupresult:1,clear:1,clone:6,close:7,cloud:[1,2],cmd:6,cmdscale:9,code:[2,4,6],coef:9,coeffici:[1,2],colindex:1,collectalternativesearchterm:1,colnam:9,color:[1,9],colorcount:9,colorstr:9,column:[1,2,5,7,9],com:[1,6,7],combin:[1,2,3,9],combinerank:1,combining_method:2,combiningselector:1,come:[3,6],comma:7,command:[1,3,6,7,9],commandarg:9,comment:[1,3],common:7,compar:[1,2,8],comparison:[1,2],compil:[3,6],complet:[1,6],complex:1,compon:[1,4],composit:1,comprior:[1,2,3,6,8],comput:[1,7,9],computeactivityscor:1,computeactivityvector:1,computeexternalrank:1,computefoldchangediff:1,computegenevari:1,computekendallsw:1,computekendallswscor:1,computeoverlap:1,computepvalu:1,computestatisticalrank:1,concret:[0,9],conduct:1,config:[1,2,4,5,6,7,8,9],configur:[1,4,6],connect:[6,9],consist:[1,9],construct:[1,2,3],constructor:7,contain:[0,1,2,3,6,7,8,9],content:[4,7],continu:7,control:1,convers:1,convert:[1,2,7],coordin:1,core:[2,7],corg:1,corgsactivitymapp:1,corgsnetworkactivity_kb:2,correct:[1,3,6],correctli:[1,6],correl:[1,2],correspond:[0,1,3,5,7,9],correspondingli:1,could:[1,3],count:1,countannotationpercentag:1,coupl:1,cover:1,coverag:[1,2,8],cperscheid:6,cpp:[3,6],cppconfig:3,cpplocat:3,cran:1,creat:[1,2,3,7,9],createclassifi:1,createcombinedselector:3,createdirectori:1,createintegrativeselector:3,createknowledgebas:[1,3],createlog:1,createorcleardirectori:1,createparam:1,createselector:1,createtraditionalselector:3,creation:1,cross:[1,2,4,7,8],crossclassif:1,crossevalu:[1,8],crossevaluationclasslabel:[2,5],crossevaluationdata:2,crossevaluationdir:2,crossevaluationgeneidformat:2,crossval_preprocess:2,crossvalid:8,crossvalidatemodel:7,csv:[1,3,7,8,9],csvloader:7,csvwriter:7,csw:6,cui:1,curl:6,current:[1,2,3,5,6,8,9],currentformat:1,currentgeneidformat:2,currentidformat:3,currenttimemilli:7,custom:[1,4,6],cwd:3,cxx:6,d_fortify_sourc:6,data:[1,2,3,4,6,7,8,9],databas:1,datacharacteristicsplot:9,dataconfig:1,datadir:1,dataformatt:3,datafram:[1,3,9],dataload:7,datamovepreprocessor:1,datasepar:[1,2,5],dataset:[1,4,5,8,9],datasetevalu:[1,9],datasetfil:7,datasetloc:1,datasourc:1,datast:1,datatransformationpreprocessor:[1,3],dbinfo:1,dbmi:1,deb:6,debian:6,declar:1,decreas:[1,9],def:3,default_escape_charact:7,default_extens:1,default_line_end:7,defin:[1,3,7,9],degre:1,delet:[1,7],deleteattributeat:7,delimit:1,deliv:1,demand:1,densiti:[1,2,9],density_:9,depend:[1,3,6,7],descend:[1,3,9],describ:[0,1,2,3,6],descript:1,design:6,desir:[1,2,7,9],desiredformat:1,desiredidformat:3,desper:9,detail:1,detect:9,dev:[6,9],devel:6,diagram:[1,2,4,9],dict:[1,3],dictionari:1,did:9,differ:[1,3,6,8,9],diffus:1,dimension:9,dir:9,directli:1,directori:[1,2,3,6,7,9],directoryloc:1,dis:2,disabl:1,disablelogflush:1,discov:1,diseas:[1,2,3,5],diseasecod:5,diseasecolumn:1,diseaselabelnam:5,disgenet:[1,4],disjunct:1,dist:9,distanc:9,distinct:[1,9],distribut:[2,6,9],distribution_:9,divid:1,dllpath:6,dndebug:6,document:3,doe:[1,3],doi:9,domain:1,done:1,doubl:7,download:[1,6],downloaded_packag:6,downloadenrichedterm:1,dplyr:9,draw:1,drawbarplot:1,drawboxplot:1,drawlineplot:1,driven:1,drop:9,duchar_typ:6,duct:5,durat:[1,8],dure:[1,2,7,8],dvl1:5,dyn:6,dynam:1,each:[1,3,7,9],echo:6,ecnumb:1,effici:1,either:[1,3,5,6],element:[1,9],elimin:1,eliminatin:1,els:[7,9],embed:2,empti:[5,9],enabl:[1,6,9],enableclassif:2,enablecrossevalu:2,enablelogflush:1,enablepredict:2,encapsul:[0,1,3],encod:[1,6],end:[1,7,9],endpoint:[1,2,3],enrich:[1,2,8],enrichgeneset:1,enrichment_overlap:2,enrichr:[1,4],ensembl:[1,9],ensembl_gene_id:9,ensembl_mart_ensembl:9,ensg:2,entiti:1,entrezgen:2,entri:[1,7],environ:6,equal:1,equip:1,erbb2:5,errno:6,error:[1,6],especi:1,etc:[1,6],euclidean:9,eval:7,evalconfig:1,evalmetr:7,evalu:[4,8,9],evaluatebiomark:1,evaluateinputdata:1,evaluatekbcoverag:[2,8],evaluateknowledgebas:1,event:1,everi:[0,1,2,3,7,8,9],exampl:[1,3,5,6,7,8],exampleconfig:6,exampled_input:3,examplefeaturemapp:3,examplekb:3,examplekbw:3,examplenetworkselector:3,examplepathwaykb:3,examplepathwaypars:3,examplepreprocessor:3,exampleselector:3,except:[1,5,7],exchang:1,exclus:1,execut:[1,4,6],executepipelin:1,exist:[1,2,3,8],exit:[6,7],expect:[1,3,6],explan:2,express:[1,2,4,9],expressionlevel:1,extend:[1,2,3],extens:1,extension_trad_kb:2,extensionselector:1,extern:[0,1,2,3,8,9],externalkbdir:[2,3],externalknowledg:8,externalrank:1,externalscores_filenam:3,extract:1,factor:9,factori:1,fail:6,fals:[1,2,3,9],fau:6,favor:1,featur:[0,1,2,4,5,6,8],feature_count:9,featurelist:1,featuremapp:[1,3],featurenam:9,features_:7,featureselect:[3,4,7,9],featureselector:[0,1,3],featureselectorfactori:[1,4],fedora:6,femal:5,fetch:9,few:1,fewer:9,field:[1,2],file:[1,2,4,5,6,7,9],file_path_sans_ext:9,fileend:9,filenam:[1,3,9],filenotfounderror:6,fileoutput:9,filepath:7,fileprefix:1,filesuffix:1,filewrit:7,filter:[1,2,9],filtermiss:1,filtermissingsingen:2,filtermissingsinsampl:2,filterpreprocessor:1,final_filenam:1,final_map:9,finalgeneidformat:2,find:[1,3,4,6,9],finish:7,first:[1,2,3,5],fleiss:2,fleiss_kappa:2,flexibl:6,flush:[1,7],flushlog:1,focu:1,fold:[1,2,7],folder:[1,3,4,6,7],follow:[1,2,3,6,7,8],fommil:6,forest:2,forget:3,form:1,format:[1,2,3,5,6,9],former:1,fortran:6,forward:[1,2,3],found:[1,2,3,6,7],fpic:6,frame:[1,9],framework:[1,2,6],freq:9,frmt:1,from:[0,1,2,4,6,7,8,9],fromlist:9,fs_lassopenalti:[3,9],fs_mrmr:9,fs_varianc:9,fstack:6,ftp:6,full:1,further:[1,5],fvisibl:6,gainratio:7,gainratioattributeev:7,gather:9,gcc:6,gconvert:[1,4],gender:5,gene:[1,3,4,9],gene_dpi:2,gene_dsi:2,genechunk:9,geneexpressionmatrix:9,genefilt:[1,9],geneid:1,geneinfo:[1,3],genelist:1,genemap:1,gener:[1,3,4,7],generank:8,generateoverlap:1,genescor:3,genesetlibrari:2,genesincolumn:[1,2,5],geom_boxplot:9,geom_dens:9,geom_point:9,get:[1,3,6,7,9],getabsolutepath:7,getanovascor:1,getassoci:1,getaveragecorrel:1,getbm:9,getconfig:[1,3],getconfigboolean:1,getconfigvalu:1,getcui:1,getdata:[1,7],getdataset:7,getexternalgen:1,getfeatur:1,getgenescor:[1,3],getlabel:1,getlength:7,getlogg:7,getnam:[1,3,7],getpathwaygen:1,getpathwaynam:1,getrelevantgen:[1,3],getrelevantpathwai:[1,3],getsampl:1,getsearchterm:1,gettimelog:1,getuniquelabel:1,getunlabeleddata:1,getvers:[1,3],gfortran_1:6,ggplot2:9,ggplot:9,git:6,github:[1,6],give:9,given:[1,3,9],glmnet:6,global:6,gnu:6,good:9,gov:1,gprofil:[1,2],grab:6,grant:1,graph:1,gregexpr:9,grei:0,group:2,had:[3,6],handl:[1,3],happen:[1,6],has:1,hasgen:1,hasgeneinform:1,hashmap:7,haspathwai:1,haspathwayinform:1,have:[1,2,3,5,6,9],head:9,header:[5,7,9],headerstart:7,headlin:1,healthi:6,help:[1,6,9],here:[0,1,3,5,6,8,9],hex:1,hgnc:2,hgnc_symbol:9,hidden:6,hierarchi:3,high:9,higher:2,highli:[1,9],hit:1,hms:1,homepath:[2,3,6],homo:1,hour:1,how:[1,4,6,7],howev:[1,3,5,9],hpi:7,hsapiens_gene_ensembl:9,html:[1,3],http:[1,2,3,6,7,9],http_get:3,httr:9,hub:1,human:1,ibk:7,identifi:[1,3,5,7,8,9],identifiermap:9,ids:[1,9],imag:0,implement:[0,1,4,6,9],importerror:6,improv:9,includ:[1,2,4,6,7,9],include_dir:6,incorpor:[2,9],increas:7,index:[1,4,9],indic:[2,3],individu:[1,9],infer:[1,2],infiltr:5,info:[1,3,7],infogain:[1,2,7],infogainattributeev:7,infogainselector:[1,7],inform:[1,2,3,5,6],informat:1,infrastructur:8,inherit:[0,1,3],ini:[1,3,6,8],init:3,initi:7,input:[1,2,3,4,6,7,9],input_filenam:3,input_metadata:3,inputdir:[1,2],inputfil:[1,9],inputmatrix:1,inputpath:[1,9],insid:1,inspect:1,inspir:1,inst:6,instal:4,install_maco:6,installout:6,instanc:[1,3,7],instead:[1,3,6],integ:[7,9],integr:3,intend:[1,3],interact:[0,1],intercept:9,interest:[1,9],interfac:[0,1,3],intermedi:[1,2,3,4],intermediate_output:3,intermediatedir:[1,2],intern:[1,3,6],interpret:[3,6],intersect:1,introduc:9,invoc:1,invok:[1,4,7,9],ioexcept:7,isfil:7,issu:[6,9],item:1,itemlist:1,itendifi:1,its:[0,1,3,6,7,9],itsfoss:6,j48:7,jai:9,jar:[1,2,3,7],java:[1,4],java_hom:6,javaconfig:1,javaloc:[2,6],javaselector:[1,3],jdk:4,jean:1,jointli:2,journal:1,jre:6,json:[1,3],just:[1,3,6,9],jvm:6,kanehisa:1,kappa:[2,7],kb_config:1,kb_score:1,kbfactori:3,kbonly_kb:2,kbselector:1,kbweightedselector:1,keep:[1,9],keepord:1,kegg:[1,4],keggpathwaypars:[1,3],kei:[1,2,3,9],kendal:[1,2],kendall_w:2,kernel:[1,2,7],keyset:7,keyword:[1,2],kfold:2,kgml:1,kgml_pathwai:1,kidnei:2,kidney_canc:2,kind:1,knn3:[2,7],knn5:[2,7],knn:2,knoweldg:1,knowledg:[0,1,2,4,5,6,8,9],knowledgebas:[4,9],knowledgebaseevalu:1,knowledgebasefactori:[1,4],knowledgebaselist:1,lab:9,label:[1,2,3,5,9],labelcol:9,labeleddata:9,labeledinputdatapath:1,lang3:7,lang:7,languag:4,larg:1,lasso:[1,2,9],lassopenalti:1,lassopenalty_kb:2,lassopenalty_kegg:1,lassopenaltyselector:9,lassoselector:1,last:1,last_genechunk:9,later:1,lazi:7,ldl:6,lead:1,learn:1,leav:5,lee:[1,2],leftov:9,length:[1,7,9],let:6,level:[1,9],lib:6,lib_dir:6,libc:7,libcurl4:6,libcurl:6,libgfortran:6,librari:[1,2,6,9],libssl:6,libssl_dev:6,libxml2:6,libxml2_dev:6,libxml:6,licudata:6,licui18n:6,licuuc:6,lies:1,like:[1,3,6,9],limma:9,line:[1,3,6,7,9],linear:2,link:[1,6],linux:6,list:[1,3,7,9],listfil:7,listofdir:7,lixml:6,llzma:6,load:[1,6,7,9],loadannotationfil:1,loadconfig:1,loaddata:7,loader:7,loadgenerank:1,loadrank:1,loadtopkrank:1,lobular:5,local:6,localpoint:6,localpointerbas:6,locat:[1,2,3,5,6,7],log:[1,2,7,8],logger:7,loggingdir:1,login:[1,2],login_uri:2,loginservice_uri:2,logist:7,look:[1,6],lowli:1,lucen:1,luma:5,lumb:5,lxml2:6,maayanlab:[1,2],mac:6,machin:[2,6],maco:6,main:[6,7],mainli:2,make:[1,2,3,5,6,9],makevar:6,mani:[1,3,7],manner:[3,7],manual:6,map:[1,3,5,7,8,9],mapdatamatrix:1,mapfeatur:[1,3],mapgenelist:1,mapidentifi:1,mapitem:1,mapped_data:1,mapped_input:[1,3],mappeddataset:3,mapper:[1,3],mappingpreprocessor:[1,3],maprank:1,mark:0,mart:9,master:[3,6],match:1,matplotlib:1,matrix:[1,9],matthew:2,matthewcoef:[2,7],maven:4,maxfeatur:[1,9],maxim:1,maximum:[1,2,7,9],maxnumpathwai:2,maxrank:1,mayb:1,md5:6,mds:[1,2,9],mds_:9,mdspl:9,mean:1,measur:1,median:1,member:1,merg:[1,9],messag:[1,6],meta:1,metadata:[1,2,4,8],metadataidsincolumn:[2,5],metadatapreprocessor:1,method:[0,1,3,4,7,9],methodcolor:1,methoddir:7,metric:[1,2,7,8],metricparam:7,metricsdir:2,metricv:7,mice:1,microarrai:1,might:[1,6],minim:1,minimum:[1,2,7],minoru:1,miriam:1,mirror:9,miss:[1,2],mlxtend:1,model:[7,9],modifying_method:2,modul:[0,4,7],more:9,most:9,move:1,mrmr:[1,2,9],mrmre:[1,9],mrmrselector:[1,9],much:1,multidimension:2,multipl:[1,2,3,7],must:[0,1,2,3,5],myenvvar:6,myexamplekbwebservic:3,naiv:2,naivebay:7,name:[1,2,3,5,6,7,8,9],namespac:6,nativ:6,navig:6,ncbi:1,ncol:9,nearest:2,nearli:1,necessari:[1,9],need:[1,3,4,6],neighbor:[1,2],netlib:6,network:[1,2,4],network_method:2,networkactivity_kb:2,networkactivityselector:1,networkselector:[1,3],newgenescor:1,newtimelog:1,next:3,nih:1,nio:7,nip:1,nlm:1,no_quote_charact:7,non:6,none:[1,3,6],normal:1,notavail:1,note:1,noth:7,notimplementederror:[1,3],now:1,nrow:9,nset:9,number:[1,2,7,8,9],numberofattributesretain:7,numcor:[1,2],numer:[1,9],numfold:7,numpi:1,numrow:9,object:[1,3,6,7],obtain:1,ofattribut:7,off:9,offer:1,offici:1,old:1,older:1,onc:[1,3],one:[1,3,7,8,9],onefil:9,ones:[1,9],onli:[1,2,3,6,7,9],onlin:0,ontolog:1,open:7,opencsv:7,openjdk:6,opensourc:7,openssl:6,opentarget:[1,4],opentargetscli:1,optim:3,option:[1,4,6,9],orchestr:1,order:[1,3,6,9],orderednamelist:9,orderednamevaluelist:9,orderednamevaluematrix:9,org:[1,3,7,9],organ:1,origin:[1,3,7,9],original_data:[1,3],originalformat:1,originalidformat:9,osx:6,other:[0,1,3,6],otherwis:[1,9],our:3,out:[1,6,7,8,9],outdat:1,output:[1,2,3,4,6,7,9],output_filenam:3,outputdata:9,outputdir:[1,2,3],outputdir_nam:[2,8],outputdirectori:2,outputfil:[1,9],outputfilenam:3,outputfilepath:1,outputloc:9,outputpath:1,outputrootpath:1,overal:[1,2,3,7,9],overlap:[1,2,9],overrid:1,overview:6,overwrit:[1,6],overwritten:8,own:[0,1,2,3,6],owner:1,packag:[1,3,6,7,9],page:[1,4],pai:5,panda:[1,3],papachristoudi:1,parallel:[1,2,9],param:[1,2,3,7,9],paramet:[1,3,4,5,6,7,8,9],pars:[1,2,3,9],parseint:7,parsepathwai:[1,3],parser:[4,6],part:[1,3,9],particip:1,particular:[1,7],pass:3,past:9,paste0:9,path:[1,2,3,6,7,8,9],pathwai:[1,2,4,8],pathwayactivitymapp:1,pathwaycommon:[1,4],pathwaycommonsw:1,pathwayid:[1,3],pathwayinfo:[1,3],pathwaymapp:1,pathwaypars:[1,3],pathwayrank:3,pattern:9,pctcorrect:7,pdf:[8,9],pearson:2,penalti:[1,2,9],per:[1,2,7,8,9],percentag:[1,2],percentil:1,perform:[1,2,7,9],perhap:6,perman:6,permut:1,phase:1,philipp:1,physic:1,pid:1,pip3:6,pipelin:[4,6],pkg:6,pkg_cflag:6,pkg_config_path:6,pkg_lib:6,pl2:9,place:3,plaintext:1,platform:9,pleas:[1,9],pleiotropi:2,plot:[1,2,8,9],point:[0,1,6,7],poli:[1,7],polykernel:2,popen:3,possibl:1,postfilt:1,postfilter_trad_kb:2,postfilterselector:1,postprocess:1,potenti:1,preanalysi:[1,2,8],preanalysis_plot:[2,8],preced:3,precis:[1,2,7],predict:[4,8,9],predictor:2,prefer:3,prefilt:1,prefilter_trad_kb:2,prefilterselector:1,prefix:[1,2],prepar:1,preparedirectori:1,prepareexecut:1,prepareinput:1,prepareoutput:1,preprocess:[4,5,8],preprocessdata:[1,3],preprocessor:[0,1,4],prerequisit:6,primary_diagnosi:5,print:[3,6,7,9],println:7,printstacktrac:7,prior:[1,2,3,6,9],priorknowledgeselector:[1,3],privat:7,probabl:9,problem:6,procedur:[1,3,7],process:[1,3,7,8],produc:1,profil:[1,6],program:[1,4],project:1,project_id:5,properli:[2,6],properti:1,protector:6,proven:1,provid:[1,2,3,5,6,7],ptr:6,purpos:1,put:[1,2,7,8],pycurl:6,pypath:[1,3],python3:6,python:[2,3,4,6,9],pythonselector:1,q06609:1,q549z0:1,qualiti:1,queri:[1,2,3,8,9],rais:3,ran:1,random:[1,2,7],randomforest:[1,2,7],randomforestclassifi:1,randomforestselector:1,randomli:1,randomselector:1,rang:1,rank:[1,3,4,7,8,9],rankedattribut:7,ranker1:1,ranker:[1,7],rankingfil:1,rankingsdir:1,rankingsevalu:[1,9],rather:[1,6],rawdata:9,rbind:9,rconfig:[1,3],rdf:1,reachabl:9,reactom:1,read:[1,7,9],readi:1,readinteract:1,readpathwai:1,readthedoc:3,realiz:1,reason:2,receiv:1,recogn:1,recommend:[2,6],record:1,recurs:1,reduc:[1,2,7],reduceddata:8,reduceddataset:2,reduceddatasetloc:7,redund:1,refarpack:6,refbla:6,refer:3,referenec:1,reflapack:6,reflect:7,regard:1,regist:[1,4],regress:[2,9],regular:[2,9],reinstal:6,relat:[0,1,3,6],relationship:1,relev:1,relieff:[1,2,7],relieffattributeev:7,relieffselector:1,remain:1,remov:[1,6,9],removeattributesfromdataset:1,removedirectorycont:1,removefil:1,removeunusedattribut:1,renam:9,repeatedli:1,replac:2,repositori:6,repres:1,represent:1,request:[1,3],requir:[1,3,6,7],requiredidformat:9,respect:[2,3],respons:1,rest:[0,1,3],restrict:1,result:[1,2,3,4,6,7,9],resultlin:7,resultloc:7,resultsdir:2,ret:3,retain:9,retriev:[0,1,2,3,8],retrievemap:1,retriv:1,returnstr:7,review:1,rfe:[1,2],rhel:6,right:[1,6,8],robustnessresult:2,root:6,round:7,row:[5,9],rownam:9,rownamescol:9,rowvar:9,rpm:6,rscript:[1,2,6],rscriptloc:[2,6],rselector:[1,3],rtmpashma8:6,rtype:3,run:[1,2,3,6,7,8,9],runcppcommand:3,runfeatureselector:1,runjavacommand:[1,3],runrcommand:[1,3],runselector:1,runtim:[1,2],same:[1,2,3,5],sampl:[1,2,5,7,9],sample1:5,sample2:5,sampleexpressionlevel:1,samplenam:5,sapien:1,save:1,saveloc:7,saveselectedattribut:7,scale:2,schema:3,scheme:1,scikit:1,score:[1,2,3,7,9],script:[1,3,6],scriptnam:1,search:[1,2,3,4,5],searchabl:1,searchterm:1,second:[1,2,3,8],section:[2,3],secur:6,see:[0,1,2,3,6,7],seem:[6,9],segment:3,selec:1,select:[0,1,4,5,8],selectattribut:7,selectfeatur:[0,1,3],selectionmethod:7,selectkgen:2,selector:[0,1,2,4,6,7],selectornam:3,selectpathwai:[1,3],self:[1,3],send:[1,3,9],sens:1,sensit:[1,2,7],sent:1,sep:[2,3,9],separ:[1,2,3,5,7,9],sequenti:1,seri:1,serv:9,server:9,servic:[0,1,2,4,6],set:[1,2,3,4,6,7,8,9],set_config:9,setclassindex:7,setcount:9,setevalu:7,setfieldsepar:7,setknn:7,setparam:1,setpercentthreshold:7,setpercenttoeliminateperiter:7,setsearch:7,setsourc:7,settimelog:1,setup:1,shall:[1,9],share:6,should:[1,2,7],show:[1,2,9],shown:[1,5],sif:1,signific:1,similar:[0,1,2,6],simpl:1,singl:1,singleton:[1,3],site:6,size:[7,9],sklearn:1,smo:[2,7],snack:6,sofocl:1,solari:6,solut:[6,9],some:[1,3,6,7,9],somehow:[1,3],someth:6,sometim:9,sort:[1,9],sourc:[1,2,3,6,7,9],sourcefil:7,space:[1,2,3],special:1,specif:[1,2,3,7],specifi:[1,2,3,5,6,7,8],sphinx:1,split:[7,9],src:6,ssl:6,ssl_verifyp:9,stabil:9,standalon:1,standard:[1,7],start:[1,6,7,9],startstr:7,stat:[1,2],state:[1,6],statement:3,statist:[1,8],statisticalrank:1,statu:6,std:6,step:1,still:[2,6,9],stop:[3,7,9],store:[1,2,3,6,7,9],str:[1,3],str_split:9,strategi:[1,2,3],string:[1,3,7,9],stringr:9,stringsasfactor:9,strong:6,strongli:1,strtoi:9,structur:[1,4,6],studi:1,sub:[3,8],subclass:1,subdirectori:7,submodul:1,subnetwork:[1,3],subnetworknam:3,subprocess:3,subsequ:[1,3],substr:9,subtyp:5,successfulli:6,sudo:6,suffix:1,sum:[1,6,7],summar:7,suppli:9,support:[2,3,5,9],sure:[3,5,6],svm:[1,2,7],svmattributeev:7,svml:2,svmprfe:[2,7],svmrfeselector:1,syntax:1,sysexit:7,system:[1,4,7],systemarpack:6,systembla:6,systemlapack:6,tabl:[1,5,9],take:[1,6],taken:1,tar:6,target_indic:9,task:[1,2],taxonomi:1,tee:6,term:[1,2,5],test:1,text:1,tgt:1,tgt_timestamp:1,than:[1,2,4,6],thei:[1,6,9],them:[1,2,3,7],theme_bw:9,themselv:1,theoret:1,theses:1,thi:[0,1,2,3,6,7,9],third:1,those:[1,6],thread:6,three:[1,3,9],threshold:[1,2],throughout:1,thu:1,tian:1,ticket:1,tidi:1,tidyr:9,time:[1,6,8],timelog:[1,8],timestamp:1,titl:[1,9],tmp:6,token:6,too:1,tool:9,top:[1,2,7,8,9],top_k_overlap:2,topgen:9,topk:[1,9],topkmax:[1,2,7],topkmin:[1,2,7],tostr:[7,9],tosummarystr:7,toward:[1,2],tp53:5,trad:2,trad_scor:1,tradapproach:1,tradit:[1,2,3],tradition:2,traditiona:1,traditional_method:2,tradscor:1,trailingonli:9,train:9,trainandevaluatewithtopkattribut:7,transfer:1,transform:[1,2,3],transit:1,transport:6,transpos:1,transposed_input:3,transposemetadatamatrix:1,travers:1,tree:[6,7],treshold:2,trigger:1,troubleshoot:4,tupl:1,tutori:6,two:[0,1,9],type:[1,3,5,6,9],typic:[1,6],u_noexcept:6,ubuntu:4,ucnv:6,uenum:6,uml:[1,4],umls_auth:1,unabl:6,unavail:6,under:2,underli:1,unicod:6,uninstal:6,union:1,uniprot:1,uniqu:[1,9],univari:1,unlabel:1,unlabeleddata:9,unless:[2,8],unlist:9,unpack:6,unstabl:[1,9],until:1,updat:[1,4,6,7],updatescor:1,upset:9,upsetdiagramcr:9,upsetr:[1,9],uri:1,url:[1,2,3],usag:[1,4,9],use:[1,2,3,6,7,9],useast:9,used:[1,2,3,6,7,8,9],useensembl:9,user:[1,3,6],userconfig:1,useridlist:1,userlistid:1,uses:[1,3],using:[1,3,7,9],usr:6,usual:1,util:[1,3,4,7],uts:1,valid:[1,2,4,7,8],valu:[1,2,3,7,9],valueof:7,vari:1,variabl:6,varianc:[1,2,9],variance2selector:1,varianceselector:[1,9],variant:9,vector:[1,2],venn:1,veri:[1,6,9],version:[1,3,6],vert:1,via:[1,2,6,8],visual:[1,8],vocabulari:1,wai:1,waikato:1,wait:3,want:[1,2,3,5,6,9],warn:6,wchar_t:6,wdate:6,web:[0,1,2,4,6],webservic:1,webservice_uri:2,webservice_url:[2,3],weight:[1,2],weighted_kegg_infogain:1,weighted_trad_kb:2,weightedareaunderroc:7,weightedfmeasur:7,weightedmatthewscorrel:7,weightedprecis:7,weightedtruenegativer:7,weightedtruepositiver:7,weka:[1,6,7],weka_evalu:7,weka_featureselector:7,well:[1,6],went:6,were:[1,3,7,9],werror:6,wformat:6,wget:6,what:[1,3,4,6,9],whatev:[3,6],whatever_you_ne:3,when:[1,3,6,7],where:[1,2,3,4,6,7,9],whether:[1,2,5,9],which:[0,1,2,3,6,7,9],whole:1,whose:[1,8],wiki:3,within:[2,3],without:[1,3],work:1,would:5,wrap:1,wrapper:[1,2],wrapperselector:1,write:[1,3,6,7,9],writemappedfil:1,writenext:7,writer:7,writerankingtofil:1,written:[1,3],wrong:6,wsdl:3,www:[1,3],x86_64:6,xml2:6,xml2_util:6,xml:[1,6],xmlmemori:6,xrefdb:1,xrefid:1,xtune:[1,6,9],xxx:8,xzvf:6,yet:4,ylabel:1,you:[1,2,3,5,6],your:[1,2,3,5,6,8,9],your_str:3,yournetworkselector:3,yournetworkselectornam:3,yourselectornam:3,yourselectorname_kbnam:3,yourselectorname_tradname_kbnam:3,zeng:[2,9],zero:6,zip:6},titles:["System Architecture","Python Code Documentation","Configuration Parameters","How-Tos","Welcome to Comprior\u2019s documentation!","Input Data Sets","Installation and Usage","Java Code Documentation","Output Folder Structure  - Where to find what Files","R Code Documentation"],titleterms:{"class":[0,3],"function":3,"new":3,Tos:3,access:3,add:3,anoth:3,approach:3,architectur:0,base:3,benchutil:1,biomart:2,classif:2,code:[1,3,7,9],compon:0,comprior:4,config:3,configur:2,cross:5,custom:3,data:5,dataset:2,diagram:0,disgenet:2,document:[1,4,7,9],enrichr:2,evalu:[0,1,2,7],execut:3,express:5,featur:[3,7,9],featureselect:[0,1],featureselectorfactori:3,file:[3,8],find:8,folder:8,from:3,gconvert:2,gene:[2,5],gener:2,how:3,implement:[2,3],includ:3,indic:4,input:[5,8],instal:6,intermedi:8,invok:3,java:[2,3,6,7],jdk:6,kegg:2,knowledg:3,knowledgebas:[0,1,3],knowledgebasefactori:3,languag:3,maven:6,metadata:5,method:2,modul:1,need:2,network:3,opentarget:2,option:3,output:8,paramet:2,parser:3,pathwai:3,pathwaycommon:2,pipelin:[1,3],predict:2,preprocess:[0,1,2,3],preprocessor:3,program:3,python:1,rank:2,regist:3,result:8,select:[2,3,7,9],selector:3,servic:3,set:5,structur:8,system:0,tabl:4,than:3,troubleshoot:6,ubuntu:6,uml:2,updat:3,usag:6,util:9,valid:5,web:3,welcom:4,what:8,where:8,yet:2}})