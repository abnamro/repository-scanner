#!/bin/bash
docker build -f Dockerfile-local-windows . -t resc/repository-scanner-backend:${1:-1.0.0}