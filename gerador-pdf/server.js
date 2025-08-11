// server.js

const express = require('express');
const bodyParser = require('body-parser');
const pdfRoutes = require('./routes/pdf.routes');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(bodyParser.json({ limit: '20mb' }));
app.use('/api/pdf', pdfRoutes);

app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
});
