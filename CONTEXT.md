# GT-Vision – Project Context (AI Coding Assistant)

## 1. Project Overview

**GT-Vision** is a **high-availability traffic monitoring system** focused on **vehicle detection and license plate recognition (LPR/ANPR)**. The service is designed primarily for **municipal governments (prefeituras)** and must comply with **LGPD (Brazilian General Data Protection Law)**, security best practices, and strict uptime requirements.

The system is intended to operate **24/7**, handling real-time video streaming and AI-based detection with minimal latency, strong fault tolerance, and horizontal scalability.

---

## 2. Target Clients

* Municipal governments (Prefeituras)
* Traffic departments
* Public safety departments
* Civil police
* City administrators and mayors

The system is **not consumer-oriented**; it is a **B2G (Business-to-Government)** platform.

---

## 3. Core Principles

* **High Availability (HA)** – no single point of failure
* **Low Latency Streaming** – optimized for browser playback
* **Fault Isolation** – streaming and AI must fail independently
* **Security First** – OWASP, JWT, encryption, least privilege
* **Compliance** – LGPD by design
* **Observability** – metrics, logs, tracing
* **Maintainability** – clean code, tests, cyclomatic complexity control

---

## 4. Actors (User Roles)

### 4.1 Administrators

Users with elevated privileges, including:

* Traffic agents
* Civil police
* City security operators
* IT/security administrators
* City executives (read-only dashboards)

Capabilities:

* Access live streams
* Configure AI detection rules (ROI, triggers)
* Review detections and alerts
* Manage cameras
* Audit logs and reports

---

## 5. System Architecture (High Level)

The platform is divided into **independent, decoupled services**:

```
[ Cameras ]
     |
     v
[ Streaming Service ]  --->  [ Browser / Dashboard ]
     |
     +----> [ AI Detection Service ] ---> [ Events / Alerts / DB ]
```

### Key Rule

> **Streaming must NEVER depend on AI detection.**

If AI fails, streaming continues unaffected.

---

## 6. Streaming Service

### 6.1 Responsibilities

* Ingest camera feeds (RTSP / ONVIF / HLS)
* Transcode or relay streams
* Deliver low-latency video to browsers
* Handle thousands of concurrent viewers

### 6.2 Requirements

* 24/7 availability
* No memory leaks or buffer overflows
* No data explosion (controlled bitrate)
* Backpressure handling
* Graceful degradation

### 6.3 Non-Functional Constraints

* Must not overload CPU/RAM
* Must scale horizontally
* Stateless whenever possible

---

## 7. AI Detection Service

### 7.1 Overview

Runs independently from streaming. Receives frames or substreams and performs detection only when **ROI + Trigger conditions** are met.

### 7.2 Detection Models

1. **YOLO-based model (on-prem / GPU)**

   * Vehicle detection
   * License plate detection
   * Fast inference

2. **AWS Rekognition Integration**

   * Optional cloud-based detection
   * Used when configured per camera
   * Must respect ROI boundaries

### 7.3 ROI & Trigger System

* ROI (Region of Interest) is defined in the frontend
* User draws polygons or lines on the video
* AI processes frames **only inside ROI**
* Triggers activate detection events

Examples:

* Virtual line crossing
* Restricted area entry
* Stop line violation

---

## 8. High Availability Strategy

### 8.1 Service Isolation

* Streaming Service: multiple replicas
* AI Workers: multiple independent workers

### 8.2 Worker Model

* If one AI worker fails, another takes over
* No shared mutable state between workers
* Jobs must be idempotent

### 8.3 Failure Scenarios

* AI down → Streaming continues
* Worker crash → Job reassigned
* Node crash → Container rescheduled

---

## 9. Security Architecture

### 9.1 Authentication & Authorization

* JWT access tokens
* Bcrypt for password hashing
* Role-Based Access Control (RBAC)

### 9.2 Token Policy

* Access token with short TTL
* Refresh token issued immediately after login
* Automatic token rotation

### 9.3 Session Rules

* Auto logout after **3 minutes of inactivity**
* Token invalidation on logout

### 9.4 OWASP Compliance

* Input validation
* Rate limiting
* Secure headers
* SQL injection prevention
* XSS / CSRF mitigation

---

## 10. LGPD Compliance

* Minimum data retention
* Access logging
* Audit trails
* Encryption at rest and in transit
* Clear separation between:

  * Raw video
  * Metadata
  * Personal data

---

## 11. Observability

* Structured logging
* Metrics (CPU, RAM, FPS, latency)
* Health checks
* Alerts for service degradation

---

## 12. Testing & Quality

### 12.1 Unit Tests

* Mandatory for core logic
* Especially:

  * ROI logic
  * Trigger evaluation
  * Auth flows

### 12.2 Cyclomatic Complexity

* Must be measured continuously
* Avoid overly complex functions
* Prefer composition over condition-heavy logic

---

## 13. Debugging Guidelines

### Common Issues

* Stream freezing → check buffer / bitrate
* AI lag → GPU saturation or ROI misconfiguration
* High memory usage → frame leaks
* Auth issues → token expiration or clock drift

Each known issue must have:

* Symptoms
* Root cause
* Resolution steps

---

## 14. Documentation Rules

* All documentation must be placed under `/docs`
* Markdown (`.md`) only
* Clear, objective, technical language
* This file is the **primary context source** for AI coding assistants

---

## 15. Code Style Guidelines

* Clean Architecture principles
* Small, focused functions
* Explicit naming
* No hidden side effects
* Prefer immutability

---

## 16. Final Notes for AI Assistants

When generating code or suggestions:

* NEVER couple streaming with AI
* ALWAYS assume high-load scenarios
* PRIORITIZE safety, security, and availability
* THINK like a public-sector, mission-critical system
