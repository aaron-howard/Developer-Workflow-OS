# Jenkins CI/CD Integration Guide

Connect Jenkins automation server build triggers, pipeline statuses, and build failures to the **Developer Workflow OS**.

---

## 1. Overview & Capabilities

- **Build Pipeline Ingestion**: Ingest build success, failure, and stage duration signals.
- **Release Readiness Blocker Analysis**: Automated blocker flagging when critical builds fail on target release branches.

---

## 2. Setup in Jenkins

1. **Install Notification Plugin**:
   - Go to **Manage Jenkins** -> **Plugins** -> Install *Notification Plugin* or *HTTP Request Plugin*.

2. **Configure Pipeline Webhook Post Step**:
   Add to your `Jenkinsfile`:
   ```groovy
   post {
       always {
           httpRequest httpMode: 'POST',
                       contentType: 'APPLICATION_JSON',
                       customHeaders: [[name: 'X-SDLC-Signature', value: "${env.WEBHOOK_SECRET}"]],
                       requestBody: """{"job": "${env.JOB_NAME}", "build": "${env.BUILD_NUMBER}", "status": "${currentBuild.currentResult}"}""",
                       url: "http://<your-host>:5000/api/v1/ingest/cicd/jenkins"
       }
   }
   ```

---

## 3. Setup in Developer Workflow OS

Add credentials to [`.env`](file:///d:/repos/agentic-os/.env):

```bash
JENKINS_URL="https://jenkins.yourcompany.com"
JENKINS_API_TOKEN="your_jenkins_api_token"
```

---

## 4. Verification

Run a test Jenkins build and verify release status output:
```bash
curl http://localhost:5000/api/release/readiness
```
