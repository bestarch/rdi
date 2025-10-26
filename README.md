# rdi


sudo docker run -d \
  --name employee_postgres \
  -e POSTGRES_DB=employee_db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15
