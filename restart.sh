#!/bin/bash
docker compose down
docker rmi translate-video-frontend
docker rmi translate-video-backend
docker compose up -d