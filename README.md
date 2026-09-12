# AI Commerce Assistant

> An AI-powered commerce assistant for sellers, designed to automate customer conversations, product discovery, and order management through conversational interfaces.

**AI Commerce Assistant** is an ongoing project focused on building an intelligent commerce layer between sellers and their customers.

The initial implementation is built around **Telegram**, where an AI agent can interact with customers, access store data, answer product-related questions, and assist with order processing.

The project is gradually evolving from a simple chatbot into a modular commerce platform with a clear separation between **AI, domain logic, infrastructure, and communication channels**.

---

## 🎯 Project Goal

Many small online sellers manage their businesses through messaging platforms such as Telegram and Instagram.

Their product information, customer conversations, inventory, and orders are often handled manually.

The goal of this project is to build an AI assistant that can operate on top of the seller's existing commerce data and handle common interactions conversationally.

The long-term vision is:

```text
Customer
   │
   ▼
Communication Channel
(Telegram / Web / ...)
   │
   ▼
AI Commerce Assistant
   │
   ├── Product Discovery
   ├── Store Information
   ├── Inventory
   ├── Order Management
   └── Seller Operations
          │
          ▼
       Store Data
```

The AI should not simply generate text.

It should be able to **understand the conversation, reason about the available store data, and perform actions through tools**.

---

# 🚀 Current Status

The project is actively under development.

### Currently implemented

* Telegram-based AI assistant
* LLM integration
* AI tool/function calling
* Product domain and persistence
* Store-aware request context
* Telegram channel → store resolution
* FastAPI backend
* Telegram Mini App prototype
* Mini App → FastAPI communication
* Product retrieval through the API
* Initial Feature-Based / Modular Monolith migration

### Currently being developed

* Product vertical slice
* Cleaner domain/application/infrastructure boundaries
* Seller-facing AI operations
* Product browsing experience through Mini App
* More robust store/tenant context handling
* Order workflows
* Channel-independent architecture

---

# 🧠 AI Layer

The AI layer is designed around an **agent/tool-calling architecture**.

Instead of giving the LLM direct access to the database, the model interacts with controlled application tools.

Conceptually:

```text
User Message
     │
     ▼
   LLM
     │
     ├── Answer directly
     │
     └── Call Tool
           │
           ▼
      Application Logic
           │
           ▼
        Repository
           │
           ▼
        Database
```

This allows the AI to work with real application state rather than relying only on information contained in the model's context.

Examples of potential AI capabilities include:

* Searching products
* Retrieving product information
* Checking inventory
* Creating orders
* Updating store information
* Answering seller questions
* Assisting customers with product discovery

The AI layer is intentionally separated from the underlying commerce domain so that the same business capabilities can later be used by other interfaces.

---

# 🏗️ Architecture

The project is gradually moving toward a **Feature-Based Modular Monolith** architecture.

Instead of organizing the entire application primarily around technical layers such as:

```text
controllers/
services/
repositories/
models/
```

the goal is to organize business capabilities around features:

```text
Product
Order
Store
AI
...
```

Each feature owns the logic relevant to that business capability.

A simplified representation:

```text
backend/
│
├── src/
│   │
│   ├── modules/
│   │   ├── product/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── infrastructure/
│   │   │   └── ...
│   │   │
│   │   ├── order/
│   │   └── store/
│   │
│   ├── ai/
│   │
│   ├── infrastructure/
│   │
│   └── interfaces/
│       ├── http/
│       └── telegram/
│
└── ...
```

The architecture is being introduced incrementally rather than through a complete rewrite.

---

# 📦 Product Feature

The **Product** feature is currently the main vertical being migrated to the new architecture.

A simplified structure:

```text
product/
│
├── domain/
│   ├── entities/
│   │   └── product.py
│   │
│   └── repositories/
│       └── product_repository.py
│
├── application/
│   └── services/
│       └── product_service.py
│
└── infrastructure/
    └── repositories/
        └── sqlalchemy_product_repository.py
```

The important architectural distinction is:

### Domain Repository

Defines what the domain/application needs:

```text
ProductRepository
```

It describes the contract without depending on SQLAlchemy or a specific database.

### Infrastructure Repository

Implements that contract using the actual persistence technology:

```text
SqlAlchemyProductRepository
```

This keeps database-specific concerns outside the domain.

---

# 🌐 FastAPI

FastAPI is used as the HTTP interface for the backend.

Current responsibilities include:

* HTTP API
* API versioning
* CORS configuration
* Dependency management
* Product endpoints
* Mini App integration

Current API flow:

```text
Telegram Mini App
        │
        │ HTTP
        ▼
     FastAPI
        │
        ▼
 Product Feature
        │
        ▼
 Repository
        │
        ▼
    Database
```

The first working Mini App → FastAPI integration is already in place, with the Mini App successfully retrieving products from the backend.

---

# 📱 Telegram Mini App

The Telegram Mini App is being developed as a complementary interface rather than replacing the conversational bot.

The current approach is:

```text
Telegram Bot
    │
    ├── AI Conversation
    │
    └── Mini App
          │
          ├── Product Listing
          ├── Product Details
          └── Future commerce UI
```

The bot remains the primary conversational interface.

The Mini App is intended for interactions where a visual UI provides a better experience than chat, such as:

