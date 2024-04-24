const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// POST endpoint at /matomo
app.post('/matomo', (req, res) => {
    // Log the received data
    console.log('Received data:', req.body, req.query);

    // Echo back the received data
    res.json({ message: 'Data received successfully', data: req.body });
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
