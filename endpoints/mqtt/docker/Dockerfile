FROM eclipse-mosquitto:2.0

# Copy configuration
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

# Create data directory
RUN mkdir -p /mosquitto/data

# Expose MQTT and WebSocket ports
EXPOSE 1883 9001

# Run Mosquitto
CMD ["/docker-entrypoint.sh", "mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
