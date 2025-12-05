#!/bin/bash
unset DOCKER_API_VERSION

echo ">>> Deploying latest commit..."

# USE "docker compose" (space) NOT "docker-compose" (hyphen)
docker compose up -d --build

echo ">>> Deployment finished. Waiting 10s for app to stabilize..."
sleep 10

# Log the current status
echo ">>> Current app status:"
curl -s http://localhost:5000/ || echo ">>> App returned error!"

echo ">>> Current docker logs (last 5 lines):"
docker logs target-app-container --tail 5