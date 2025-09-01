FROM nginx:alpine

# Copy your custom nginx.conf to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Default command (nginx starts automatically)
CMD ["nginx", "-g", "daemon off;"]