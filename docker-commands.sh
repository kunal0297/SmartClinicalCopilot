#!/bin/bash

# Function to display help message
show_help() {
    echo "Smart Clinical Copilot Docker Commands"
    echo "Usage: ./docker-commands.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  build       Build all services"
    echo "  logs        Show logs for all services"
    echo "  clean       Remove all containers and volumes"
    echo "  help        Show this help message"
}

# Function to start services
start_services() {
    echo "Starting services..."
    docker-compose up -d
    echo "Services started!"
}

# Function to stop services
stop_services() {
    echo "Stopping services..."
    docker-compose down
    echo "Services stopped!"
}

# Function to restart services
restart_services() {
    echo "Restarting services..."
    docker-compose restart
    echo "Services restarted!"
}

# Function to build services
build_services() {
    echo "Building services..."
    docker-compose build --no-cache
    echo "Services built!"
}

# Function to show logs
show_logs() {
    echo "Showing logs..."
    docker-compose logs -f
}

# Function to clean up
clean_up() {
    echo "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    echo "Clean up completed!"
}

# Main script logic
case "$1" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "build")
        build_services
        ;;
    "logs")
        show_logs
        ;;
    "clean")
        clean_up
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 