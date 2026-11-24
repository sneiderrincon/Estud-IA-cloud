# Soluciones (solo profesor) · Azure y GCP

Para la sección AWS usa tu `soluciones.md` actual. Los tres problemas de AWS, para mantener el paralelo, son: falta `id-token: write` en el workflow, falta la condición sobre `sub` en la política de confianza y `ecr:*` sobre `*` en los permisos.

## Azure

### 1. Workflow: falta `id-token: write`

**Síntoma.** `azure/login` falla antes de llegar a Azure indicando que no puede obtener el token de ID. Es un fallo visible.

**Causa.** `permissions` solo declara `contents: read`. Al declarar `permissions`, los permisos no listados quedan en `none`, así que GitHub no emite el token OIDC.

**Corrección.**

```yaml
permissions:
  contents: read
  id-token: write
```

Este permiso solo autoriza a pedir el token; no da acceso a ningún recurso.

### 2. Confianza: `subject` apunta a `master`

**Síntoma.** Azure rechaza el intercambio con un error de que no hay credencial federada que coincida (AADSTS70021). Es un fallo visible, y la pista está en que el `sub` del token dice `refs/heads/main`.

**Causa.** El `subject` debe coincidir exactamente con el `sub` del token. Aquí la credencial espera `master`, pero el workflow corre en `main`.

**Corrección.**

```json
"subject": "repo:eafit-nube/estudia-taller:ref:refs/heads/main"
```

**Para conversar.** Si el job declara `environment: produccion`, el `sub` cambia a `repo:eafit-nube/estudia-taller:environment:produccion` y hay que crear otra credencial. A diferencia de AWS, en Azure el `subject` es obligatorio, así que no se puede olvidar la restricción por repositorio; el error posible es ponerla mal.

### 3. Permisos: `Owner` sobre la suscripción

**Síntoma.** Todo funciona. Es un riesgo invisible: un job comprometido puede crear, modificar o borrar cualquier recurso de la suscripción.

**Causa.** Se asignó el rol más amplio en el alcance más amplio.

**Corrección.** Un rol de solo push, limitado al registro.

```bash
az role assignment create \
  --assignee <client-id-del-service-principal> \
  --role AcrPush \
  --scope /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/<grupo>/providers/Microsoft.ContainerRegistry/registries/estudiaacr
```

## GCP

### 1. Workflow: la action `auth` no entrega un token de acceso

**Síntoma.** `docker/login-action` falla por contraseña vacía. Es un fallo visible.

**Causa.** `steps.auth.outputs.access_token` solo existe si `auth` recibe `token_format: access_token`. Sin esa entrada, `auth` deja credenciales para las herramientas de Google, pero no genera el token que Docker necesita.

**Corrección.**

```yaml
- name: Autenticación en Google Cloud
  id: auth
  uses: google-github-actions/auth@v3
  with:
    workload_identity_provider: projects/123456789012/locations/global/workloadIdentityPools/github/providers/github-oidc
    service_account: github-ar@estudia-ejemplo.iam.gserviceaccount.com
    token_format: access_token
```

Alternativa: usar la action `setup-gcloud` y `gcloud auth configure-docker us-central1-docker.pkg.dev`.

### 2. Confianza: provider sin condición y binding a todo el pool

**Síntoma.** Todo funciona, incluso para quien no debería. Es un riesgo invisible: cualquier repositorio de GitHub que obtenga un token válido de GitHub y conozca el provider podría intentar asumir la cuenta de servicio.

**Causa.** Hay dos defectos que se suman. El provider se creó sin `--attribute-condition`, y el binding usa `.../workloadIdentityPools/github/*`, que concede `workloadIdentityUser` a **todas** las identidades del pool.

**Corrección.**

```bash
gcloud iam workload-identity-pools providers create-oidc github-oidc \
  --project=estudia-ejemplo \
  --location=global \
  --workload-identity-pool=github \
  --issuer-uri=https://token.actions.githubusercontent.com \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == 'eafit-nube/estudia-taller'"

gcloud iam service-accounts add-iam-policy-binding \
  github-ar@estudia-ejemplo.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/123456789012/locations/global/workloadIdentityPools/github/attribute.repository/eafit-nube/estudia-taller"
```

**Para conversar.** Es el equivalente de la condición sobre `sub` en AWS. La condición del provider filtra quién puede entrar al pool; el binding filtra quién puede usar esta cuenta de servicio. Conviene tener las dos.

### 3. Permisos: `roles/editor` sobre el proyecto

**Síntoma.** Todo funciona. Es un riesgo invisible: el job puede modificar casi cualquier recurso del proyecto.

**Corrección.** Un rol de escritura sobre el repositorio de imágenes, no sobre el proyecto.

```bash
gcloud artifacts repositories add-iam-policy-binding estudia \
  --project=estudia-ejemplo \
  --location=us-central1 \
  --member="serviceAccount:github-ar@estudia-ejemplo.iam.gserviceaccount.com" \
  --role=roles/artifactregistry.writer
```

## Cómo usarlo en clase

- Los tres problemas de cada hoja tienen la misma forma: **uno que rompe el job** y **dos que no**. Aprovecha eso para enseñar que una ejecución verde no demuestra que la configuración sea segura.
- En Azure, el error que se ve es el de confianza (`subject`) y el invisible es el de permisos. En GCP, el que se ve es el del workflow y los invisibles son los de confianza y permisos.
- Si el grupo tiene cuentas en nubes distintas, la tabla comparativa del inicio de la hoja sirve para la revisión entre pares: el revisor traduce el problema de su compañero a su propia nube.
