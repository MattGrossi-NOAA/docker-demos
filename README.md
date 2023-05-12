# docker-demos

#### Experimental Docker demonstrations for learning and teaching

## Summary

This repository contains minimal working examples (MWEs) of Docker containerization to demonstrate how to configure and use containers. Its primary purpose is twofold: first, to help me learn Docker myself, and second, to serve as a teaching tool when I introduce others to containerization. It is my intent that the repository will continue to grow as I encounter new applications for Docker and dive deeper into its many capabilities and sophistications. It is also very like to be updated, edited, or revised as I continue to learn more.

The contents are as follows:

### /linear\_classifier

<details>
  <summary>
  A simple yet somewhat realistic MWE of a containerized Python model
  </summary>

For this demo, I created and containerized a straightforward linear classification model that can be used on binary class data. There are no bells and whistles attached and it is far from optimzed coding; this is simply a Python class object with a few methods like one might code up for real world problems. For a description and discussion of the demo, see the accompanying [README therein](https://github.com/mdgrossi/docker-demos/blob/main/linear_classifier/README.md).

</details>

### /linear\_classifier\_jupyter

<details>
  <summary>
  A containerized Jupyter notebook used to develop a simple Python model
  </summary>

This demo contains a working Jupyter notebook used to develop and test the simple linear classifier model from the [linear\_classifier](https://github.com/mdgrossi/docker-demos/tree/main/linear_classifier_jupyter) example. This container deploys a Jupyter server with which the user can familiarly interact via a web browser. For a description and discussion of the demo, see the accompanying [README therein](https://github.com/mdgrossi/docker-demos/blob/main/linear_classifier_jupyter/README.md).

</details>


## Why containerization?

Containers offer a number of benefits to both the developer and the end-user of an application, a model, or any source code. Containerizing an application, a model, or source code enhances:

1. **Portability** between computers, across operating system platforms, or on-prem to the cloud
2. **Reproducibility** by specifying all dependencies and versions to ensure that every deployment is configured identically
3. **Scalability** such that the number of instances of the software can easily be scaled up (or down) depending on needs
4. **Security** by isolating the software itself from the hardware on which it is running

## What is a container?

A **container** is a lightweight and portable package containing source code and all dependences, including libraries and runtime environments, needed to run an application, a model, or a script. It allows code to be shipped, tested, and deployed easily, ensuring it runs the same way every time and on every system. How containers work is beyond the scope of this discussion; plenty of information can be found online. For now, we need only think about a container as a directory containing all relevent scripts, data, and some configuration files.

More accurately, _containers_ are runnable instances of _images_ that run in isolation from all other processes on the host machine. An image, in turn, is a read-only template that contains custom, isolated filesystems; all dependencies, configurations, scripts, binaries, _etc._ needed to run the software; and container configurations such as environmental variables, commands to run, and other metadata (see, _e.g._, [Docker overview](https://docs.docker.com/get-started/overview/)).

> :bulb: **Example:** As any Python developer knows, package management is critically important in Python -- and if one is not careful, things can get pretty messy rather quickly when different versions of packages start clashing with each other.[^1] Package management is one main reason Anaconda exists. It is also why best practices for Python traditionally involves working in project-specific virtual machines (VMs). Containers can be likened to VMs, but under the hood they are quite a bit different (and arguably better.)
>
> [^1]: This is not to pick on Python, as it's true of many/most programming languages.

## Docker

[Docker](https://docs.docker.com/) is one of the most common container management platform options (some others being [Podman](https://podman.io/) and [Kubernetes](https://kubernetes.io/)). Once [downloaded and installed](https://docs.docker.com/get-docker/) locally, Docker can be used to create, run, and interact with containers. A Docker container requires a few components:

1. **Source code**: the application (app), model, or source code script(s)
2. **Requirements**: a list of package dependencies
3. **Dockerfile**: blueprint for building and running the container image
4. **Docker-compose**: a yml file containing instructions for building and running the container itself

Suppose we have a model written in Python that we would like to deploy on a new machine. For simplicity, let's assume this model has only one package dependency: numpy.  Our Docker container would look like this:

```bash
home/user/modelDir/
├── myNiftyUselessModel.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
```
Let's take a look at each of these files.

### myNiftyUselessModel.py

This is our source code, the model itself:

```python
import numpy as np

def model():
    mysum = np.add(1, 1)
    print("I can't predict anything, but I know that 1 + 1 = {}.".format(mysum))

if __name__ == "__main__":
    model()
```

The model or app can consist of multiple scripts, as long as every required script is somewhere within this modelDir directory. We will see why this important shortly.

### requirements.txt

This file contains a simple list of non-base libraries the model requires, one per line. In this example, the text file contains only one item:

```
numpy==1.24.3
```

> :bulb: **Hint:** Look at the `import` calls in all relevant scripts to know what needs to be included in this container. Remember that only _non-base_ libraries need to be listed.

Note that the version number is technically not required here, but it is best practice (and much safer) to include it. If omitted, the most recent version of the package(s) will be downloaded, and there is no guarantee those versions will be compatible with the scripts.

If this model was created within its own virtual environment on the local machine (which it should have been, if we're adhering to best practices), the requirements file can be generated by runnning in a terminal window either

```bash
pip freeze > requirements.txt
```

for pip environments or

```bash
conda list -e > requirements.txt
```

for Anaconda environments. Both methods automatically include version numbers in the list produced. It is worth noting here that requirement lists generated from Anaconda environments tend to be much longer (and arguably more cluttered) than those generated from pip environments. This is because Anaconda is more liberal than pip with downloading and installing dependencies whenever a user downloads a specific package. For a clearner container, one might consider generating the `requirements.txt` file, whittling down the list to only those packages explicitly called for in the scripts, and then re-adding package dependencies afterwards as needed. While this is not entirely necessary, it can save time when building the container by eliminating the installation of unnecessary (to the script itself) packages.

### Dockerfile

The `Dockerfile` (no extension) defines steps for creating the image and (optionally) what to do upon creation. Here we have a very simple Dockerfile:

```
FROM python:3.8

WORKDIR /home/jovyan/mymodel
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "./mymodel/myNiftyUselessModel.py"]
```

Think of this as a series of commands with each instruction creating a layer within the image. The first step downloads and installs a base image `FROM` [Docker Hub](https://hub.docker.com/), a public repository of container images. We opted for a [Python image with Python 3.8](https://hub.docker.com/_/python) installed, where `python` (text before the colon in the FROM command) indicates the image name and `3.8` (following the colon) is the desired tag, which, in this case, specificies the version and type of Python install (see the [docs](https://github.com/docker-library/faq#whats-the-difference-between-shared-and-simple-tags) for more information).

The next command creates a working directory (`WORKDIR`) inside the container. Recall that containers have their own isolated file structure. We are creating a directory a "home", made-up user "[jovyan](https://github.com/jupyter/docker-stacks/issues/358)", and "mymodel" directories in which we `COPY` our `requirements.txt` file so that the container will have access to it.

> :writing_hand: Note: If we do not explicitly copy items into the container's file structure, the container will not have any idea they exist. This is what is meant by "isolated file system."

Next, the required packages are installed from the text file. This is done by telling Docker to `RUN` the appropriate shell command.

> :bulb: We could have opted for an Anaconda image instead (they exist in Docker Hub), in which case we would install packages with `conda install --yes --file requirements.txt` instead. See the Docker and Anaconda documentation for more information.

Finally, once the container is launched, the model is run by issuing the command (`CMD`) as in bash. This line could also have been written:

```
RUN python ./home/jovyan/mymodel/myNiftyUselessModel.py
```

### docker-compose.yml

This file provides an alternative to passing command line configuration arguments when spinning up the container. These files are also extremely helpful when multiple containers need to be spun up together and interact with each other, but that is beyond the scope of this demo. The `docker-compose.yml` file looks like this:

```
version: '3.3'
services:
  mymodel:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - /home/user/modelDir:home/jovyan/mymodel
```
This is telling Docker what version of [Docker Compose](https://docs.docker.com/compose/) to use, and, under `service`, an arbitrary tag "mymodel" is provided to tag and reference the container, followed by instructions on how to configure (`build`) the container. The container is to be built from the `Dockerfile` located in the same directory as this docker-compose file (hence the `context: .` line -- note the dot!) If the `Dockerfile` was nested somewhere deeper in the file structure, we would pass the directory chain to `context`. The last step maps the local directory in which the model resides (see above) to the isolated "mymodel" directory created within the container by the Dockerfile. This step allows the container to interact with the local files; otherwise, it would have no idea they exist.

The `docker-compose.yml` file can contain a great number of commands, as there are many things that can be done with it. In fact, the same is true of Dockerfiles. It is best to read through the docs to become better familiar with these tools and what they are each capable of.

### Creating and using this container

Now that all of the components are in place, how do we actually create and use the container? [Installing Docker](https://docs.docker.com/engine/install/) also installs a Docker command line interface (CLI) with terminal commands for everything we might want to do with our container. In a local terminal navigated to the directory of the `docker-compose.yml` file:

1. **Build** the image:
```bash
docker-compose build
```
2. **Spin up** the container:
```bash
docker-compose up
```
or
```bash
docker-compose run -rm mymodel
```
where `mymodel` is the tag we assigned to the container in the `docker-compose.yml` file. In this simple example, this step will spin up the model, run it (the last line of the Dockerfile), and then shut down the container.

3. **Spin down** the container when done:
```bash
docker-compose down
```

This example is, as the name alluded to, rather useless. It is intended entirely for illustrative purposes. See [linear\_classifier](https://github.com/mdgrossi/docker-demos/tree/main/linear_classifier) or [linear\_classifier\_jupyter](https://github.com/mdgrossi/docker-demos/tree/main/linear_classifier_jupyter) more realistic -- albeit still overly simplified -- examples that can be downloaded, run, and experimented with for practice.

## Disclaimer

This overview is subject to change as I myself learn more about Docker, how to use and implement it, its capabilities, _etc_. This document, neither in its current nor any future form, is not intended to replace the official documentation referenced above. Feedback, suggestions, or corrections are welcome, keeping in mind that this document assumes no authoritative nature whatsoever.