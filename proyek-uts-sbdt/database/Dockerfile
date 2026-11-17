FROM postgres:16-alpine
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql
COPY setup-primary.sh /docker-entrypoint-initdb.d/02-setup-primary.sh
COPY replica-entrypoint.sh /replica-entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/02-setup-primary.sh /replica-entrypoint.sh