# Readme

**Docker engine and docker compose**

The Docker engine and Docker compose is automatically installed by executing the shell script on the /home/thep_natchanon/docker_setup.sh

**#Command**

```bash
./docker_setup.sh
```

# **VM Instance**

There are 2 instances used in this project:

- *airflow-instance*

    Link: [http://34.133.28.23:8080/](http://34.133.28.23:8080/) (start airflow container first)

- *spark-jupyter-instance*

    Link: [http://34.121.118.190:8888/](http://34.121.118.190:8888/) (start jupyter notebook first)

Remote Access VM via SSH

![Image](https://lh5.googleusercontent.com/pjaFGD40yx4kj5Gs_2z8rcQMxPWmTrZMwRQgIuY488wT6UZ01S6bTdikRlOVt-z8DgICDHpf0zGACS4DYzibLCzAOs5IHFa8roZw36OtPSBZcxOdLpZWv0Deeve3lGhKGvb7kGgN)

# **Google Cloud Storage**

The data source will be ingested and stored in the bucket path:

**gs://demo-landing-bucket/raw_data**

In the transformation step, the data is transformed and stored in

**gs://demo-landing-bucket/cleaned**

# **Google Cloud Bigquery**

**Table ID**

demo-natchanon:demo_dataset.user_log

demo-natchanon:demo_dataset.users

# Airflow-instance guide

## Start airflow container

```bash
sudo docker-compose up -d
```

## Initial airflow database & add user, pass

```bash
sudo docker-compose up airflow-init
```

## Stop airflow container

```bash
sudo docker-compose down
```

## Check services health

```bash
sudo docker ps
```

## Access container

```bash
sudo docker exec -it <CONTAINER_ID> bash
```

## Edit DAG

```bash
# access container first
cd ~/data-platform-demo/airflow-docker/
vi demo_dag.py
```

# Data pipeline (DAG)

Dag id : demo_dag

Schedule_interval: hourly

Graph view

![Image](https://lh3.googleusercontent.com/T7zlmytLWBKlP3gd9IS-ou0WLOwSScWuY4DzlNedgwrT2PC2gxZEb_VqHLCPyXpupY-J6KREPP8hNQEbIXf8h9sx_JoDWfbcpK7wA25lXj4b4eJ1f5QC5dyVhotqeRu5dEcbmdbt)

# **Airflow Variables and Connection**

**my_postgres_conn**

![Image](https://lh4.googleusercontent.com/9yI7vf96STGeULme3GF7i02jhYvzFArKTnzyJVOZHmGPXCuLt5yZR8hUdg6vEJmzU_KmyYYm0nKQ9hCdwlOPmUHmnW7jcB0ZE-7P837JmEFGswOTrIQNdKuusrpfdQwbqWQbk299)

# Spark - jupyter notebook

## Start jupyter notebook

```bash
jupyter notebook
```

## PySpark read bigquery table example

The example notebook is stored on 

~/notebook/example.ipynb