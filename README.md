# Prepare before running code in repository
### Start Sawtooth validator
```bash
sudo -u sawtooth sawtooth-validator -vv
```
### Run Sawtooth REST-API
```bash
sudo -u sawtooth sawtooth-rest-api -v
```
# Run code in this repository
### Start OCEANSONG Transaction Processor
```bash
cd ./oceansong-tp/pyprocessor
./ocean-tp
```

### Start OCEAN Client
```bash
cd ./oceansong-tp/pyclient
./ocean <command>
```
# Docker
### Start "ONOS" container
My Onos container name is <onos-mininet>
```bash
docker start onos-mininet
```
### Start "Containernet" container
"containernet" name is "containernet"
```bash
docker start containernet
```