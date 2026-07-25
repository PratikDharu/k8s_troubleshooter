docker build -t k8s-troubleshooter ./backend

docker run --rm -p 8000:8000 k8s-troubleshooter