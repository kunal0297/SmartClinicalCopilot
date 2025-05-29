# Smart Clinical Copilot

A comprehensive clinical decision support system that integrates with FHIR and IRIS for Healthcare to provide real-time clinical guidance and alerts.

## Features

- Real-time clinical decision support
- FHIR integration for healthcare data
- IRIS for Healthcare integration
- Rule-based alerting system
- Modern web interface
- Docker-based deployment

## Architecture

The system consists of the following components:

- **Frontend**: React-based web interface
- **Backend**: FastAPI-based API server
- **FHIR Server**: HAPI FHIR server
- **IRIS**: InterSystems IRIS for Healthcare
- **Database**: PostgreSQL

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js (for local development)
- Python 3.9+ (for local development)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SmartClinicalCopilot.git
   cd SmartClinicalCopilot
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Access the services:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - FHIR Server: http://localhost:8080
   - IRIS Management Portal: http://localhost:52773

## Development

### Backend Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend Development

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
