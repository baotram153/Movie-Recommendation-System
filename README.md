# MOVIE RECOMMENDATION SYSTEM

## Introduction
- This repo is our attempt to demo the use of tools like pandas, sns, matplotlib to extract useful ingisights and visuallize data, and the use of Mongodb for big data storage, and Apache Spark for efficient big data processing.
- We use the `movielens` dataset, which includes movie informations and movie ratings by multiple users, from the website https://movielens.org.

## Run the Movie Web App
1. Setup a virtual environment and download dependencies
    ```sh
    cd Movie-App
    python -m venv env
    ./env/Scripts/activate
    pip install -r requirements
    ```

2. Build the db
    ```sh
    python
    >>> from app import app, db
    >>> with app.app_context():
    >>>     db.create_all()
    ```
    - Running this script will create an instance folder which contains the database

3. Run the app
    ```sh
    python app.py
    ```

## Installation
-----------------REQUIREMENTS FOR THE 1ST NOTEBOOK-----------------

1. Download dataset from MovieLens
    - Due to limited resource, we use the `ml-latest-small` dataset, which can be downloaded via this link: https://files.grouplens.org/datasets/movielens/ml-latest-small.zip
    - You can also try the recommended MovieLens 32M dataset, which is much bigger and can provide better insights: https://files.grouplens.org/datasets/movielens/ml-32m.zip
    

----------------REQUIREMENTS FOR THE 2ND NOTEBOOK----------------

2. Download Apache Spark
    - Method 1: which allows you to write Python applications for Spark but doesn’t include the full Spark setup. This installation doesn’t come pre-configured for Hadoop or other cluster managers, so it’s more commonly used for local or small-scale testing, which is what we'll do in this demo. So this is good enough.
        - `pip install pyspark`
        - Then you can just directly import `pyspark` and run the python script directly via `python <script_name>.py`
    - Method 2 (we call it Spark&Hadoop :v): This approach gives you the full Spark distribution, including core components for cluster management, libraries (MLlib, Spark SQL, etc.), and support for different cluster managers (e.g., Hadoop/YARN). You have to set up the environment, configure it for your system, and ensure that it works with your chosen cluster manager. The following link includes Spark compiled with Hadoop 3, which enables you to use Spark on a Hadoop cluster.
        - Download Apache Spark distribution from this link: https://spark.apache.org/downloads.html

3. Download JDK 8
    - Choose the package suitable for your OS: https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html

4. Setup environment
    - Add environment variable:
        - JAVA_HOME = <path-to-your-jdk>
        - For Spark&Hadoop, you have to configure a few more
            - For Hadoop
                - Download `winutils.exe` according to your Hadoop version from: https://github.com/steveloughran/winutils
                - Put `winutils.exe` in a `bin` folder and put that bin in a `hadoop` folder
                - Set HADOOP_HOME = <path_to_hadoop_folder>
            - For Pyspark
                - PYSPARK_HOME = python (make sure you've specify the environment paths to `Python<version>` and `Python<version>/Scripts`, where `<version>` is the python version you're using)
                - SPARK_HOME = <path_to_spark>
    - Add paths
        - %JAVA_HOME%\bin
        - For Spark&Hadoop, you have to configure a few more
            - %HADOOP_HOME%\bin
            - %SPARK_HOME%\bin
    - The configuration for Apache Spark distribution prebuilt for Hadoop is incomplete, despite our effort, we still receive bugs under this configuration!!! :<

5. Install MongoDB
    - Via this link: https://www.mongodb.com/try/download/community
    - Create a connection

## Further development
- We will try to use spark on a cluster of computers
- Build a web server using Flask
    - A page for movie recommendation
    - A page for movie filter
