# Scraping Database Generator
Database generation infrastructure for scraping projects. 

## Functionality
- Derive and generate a database structure from API responses.
- Analyze websites for scraping processes
- Archive websites
- Derive crawling and scraping processes from websites architecture. (Utilizes LLMs and therefore is more hardware intensive!)

## Installation as Docker container
### 1. Install Docker
```sh
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
(https://docs.docker.com/engine/install/ubuntu/)

For GPU support, additionally install the NVIDIA-Docker-Runtime:
```sh
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu20.04/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2 nvidia-container-runtime

sudo systemctl restart docker
```
(https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0))

Note: If you choose GPU-support, from now on replace the command `docker` with `nvidia-docker`!

### 2. Clone or download and unpack this repository

After cloning or downloading and unpacking, you might want to add to or adjust the code. An example might be `Dockerfile`, specifically the installed packages.

### 3. Build a Docker image from the repository

```sh
docker build -f <path to repo folder>/Dockerfile.cpu -t scraping-database-generator-container:v0.1
```
### 4. Start a container based off of the image
```sh
docker run  \
    -it --net=host -p 7860:7860 --gpus all \
    --mount type=bind,source=<my local text generation model folder>,target=/scraping-database-generator-container/machine_learning_models/GENERATION_MODELS \
    --mount type=bind,source=<my local text embedding model folder>,target=/scraping-database-generator-container/machine_learning_models/EMBEDDING_MODELS \
    --mount type=bind,source=<my local LoRA model folder>,target=/scraping-database-generator-container/machine_learning_models/LORAS \
    --mount type=bind,source=<my local working data folder>,target=/scraping-database-generator-container/data \
    "scraping-database-generator-container:v0.1"
```
Note, that mounting the four shared folders above is not mandatory but strongly recommended. Not linking these folders will result in potentially duplicate models and working data being downloaded into the docker container's folder structure and therefore will blow up the container size.

Note, that you can also open a terminal by appending `/bin/bash` to the command above. You will get to a terminal inside the running container. Afterwards you can start the explorer manually with `bash run.sh`.

### 5. (Re)run the container
If you exit the container and it is stopped, you can use 
```sh
docker ps --all
```
to retrieve the name of the `scraping-database-generator-container:v0.1` container and rerun and interactively enter it with
```sh
docker restart <container name> &&  docker exec -it <container name> /bin/bash
```
Inside the docker container's shell, you can run the explorer again by using 
```sh
bash run.sh
```
