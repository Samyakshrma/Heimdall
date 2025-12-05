#!/bin/bash
echo ">>> Deploying latest commit..."
docker-compose up -d --build
echo ">>> Deployment finished. Waiting 10s for app to stabilize..."
sleep 10
echo ">>> Current app status:"
curl -s http://localhost:5000/ || echo ">>> App returned error!"
echo ">>> Current docker logs (last 5 lines):"
docker logs target-app-container --tail 5