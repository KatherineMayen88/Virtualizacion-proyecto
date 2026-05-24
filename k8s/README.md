# Fase 2: Migración y Ejecución con Kubernetes

Este documento detalla el paso a paso realizado para implementar la infraestructura del proyecto usando Kubernetes a través de Docker Desktop, sirviendo como respaldo y guía de uso para la documentación del proyecto.

## ¿Qué se hizo? (Paso a paso)

### 1. Activación del Entorno
Habilitamos el motor de Kubernetes que viene integrado dentro de **Docker Desktop**. Esto nos permite tener un clúster local para hacer pruebas y ejecutar la infraestructura sin necesidad de instalar orquestadores complejos de terceros (como Minikube).

### 2. Creación de Manifiestos de Kubernetes (`.yaml`)
Dado que Kubernetes no utiliza el archivo `docker-compose.yml`, tuvimos que "traducir" toda la configuración de los servicios a **manifiestos** nativos de Kubernetes. Estos archivos se dividieron y agruparon en la carpeta `k8s/` para una administración más clara (separando Deployments de Services):

* **`01-secrets.yaml`** *(Ignorado en Git por seguridad)*: Registra de forma segura las variables de entorno, credenciales y contraseñas de MongoDB de forma local.
* **`01-secrets.yaml.example`**: Plantilla de ejemplo con marcadores de posición para que sepas qué variables debes configurar al clonar el proyecto en otra computadora.
* **`02-mongo-deployment.yaml`**: Crea el contenedor de MongoDB. Utiliza un volumen de tipo `hostPath` apuntando a `/var/lib/mongodb-data` en la VM del nodo local para asegurar que la base de datos **nunca pierda registros ni información** al apagar o reiniciar el clúster.
* **`03-mongo-service.yaml`**: Servicio interno para exponer y permitir conexiones seguras a MongoDB.
* **`04-mongo-express-deployment.yaml`**: Despliega el gestor visual de MongoDB (Mongo Express) conectado de forma segura.
* **`05-mongo-express-service.yaml`**: Expone a Mongo Express de manera externa en el puerto 8081.
* **`06-backend-deployment.yaml`**: Despliega la API de Flask con la política `imagePullPolicy: IfNotPresent` para usar la imagen construida de forma local.
* **`07-backend-service.yaml`**: Expone el backend en el puerto 5000 usando un servicio de tipo `LoadBalancer`.
* **`08-frontend-deployment.yaml`**: Despliega el frontend en Vue del mismo modo que el backend.
* **`09-frontend-service.yaml`**: Expone el frontend en el puerto 3000 como `LoadBalancer`.

---

## Comandos de Operación

### 🚀 Cómo correr el proyecto (Encender)

**Paso 1: Construir las imágenes** (Solo es estrictamente necesario la primera vez, o cada vez que modifiques el código fuente en las carpetas frontend/backend):
```bash
docker build -t frontend-vue:latest ./frontend
docker build -t backend-flask:latest ./backend
```

**Paso 2: Aplicar la configuración de Kubernetes**:
```bash
kubectl apply -f k8s/
```

**Paso 3: Verificar que todo se esté ejecutando**:
```bash
kubectl get pods
```
*(Espera unos segundos hasta que la columna STATUS de todos los servicios diga "Running")*

**URLs de acceso:**
* **Frontend:** http://localhost:3000
* **Backend:** http://localhost:5000
* **Mongo Express:** http://localhost:8081

### 🛑 Cómo apagar el proyecto (Detener)

Para detener los contenedores y liberar la memoria de tu computadora, ejecuta este comando estando en la carpeta raíz del proyecto:
```bash
kubectl delete -f k8s/
```

*Nota: Esto apagará y eliminará los contenedores, pero los datos de tu base de datos MongoDB **no** se perderán gracias a que configuramos la persistencia mediante `hostPath` en el directorio de la VM local.*
