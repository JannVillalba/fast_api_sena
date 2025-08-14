# 📋 Sistema de Gestión de Tareas 1.0.0

Este documento describe la API para el Sistema de Gestión de Tareas.

## 📄 Especificación OpenAPI 3.1
La especificación completa de la API se encuentra en `/openapi.json`.

---

## 🚀 Módulos y Endpoints

### 👥 Módulo de Usuarios (`Users`)

-   **POST /users/**
    -   **Descripción:** 🆕 Crea un nuevo usuario.
    -   **Permisos:** N/A (Generalmente público para registro).

-   **GET /users/{user_id}**
    -   **Descripción:** 🔎 Obtiene los detalles de un usuario específico.
    -   **Parámetros de Ruta:**
        -   `user_id` (integer): ID del usuario.
    -   **Permisos:** Se requiere autenticación.

-   **PUT /users/{user_id}**
    -   **Descripción:** ✏️ Actualiza la información de un usuario existente.
    -   **Parámetros de Ruta:**
        -   `user_id` (integer): ID del usuario a actualizar.
    -   **Permisos:** Se requiere autenticación (generalmente el usuario debe ser el propietario del perfil).

-   **DELETE /users/{user_id}**
    -   **Descripción:** 🗑️ Elimina un usuario del sistema.
    -   **Parámetros de Ruta:**
        -   `user_id` (integer): ID del usuario a eliminar.
    -   **Permisos:** Se requiere autenticación (generalmente solo por el usuario propietario o un administrador).

---

### 📂 Módulo de Categorías (`Categories`)

-   **GET /categories/**
    -   **Descripción:** 📜 Lista todas las categorías disponibles.
    -   **Permisos:** Se requiere autenticación.

-   **POST /categories/**
    -   **Descripción:** ➕ Crea una nueva categoría.
    -   **Permisos:** Se requiere autenticación.

-   **PUT /categories/{category_id}**
    -   **Descripción:** 🔄 Actualiza una categoría existente.
    -   **Parámetros de Ruta:**
        -   `category_id` (integer): ID de la categoría a actualizar.
    -   **Permisos:** Se requiere autenticación.

-   **DELETE /categories/{category_id}**
    -   **Descripción:** ❌ Elimina una categoría.
    -   **Parámetros de Ruta:**
        -   `category_id` (integer): ID de la categoría a eliminar.
    -   **Permisos:** Se requiere autenticación.

---

### ✅ Módulo de Tareas (`Tasks`)

-   **POST /tasks/**
    -   **Descripción:** 📝 Crea una nueva tarea.
    -   **Permisos:** Se requiere autenticación.

-   **GET /tasks/**
    -   **Descripción:** 📋 Lista todas las tareas del usuario autenticado.
    -   **Permisos:** Se requiere autenticación.

-   **GET /tasks/{task_id}**
    -   **Descripción:** 🔍 Obtiene los detalles de una tarea específica.
    -   **Parámetros de Ruta:**
        -   `task_id` (integer): ID de la tarea.
    -   **Permisos:** Se requiere autenticación.

-   **PUT /tasks/{task_id}**
    -   **Descripción:** ✍️ Actualiza una tarea existente.
    -   **Parámetros de Ruta:**
        -   `task_id` (integer): ID de la tarea a actualizar.
    -   **Permisos:** Se requiere autenticación.

-   **DELETE /tasks/{task_id}**
    -   **Descripción:** 🗑️ Elimina una tarea.
    -   **Parámetros de Ruta:**
        -   `task_id` (integer): ID de la tarea a eliminar.
    -   **Permisos:** Se requiere autenticación.

---

### 📊 Módulo de Estadísticas (`Statistics`)

-   **GET /stats/overview**
    -   **Descripción:** 📈 Proporciona un resumen de todas las tareas del usuario.
    -   **Permisos:** Se requiere autenticación.

-   **GET /stats/productivity**
    -   **Descripción:** 📉 Genera un informe detallado de la productividad.
    -   **Permisos:** Se requiere autenticación.

---

### 🌐 Endpoints por Defecto (`Default`)

-   **GET /**
    -   **Descripción:** Un punto de entrada simple para verificar que el servicio está en funcionamiento.
    -   **Respuesta:** `Hello World` 👋

-   **GET /info**
    -   **Descripción:** Proporciona información básica sobre la API, como la versión. ℹ️