# CONTAINERIZATION: A very quick overview and demo

**Matt Grossi** \
_Data Scientist, NOAA Southeast Fisheries Science Center (SEFSC)_ \
_Fisheries Assessment, Technology, and Engineering Support Division_\
_Advanced Technology and Innovation Branch_

Created:  May 10, 2023

---

## Synopsis

This document describes the minimal working example (MWE) of a containerized Python model presented in this repository but also provides brief introductions to containerization in general and Docker more specifically. These introductory sections are optionally expandable for the interested reader: simply click to learn more.

For an example of a jupyter notebook container, see `docker-demo/linear_model_jupyter/`, which provides a working notebook used to develop and test this model.

## Why containerization?

<details>
    <summary>
    Containers offer a number of benefits to both the developer and the end-user of an application, a model, or any source code.
    </summary>

Containerizing an application, a model, or source code enhances:

1. **Portability** between computers, across operating system platforms, or on-prem to the cloud
2. **Reproducibility** by specifying all dependencies and versions to ensure that every deployment is configured identically
3. **Scalability** such that the number of instances of the software can easily be scaled up (or down) depending on needs
4. **Security** by isolating the software itself from the hardware on which it is running

</details>

## What is a container?

<details>
    <summary>
    A container is a lightweight and portable package containing source code and all dependences needed to run software.
    </summary>

A **container** is a lightweight and portable package containing source code and all dependences, including libraries and runtime environments, needed to run an application, a model, or a script. It allows code to be shipped, tested, and deployed easily, ensuring it runs the same way every time and on every system. How containers work is beyond the scope of this discussion; plenty of information can be found online. For now, we need only think about a container as a directory containing all relevent scripts, data, and some configuration files.

