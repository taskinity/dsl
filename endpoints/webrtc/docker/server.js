const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const path = require("path");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

// Serve static files
app.use(express.static("public"));

// WebSocket connection handler
io.on("connection", (socket) => {
  console.log("New client connected:", socket.id);

  // Handle signaling
  socket.on("signal", (data) => {
    socket.broadcast.emit("signal", {
      ...data,
      from: socket.id,
    });
  });

  // Handle disconnection
  socket.on("disconnect", () => {
    console.log("Client disconnected:", socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`WebRTC signaling server running on port ${PORT}`);
});
