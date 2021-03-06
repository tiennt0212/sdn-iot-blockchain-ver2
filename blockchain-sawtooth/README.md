# Network model in case of Single-Node

![init-project](./images/single-node.png)

# Network model in case of multiple validator
You can read more in [![Sawtooth Docs](https://sawtooth.hyperledger.org/docs/core/releases/latest/app_developers_guide/docker_test_network.html) <br/>
Each node in this network runs a validator, REST-API, settings-tp and OCEAN-tp <br/>
**Important:**  Each node in a Sawtooth network must run the same set of transaction processors.
![init-project](./images/multi-validator.png)
### About consensus algorithm
You can choose either PBFT or PoET consensus. <br/>
> In my model, i use PoET consensus.

# How to build a network with OCEAN transaction processor?
## First of all, generate a docker image for transaction processor
```
docker build -t thanhtien-oceansong-tp:6.0 ./oceansong-tp/pyprocessor
```
> This command will make a docker images. This images will be used in docker-compose file (at Second step)
## Second, run script in docker-compose file to generate network model.
```
docker-compose -f docker-compose.yaml up
```