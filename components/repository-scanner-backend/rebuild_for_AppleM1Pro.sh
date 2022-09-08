#!/bin/bash
docker buildx build --platform linux/amd64 -f Dockerfile-local . -t resc/repository-scanner-backend:${1:-1.0.0}