More accurately, _containers_ are runnable instances of _images_ that run in isolation from all other processes on the host machine. An image, in turn, is a read-only template that contains custom, isolated filesystems; all dependencies, configurations, scripts, binaries, _etc._ needed to run the software; and container configurations such as environmental variables, commands to run, and other metadata (see, _e.g._, [Docker overview](https://docs.docker.com/get-started/overview/)).

> :bulb: **Example:** As any Python developer knows, package management is critically important in Python -- and if one is not careful, things can get pretty messy rather quickly when different versions of packages start clashing with each other.[^1] Package management is one main reason Anaconda exists. It is also why best practices for Python traditionally involves working in project-specific virtual machines (VMs). Containers can be likened to VMs, but under the hood they are quite a bit different (and arguably better.)
>
> [^1]: This is not to pick on Python, as it's true of many/most programming languages.

</details>

## Docker

<details>
    <summary>
    Docker is one of the most common container management platforms.
    </summary>

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

The example is, as the name alluded to, rather useless. It is intended entirely for illustrative purposes. We next consider a more realistic -- albeit still overly simplified -- example that the reader can download, run, and experiment with for practice.

</details>

## This Repository: A containerized Python model

<!-- <details>
    <summary>
    A more realistic minimal working example.
    </summary> -->

This repository contains a simple yet somewhat realistic MWE of a containerized Python model. I have created and containerized a straightforward linear classification model that can be used on binary class data. There are no bells and whistles attached, it is far from optimzed coding; this is simply a Python class object with a few methods like one might code up for real world problems. The respository contents are as follows:

```bash
DockerDemo/linear_classifier/
├── linear_classifier.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── banknote.csv
├── skin.csv
├── README.md
```

> :bulb: For a Jupyter notebook container demo, see `docker-demo/linear_classifer_jupyter/`, which contains a Jupyter notebook used to develop and test this linear classifier.

### The contents

The model itself is contained in and run by invoking `linear_classifer.py`. Notice that the script contains four `import` statements:

```python
#!/usr/local/bin/python3 

"""
linear_classifier.py

Author: Matt Grossi (matt.grossi at noaa.gov)
Created: 2023-May-05
"""

import numpy as np
import warnings
import argparse
import sys
```

while `requirements.txt` only contains one dependency:

```
numpy==1.24.3
```

This is because, as mentioned above, only non-base libraries need to be included as requirements, since these need to be downloaded and installed manually before use. `warnings`, `argparse`, and `sys` are all Python base libraries included in any Python install, so they do not need to be listed as dependencies in `requirements.txt`.

The `Dockerfile` and `docker-compose.yml` files are nearly identical to the example above, but note we update pip before installing the package dependencies in `Dockerfile` and have moved model execution to a `command` in `docker-compose.yml`. The reason for this is that the container needs to be re-built whenever a change is made to the configuration. Building the container is done sequentially according to the `docker-compose.yml` (which calls the `Dockerfile` at some point). For complicated containers with many layers to build, this can become cumbersome and time consuming, but thankfully, Docker "remembers" previous states and only rebuilds starting from the command that changed. Thus, if we change the last command in the sequence and rebuild the container, only the last line will be re-executed, but if we modify the first line (_e.g._, if we change the container image on line 1 of the `Dockerfile`), everything thereafter is rebuilt. Accordingly, one can -- and ought to -- strategize when organizing these files such that layers that are more likely to be modified (such as running the model, in this case) are placed at the end of the sequence.[^2] Had the `RUN` command been retained in the `Dockerfile`, each time a model parameter was modified in the command line argument (or if modifications were made to the code itself), rebuilding the container would also remap the storage volumes, since this command comes after the `Dockerfile` is called in `docker-compose.yml`. While this change has minimial impact on this simple example, it could be noticably consequential with more complex real-world container scenarios.

Because this model processes data, the container needs access to the data as well. Hence, we also include two sample data sets in the directory, both from the [University of California, Irvine (UCI) Machine Learning Repository](https://archive.ics.uci.edu/ml/index.php): `skin.csv`, which comes from the [skin segmentation data set](https://archive.ics.uci.edu/ml/datasets/skin+segmentation)[^3], and `banknote.csv`, which comes from the [banknote authentication](https://archive.ics.uci.edu/ml/datasets/banknote+authentication)[^4]. Since the local parent directory is mapped in the container (`docker-compose.yml`, lines 8-9), the container is able to access these data files once spun up. As an alternative to including these data files in the same directory as the model itself, as done here, we could have also mapped a second local directory (_i.e._, wherever the data are stored locally) to the container by adding another line under the `volumes:` argument in `docker-compose.yml`, _e.g._:

```
version: '3.3'
services:
  linearclassifier:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/home/jovyan/model
      - path/to/data:/home/jovyan/data
    command: python linear_classifier.py --data=../data.banknote.csv
 ```

Finally, the last line in `docker-compose.yml` actually runs the model. It is the same thing one would type in a terminal to run the script, including the model's command line arguments. (Note the additional modification to the `command` in the example code block above to point to the alternative data directory if we chose to do that.) These arguments can be changed within `docker-compose.yml`, but remember to re-build after every change:

```bash
docker-compose build
```

### Try it!

Try this for yourself by cloning this repository to your local machine; navigating to it in a Terminal or Command Prompt window; and building, spinning up, and spinning down the container as described above. In its current form, the script will read in the specified data file, split the data into training and testing subsets, and attempt to train a linear classifier. Performance should be printed out indicating that it worked. Best of all, this should work regardless of what computer you try it on or what operating system you are running on your machine.

And that is one of the beauties of containers and why we use them!

[^2]: Of course, there will always be some commands that have to follow a specific order of operations. For exaxmple, one cannot run a Python code without first installing the dependencies. But other tasks like mounting volumes or mapping ports can be done anywhere in the sequence.

[^3]: Bhatt, Rajen and Abhinav Dhall (2012) 'Skin Segmentation Dataset', UCI Machine Learning Repository, https://doi.org/10.24432/C5T30C, retrieved May 10, 2023.

[^4]: Lohweg, Volker (2013) 'banknote authentication', UCI Machine Learning Repository. https://doi.org/10.24432/C55P57, retrieved May 10, 2023.

<!-- </details> -->

## Recommendations
1. Keep `requirements.txt`, `Dockerfile`, and `docker-compose.yml` files in the highest parent directory of your project. If the container is configured as above, it will have access to everything within that parent directory.
2. Make this parent directory a GitHub repository for version control and easy sharing.
3. Structure your Dockerfiles and docker-compose files strategically so that items that are more likely to be tweaked or modified show up towards the end of the sequence, while commands that are generally not going to change come first.
4. Take time to peruse the documentation for both [Docker](https://docs.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to fully appreciate the range of capabilities and options these tools offer.
5. Start each new project from now on in a container instead of a virtual machine. There is undoubtedly a learning curve that will take some time to navigate, but you will (eventually) be glad you did.

## Disclaimer

This overview is subject to change as I myself learn more about Docker, how to use and implement it, its capabilities, _etc_. This document, neither in its current nor any future form, is not intended to replace the official documentation referenced above. Feedback, suggestions, or corrections are welcome, keeping in mind that this document assumes no authoritative nature whatsoever.