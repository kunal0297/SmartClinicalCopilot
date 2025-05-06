# IRIS for Health Setup

This folder contains configuration and startup resources to run InterSystems IRIS for Health CE with FHIR support and load sample FHIR resources automatically.

## Getting Started

1. Copy `.env.example` to `.env` in the root of the project and update credentials as needed.

2. Run the container:

```bash
cd iris
docker compose up -d
