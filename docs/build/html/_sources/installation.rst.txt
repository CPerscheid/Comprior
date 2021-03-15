Installation and Usage
======================

Installation
************

* Prerequisites: R 3.5+, Python 3.5+, Java with JDK, and Maven. See in :ref:`installingJavaMaven` how to install JDK and Maven.
* check out the repository on your machine (or download the sources from https://github.com/CPerscheid/Comprior/archive/master.zip)::

    git clone https://github.com/CPerscheid/Comprior.git

* Run the installation bash script *install.sh* (if your are on MacOS, use *install_macos.sh*) and let it write its output into a file (the tee command prints the output to both command line and a file) - installation execution requires root access rights::

    sudo ./install.sh 2>&1 | tee installout.out

* go grab some healthy snacks, for this might take a while depending on what is already installed on your machine :-)
* check *installout.out* for any errors
* check *code/configs/config.ini* if the variables *homePath* (path to Comprior's root directory), *RscriptLocation* (path to your Rscript), and *JavaLocation* (path to your Java location) point to the right locations.

Usage
*****

* Prior information: In order to enable a flexible pipeline design for users, Comprior makes use of config files. All config files are to be stored in *code/configs* directory. **The main config file is located at code/configs/config.ini.** It is recommended not to be changed, as it specifies all parameters that Comprior needs for functioning properly, including access points to knowledge base web services and output folder structure. Instead, users can specify an own config file that contains only those parameters they want to overwrite from *config.ini*, e.g. where the input data is located or what feature selectors to apply. **Store your custom config file in the code/configs/ directory.** For a complete overview of the input parameters, see :ref:`inputParams`. If you write an own config file, make sure to provide it as input parameter for the framework (*config.ini* will always be loaded by default)

* To start Comprior
    * navigate to *code/Python/comprior*::

        cd code/Python/comprior

    * start Comprior (optionally provide a custom config file)::

        python3 pipeline.py --config ../../configs/exampleconfig.ini

* Check your results in *data/results/example* - see :ref:`outputStructure` for where to find what results.

.. _installingJavaMaven:

Installing Java JDK and Maven on Ubuntu
***************************************

* install a JDK distribution for your Ubuntu version, e.g.::

    sudo apt-get install openjdk-8-jdk

  or::

    apt install default-jdk

* let your JAVA_HOME variable point to your installed JDK. Typically, Ubuntu installs it in /usr/lib/jvm, so find it there and provide the correct path, e.g.::

    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

* also update your PATH variable to point to your JDK::

    export PATH=$PATH:$JAVA_HOME/bin

* check your variables by typing::

    echo $PATH
    echo $JAVA_HOME

* you can store the above variables permanently by just adding the above commands to */etc/profile.d/myenvvars.sh* (or similar name)::

    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
    export PATH=$PATH:$JAVA_HOME/bin

* install Maven::

    wget https://ftp.fau.de/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz -P /your/path/to/
    tar xzvf /your/path/to/apache-maven-3.6.3-bin.tar.gz -C /your/path/to/
    export PATH=/your/path/to/apache-maven-3.6.3/bin:$PATH

Troubleshooting
***************

::

    Cannot find xml2-config
    ERROR: configuration failed for package ‘XML’

* install libxml2-dev, e.g. when on Ubuntu *apt install libxml2-dev* or similar (the available package name depends on your Ubuntu distribution, which you can find out with the help of this tutorial https://itsfoss.com/unable-to-locate-package-error-ubuntu/)

::

    FileNotFoundError: [Errno 2] No such file or directory: 'curl-config': 'curl-config

* this error comes from pycurl - install *libcurl4-openssl-dev* and *libssl-dev* packages, e.g. when on Ubuntu *apt install libcurl4-openssl-dev libssl-dev* or similar (the available package name depends on your Ubuntu distribution, which you can find out with the help of this tutorial https://itsfoss.com/unable-to-locate-package-error-ubuntu/)

::

    WARNING: Failed to load implementation from: com.github.fommil.netlib.Native*** (SystemBLAS, RefBLAS, SystemLAPACK, RefLAPACK, SystemARPACK, RefARPACK)

* this can happen when running on Ubuntu and is related packages internally used by  `WEKA <https://waikato.github.io/weka-wiki/faqs/ubuntu_1804_blas_warning/>`_
* install *libgfortran-6-dev* package, e.g. when on Ubuntu *apt-get install libgfortran-6-dev* or similar (the available package name depends on your Ubuntu distribution, which you can find out with the help of this tutorial https://itsfoss.com/unable-to-locate-package-error-ubuntu/)

::

    [ERROR] No compiler is provided in this environment. Perhaps you are running on a JRE rather than a JDK?

* you either do not have a JDK installed or your variables point to the wrong location. Follow :ref:`installingJavaMaven` for installing JDK and setting the environment variables correctly.


::

    Configuration failed because libxml-2.0 was not found. Try installing:
    * deb: libxml2-dev (Debian, Ubuntu, etc)
    * rpm: libxml2-devel (Fedora, CentOS, RHEL)
    * csw: libxml2_dev (Solaris)
    If libxml-2.0 is already installed, check that 'pkg-config' is in your
    PATH and PKG_CONFIG_PATH contains a libxml-2.0.pc file. If pkg-config
    is unavailable you can set INCLUDE_DIR and LIB_DIR manually via:
    R CMD INSTALL --configure-vars='INCLUDE_DIR=... LIB_DIR=…'

* lixml-2.0 is not installed. Follow the recommendations stated there and install it, e.g. by *apt-get install libxml2-dev* or similar (the available package name depends on your Ubuntu distribution, which you can find out with the help of this tutorial https://itsfoss.com/unable-to-locate-package-error-ubuntu/)

::

    Configuration failed because openssl was not found. Try installing:
    * deb: libssl-dev (Debian, Ubuntu, etc)
    * rpm: openssl-devel (Fedora, CentOS, RHEL)
    * csw: libssl_dev (Solaris)
    * brew: openssl@1.1 (Mac OSX)
    If openssl is already installed, check that 'pkg-config' is in your
    PATH and PKG_CONFIG_PATH contains a openssl.pc file. If pkg-config
    is unavailable you can set INCLUDE_DIR and LIB_DIR manually via:
    R CMD INSTALL --configure-vars='INCLUDE_DIR=... LIB_DIR=…'

* openssl is not installed. Follow the recommendations stated there and install it, e.g. by *apt-get install libssl-dev* or similar (the available package name depends on your Ubuntu distribution, which you can find out with the help of this tutorial https://itsfoss.com/unable-to-locate-package-error-ubuntu/)


::

    ** package ‘xml2’ successfully unpacked and MD5 sums checked
    Found pkg-config cflags and libs!
    Using PKG_CFLAGS=-I/usr/include/libxml2
    Using PKG_LIBS=-lxml2 -lz -llzma -licui18n -licuuc -licudata -lm -ldl
    ** libs
    g++ -I/usr/share/R/include -DNDEBUG -I../inst/include -I/usr/include/libxml2 -DUCHAR_TYPE=wchar_t    -fvisibility=hidden -fpic  -g -O2 -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2 -g  -c connection.cpp -o connection.o
    In file included from /usr/include/unicode/uenum.h:23:0,
             from /usr/include/unicode/ucnv.h:53,
             from /usr/include/libxml2/libxml/encoding.h:31,
             from /usr/include/libxml2/libxml/parser.h:810,
             from /usr/include/libxml2/libxml/globals.h:18,
             from /usr/include/libxml2/libxml/threads.h:35,
             from /usr/include/libxml2/libxml/xmlmemory.h:218,
             from /usr/include/libxml2/libxml/tree.h:1307,
             from xml2_utils.h:5,
             from connection.cpp:3:
    /usr/include/unicode/localpointer.h:224:34: error: expected ‘,’ or ‘...’ before ‘&&’ token
    LocalPointer(LocalPointer<T> &&src) U_NOEXCEPT : LocalPointerBase<T>(src.ptr) {
    ...
    make: *** [connection.o] Error 1
    ERROR: compilation failed for package ‘xml2’
    * removing ‘/usr/local/lib/R/site-library/xml2’

    The downloaded source packages are in
        ‘/tmp/Rtmpashma8/downloaded_packages’
    Warning message:
    In install.packages("xml2") :
    installation of package ‘xml2’ had non-zero exit status

* There seems to be a different compiler required than what is currently provided in your  *~/.R/Makevars* file. Add *CXX=g++ -std=c++11* (or whatever is stated at the very beginning of the error) to your *~/.R/Makevars* file. The problem and solution are also described here: https://github.com/r-lib/xml2/issues/294

::

    Error: package or namespace load failed for ‘glmnet’ in dyn.load(file, DLLpath = DLLpath, ...):
    unable to load shared object '/usr/local/lib/R/site-library/00LOCK-glmnet/00new/glmnet/libs/glmnet.so':
    /usr/lib/x86_64-linux-gnu/libgfortran.so.5: version `GFORTRAN_1.0' not found (required by /usr/local/lib/R/site-library/00LOCK-glmnet/00new/glmnet/libs/glmnet.so)

* the R package glmnet (used by xtune package) needs a Fortran interpreter. If you have not installed it already, install it. If you have installed it already, adapt *~/.R/Makevars* and add *CC=gcc*

::

    ImportError: pycurl: libcurl link-time ssl backends (secure-transport, openssl) do not include compile-time ssl backend (none/other)

* Looks like something went wrong with pycurl/openssl. Try this::

    pip3 uninstall pycurl
    pip3 install --compile --install-option="--with-openssl" pycurl

  * if it still fails, try this as well::

      brew reinstall openssl
