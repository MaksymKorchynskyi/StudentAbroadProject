FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf

# We will copy the template to conf.d. 
# It's important for init-letsencrypt.sh to use it as a template if we need env subst,
# but we can just copy it directly if it doesn't need env vars.
COPY studentabroad.conf /etc/nginx/conf.d/
