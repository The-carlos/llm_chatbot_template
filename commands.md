# 0. Dockerfile.dev
Este es el archivo base. En este archivo es la imagen de docker que contiene un sistema minimo aislado con las dependencias necesarias instaladas para desarrollar el agente.
Para crearlo utilizamos devcontainers. Los archivos que nos ayudan a inicializar todo se crean en el directorio .devcontainer en un file llamado devcontainer.json.
Después solo necesitamos hacer un Dev containers: Re-open in container.

# 1. Crear un repositorio en artifact registry para alojar la imagen de docker:
gcloud artifacts repositories create repo-openai-assistant --repository-format docker --project project-ai-engineering --location us-central1

# 2.Subimos la imagen de docker a artifact registry:
Para ese necesitamos configurar el archivo cloudbuild.yaml, este archivo nos permite configurar los pasos que cloudbuild (el comando) debe de seguir cuando recibe la solicitud de crear la imagen de docker en artifact registry. Esos pasos son 1: Construir la imagen de docker y 2: Hacer push de la imagen a GCP.

gcloud builds submit --config=cloudbuild.yaml --project project-ai-engineering

Este comando puede generar un error si el usuario no tiene los permisos asignados en el proyecto. PAra asignarlos usamos:
Obtenemos la cuenta:
ACCOUNT=$(gcloud config get-value account)
echo $ACCOUNT

Asignamos roles:
# suficiente para enviar builds
gcloud projects add-iam-policy-binding project-ai-engineering \
  --member="user:$ACCOUNT" \
  --role="roles/cloudbuild.builds.submitter"

# o más amplio
gcloud projects add-iam-policy-binding project-ai-engineering \
  --member="user:$ACCOUNT" \
  --role="roles/cloudbuild.builds.editor"

Por último permiso de writter en artifact registry:
PROJECT_NUMBER=$(gcloud projects describe project-ai-engineering --format='value(projectNumber)')

gcloud projects add-iam-policy-binding project-ai-engineering \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"


# 3. Despleaar aplicación en Google Cloud Run 
gcloud run services replace service.yaml --region us-central1 --project project-ai-engineering

# 4. Dar acceso a el servicio a todos
Se utiliza para esto el archivo gcr-service-policy.yaml
´´´
gcloud run services set-iam-policy servicio-openai-assistant gcr-service-policy.yaml --region us-central1 --project project-ai-engineering
´´´