# Security Policy

The security of the AutoGen EHCP Document Generation Pipeline and the data it processes is a top priority. This document outlines our security posture and provides guidance for users.

## 1. Reporting a Security Vulnerability

We take all security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings, and we will make every effort to acknowledge your contributions.

If you believe you have discovered a security vulnerability in this project, please **DO NOT** report it through public GitHub issues. Instead, reach out directly to us at Somerset Council.

Please include the following in your report:
- A clear and descriptive title.
- A detailed description of the vulnerability.
- The steps required to reproduce the issue.
- The potential impact of the vulnerability.
- Any potential mitigation or remediation ideas (optional).

We will aim to acknowledge your report ASAP and work to understand and resolve the issue promptly.

## 2. Handling of Sensitive EHCP Data

This application is designed as a **stateless processing engine**. It is architected to avoid the persistent storage of Personally Identifiable Information (PII) or sensitive EHCP data within the application itself.

The data handling model is as follows:
- **Data at Rest:** All data (source documents, intermediate files, and final outputs) resides within the deploying organisation's secure Azure Blob Storage containers. The security of data at rest is the responsibility of the organisation managing the Azure environment.
- **Data in Transit:** The application reads data from Azure Blob Storage, processes it in the memory of the Azure Container App instance, and writes the results back to Azure Blob Storage. All communication with Azure services (Storage, OpenAI) uses TLS encryption.
- **No Application-Level Storage:** The application does not have its own database and does not save any source or output data to the container's local disk, which is ephemeral.

The responsibility for securing the underlying data storage lies with the organisation that deploys this open-source tool.

## 3. GDPR and Data Protection Compliance

This project provides a tool that can be used in a manner compliant with GDPR and other data protection regulations, but compliance is the responsibility of the deploying organisation.

We adhere to the "shared responsibility model":
- **Our Responsibility (as the code provider):** To provide an application that follows security best practices, is stateless, and does not itself store or leak sensitive data.
- **Your Responsibility (as the deploying organisation):** To configure your Azure infrastructure in a compliant manner. This includes:
    -   Implementing strong **Role-Based Access Control (RBAC)** on your Azure Storage Accounts and Container Apps to ensure only authorised personnel and services can access the data.
    -   Ensuring **data-at-rest encryption** is enabled on your Storage Accounts (this is on by default in Azure).
    -   Configuring appropriate **network security**, such as using private endpoints or virtual network integration, to restrict public access to your storage.
    -   Defining and implementing **data retention policies** on your storage containers.
    -   Monitoring **audit logs** for your Azure resources.

## 4. Secure API Key Management

All secrets, such as Azure OpenAI API keys and Azure Storage account keys, must be managed securely.

-   **Local Development:** For local testing, these secrets should be stored in a `.env` file in the project root. This file **MUST** be included in your `.gitignore` file and should **NEVER** be committed to version control.
-   **Production Deployment:** For deployment to Azure Container Apps, the `.env` file should not be used. Instead, all secrets **MUST** be configured using the **Azure Container App's built-in "Secrets" feature**. The application is then configured to read these secrets as environment variables. This is the secure, standard practice for managing credentials in Azure.

We are committed to maintaining and improving the security of this project. We welcome collaboration and feedback from the community to ensure it remains a safe and reliable tool for all users.