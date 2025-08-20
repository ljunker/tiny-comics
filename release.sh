#!/bin/bash
git pull
docker build -t tiny-comics:latest .
k3d image import tiny-comics:latest -c njord-cluster
