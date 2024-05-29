# Development Containers: Visual Studio (VS) Code

Docker containers can be created and used within [Visual Studio (VS) Code](https://code.visualstudio.com/). Such a container is called a development container, or `devcontainer`. The process for setting one up in VS Code is relatively simple, but not entirely intuitive to the unfamiliar user. This page summarizes the process and will be added to as needed.

## Dockerfile

To create and run a [Docker](https://www.docker.com/) container in VS Code, a [`Dockerfile`](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) is needed. These can be simple or complex; see the [README](README.md) for a demonstrative example. Call this file "Dockerfile" (no extension) and store it in the project parent directory.

## docker-compose.yml

You can also build a `devcontainer` from a `docker-compose.yml` file. Simply create this file and store it alongside the `Dockerfile` in the project parent directory.

## requirements.txt

Include a `requirements.txt` file if needed. For Python environments, this document would contain a list of package dependencies, one package per line, with optional version number. For example:

```
numpy==1.21.5
scikit-learn==1.0.2
scipy==1.9.1
```

See the pip documentation for more information on [how to format these files](https://pip.pypa.io/en/latest/reference/requirements-file-format/#requirements-file-format).

## VS Code

Open VS Code. On the welcome landing page, click "Open Folder..." and select the parent directory where the Dockerfile file lives. The directory and its content should appear in the EXPLORER panal on the left side of the application window.

#### Creating a new `devcontainer` for the first time

1. Click the blue "Open a Remote Window" button in the bottom left corner of VS Code. The icon looks like two angled L's.
2. In the menu that appears at the top, select "Reopen in Container"
3. In the next menu, select "Add configuration to workspace"
4. If a `docker-compose.yml` and/or `Dockerfile` exist with the current directory, the next menu will allow you to choose which one to build the container from ("From 'docker-compose.yml'" or "From 'Dockerfile'"). Select the desired option. A popup will appear in the bottom right as the container starts to build. Click "Show Log" to monitor the progress in a terminal pane.

Behind the scenes, these steps create a new `.devcontainer` directory containing container configuration files.

#### Using an existing `devcontainer`

If you've run the steps above once before, VS Code will detect the `.devcontainer` directory when you navigate to the project directory. A popup should appear in the bottom right corner of VS Code stating that the folder contains a Dev Container configuration file. Click the blue "Reopen in Container" button to spin up the container.

#### Closing the container

When finished, click the blue "Open a Remote Window" button in the bottom left corner of VS Code and select "Close remote container" in the menu that appears at the top of the application window.
