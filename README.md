# AAB to APK Converter

A production-ready, containerized web application to compile Android App Bundles (`.aab`) into signed, installable universal APK files (`.apk`) using Google's `bundletool`.

## Tech Stack
* **Frontend**: Vue 3 (Composition API, Pinia, Axios, Lucide Icons, Tailwind CSS)
* **Backend**: FastAPI, Uvicorn, Async Subprocess, Pydantic-Settings
* **Engine**: Google `bundletool.jar` (ver 1.18.3) executing on a Java 21 environment inside the container.
* **Orchestration**: Docker, Docker Compose

---

## Quick Start

### 1. Requirements
Ensure you have the following installed on your machine:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Run the Application
In the root directory of this repository, run:
```bash
docker-compose up --build
```

This command will:
1. Build the **FastAPI backend** container, install Python dependencies, and pull JRE 21.
2. Build the **Vue 3 frontend** container and install npm dependencies.
3. Automatically download `bundletool.jar` v1.18.3 from GitHub releases on backend startup.
4. Launch the services:
   * **Frontend**: Available at [http://localhost:3000](http://localhost:3000)
   * **Backend**: Available at [http://localhost:8000](http://localhost:8000) (Swagger Docs at `/docs`)

---

## Architectural Details & Performance
1. **Asynchronous Background Processing**: When a `.aab` file is uploaded, the main HTTP thread is never blocked. The server returns a `task_id` immediately, and compilation starts in an asynchronous background worker.
2. **Real-time Terminal Logs**: The frontend polls the status of the compilation task and streams raw console logs (stdout/stderr) from `bundletool` line-by-line directly into a retro dark terminal dashboard.
3. **Stateless Cleanup Scheduler**: To ensure the container memory and disk are not overwhelmed, a background cleanup loop runs every minute. It automatically removes all uploaded and generated files, as well as in-memory tasks, **30 minutes** after creation.
4. **Universal Signing**: APKs are generated in universal mode (`--mode=universal`), automatically signed with a default debug keystore, making them ready to install instantly on any physical test device.