* Browsing products
* Viewing product details
* Future shopping flows
* Potential cart/order interfaces

This avoids forcing every interaction into a Telegram chat interface.

---

# 🔐 Store / Tenant Context

The system is designed to support multiple stores.

Requests therefore need to be resolved to the correct store before accessing store-specific data.

Conceptually:

```text
Channel
   │
   ▼
Context Resolver
   │
   ▼
Store Context
   │
   ├── store_id
   ├── user_id
   └── channel
```

This prevents business operations from accidentally accessing data belonging to another store.

The architecture also keeps the concept of a **channel** separate from the business domain so that future interfaces such as Web or Instagram do not require the core business logic to become Telegram-specific.

---

# 🗄️ Data Layer

The current backend uses:

* Python
* SQLAlchemy
* SQLite
* Alembic

The current Product model contains concepts such as:

```text
Product
├── id
├── name
├── description
├── price
├── inventory
├── is_active
└── store_id
```

Persistence is intentionally treated as an infrastructure concern.

The goal is to keep business logic independent from SQLAlchemy wherever practical.

---

# 🛠️ Technology Stack

| Area           | Technology                     |
| -------------- | ------------------------------ |
| Language       | Python                         |
| AI             | LLM API + Tool Calling         |
| Backend        | FastAPI                        |
| Database       | SQLite                         |
| ORM            | SQLAlchemy                     |
| Migrations     | Alembic                        |
| Bot            | python-telegram-bot            |
| Frontend       | HTML / CSS / JavaScript        |
| Mini App       | Telegram Web App               |
| Local Exposure | Cloudflare Tunnel              |
| Architecture   | Feature-Based Modular Monolith |

---

# 📁 Project Structure

The project is currently being migrated incrementally, so the exact structure is evolving.

The target direction is approximately:

```text
project/
│
├── backend/
│   └── src/
│       │
│       ├── modules/
│       │   ├── product/
│       │   ├── order/
│       │   └── store/
│       │
│       ├── ai/
│       │   ├── llm_client.py
│       │   ├── orchestrator.py
│       │   └── tools/
│       │
│       ├── infrastructure/
│       │   └── database/
│       │
│       └── interfaces/
│           ├── http/
│           └── telegram/
│
├── frontend/
│   └── miniapp/
│       ├── index.html
│       ├── style.css
│       └── app.js
│
└── ...
```

The structure will continue to evolve as additional business features are introduced.

---

# 🔄 Development Approach

The architecture is not being designed in isolation before implementation.

Instead, the project follows an **incremental migration approach**:

```text
Existing System
      │
      ▼
Identify Business Feature
      │
      ▼
Extract Domain Concepts
      │
      ▼
Define Application Boundaries
      │
      ▼
Move Infrastructure Concerns
      │
      ▼
Expose Through Interfaces
      │
      ▼
Repeat for Next Feature
```

The Product feature is currently serving as the first major vertical for validating this architecture.

---

# 🗺️ Roadmap

### Phase 1 — Foundation

* [x] Telegram AI bot
* [x] LLM integration
* [x] Tool calling
* [x] Product persistence
* [x] Store-aware context
* [x] FastAPI foundation
* [x] Mini App prototype
* [x] Mini App → API product retrieval

### Phase 2 — Modularization

* [x] Begin Feature-Based architecture
* [x] Introduce Product domain
* [x] Separate repository contract from implementation
* [ ] Complete Product vertical
* [ ] Refine application services
* [ ] Establish reusable infrastructure boundaries
* [ ] Migrate additional features

### Phase 3 — Commerce Workflows

* [ ] Product browsing
* [ ] Product details
* [ ] Cart
* [ ] Order creation
* [ ] Order status
* [ ] Inventory operations
* [ ] Seller operations

### Phase 4 — Multi-Channel

* [ ] Web interface
* [ ] Additional messaging channels
* [ ] Channel-independent AI interaction layer
* [ ] Unified commerce context

---

# 🎯 Long-Term Vision

The long-term goal is not simply to build another chatbot.

The goal is to create an **AI-native commerce assistant** capable of connecting conversational AI with real business operations.

Instead of:

```text
Customer → Human → Database → Human → Customer
```

the system aims toward:

```text
Customer
    │
    ▼
AI Assistant
    │
    ├── Understand intent
    ├── Reason about store data
    ├── Query business capabilities
    ├── Execute actions
    └── Respond naturally
```

The same underlying business capabilities should remain reusable across different channels and interfaces.

---

# 🧪 Project Status

> **Early-stage / Active Development**

This repository represents an actively evolving engineering project.

Some architectural decisions are still being validated through implementation, particularly around:

* Feature boundaries
* AI/application interaction
* Store context
* Tool architecture
* Multi-channel support
* Commerce workflows

The project intentionally favors **incremental architectural evolution** over premature abstraction.

---

# 📌 Why This Project?

This project is also an exploration of a broader question:

> **What should an AI assistant look like when it is connected to real business capabilities rather than being limited to conversation?**

The focus is therefore not only on LLM integration, but also on the engineering problems around:

* Agent/tool architecture
* Domain modeling
* Context and multi-tenancy
* Modular architecture
* AI-to-business-system integration
* Human/computer interaction through conversational interfaces
* Combining conversational and visual interfaces
