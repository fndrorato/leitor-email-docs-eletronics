const express = require('express');
const router = express.Router();
const path = require('path');
const { Factura } = require('../services/Factura');
const { NotaCredito } = require('../services/NotaCredito'); // Importa o serviço NotaCredito
const { parseStringPromise } = require('xml2js');
const xml2js = require('xml2js'); // Este import não está sendo usado, pode ser removido se não for necessário em outro lugar

router.post('/factura', async (req, res) => {
    try {
        const { xml, cod_empresa, nome_empresa } = req.body;

        if (!xml || !cod_empresa || !nome_empresa) {
            return res.status(400).json({ error: 'Dados incompletos' });
        }

        // Converte XML para JSON
        const parsed = await parseStringPromise(xml, { explicitArray: false });

        // Constrói o caminho absoluto para o logo de forma mais robusta
        const projectRoot = path.resolve(__dirname, '..'); 
        const logoPath = path.join(projectRoot, 'media', 'logoFactura.png');

        // Log para verificar o caminho final do logo antes de passar para a função Factura
        console.log('Caminho do logo da Fatura na rota:', logoPath);

        const pdfBuffer = await Factura(parsed, cod_empresa, nome_empresa, logoPath);

        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'inline; filename=factura.pdf');
        return res.send(pdfBuffer);
    } catch (err) {
        console.error('Erro na rota /factura:', err);
        return res.status(500).json({ error: 'Erro ao gerar PDF da Fatura', details: err.message });
    }
});

router.post('/notacredito', async (req, res) => { // Nova rota para Nota de Crédito
    try {
        const { xml, cod_empresa, nome_empresa } = req.body;

        if (!xml || !cod_empresa || !nome_empresa) {
            return res.status(400).json({ error: 'Dados incompletos' });
        }

        // Converte XML para JSON
        const parsed = await parseStringPromise(xml, { explicitArray: false });

        // Constrói o caminho absoluto para o logo da Nota de Crédito
        const projectRoot = path.resolve(__dirname, '..'); 
        const logoPath = path.join(projectRoot, 'media', 'logoNotaCredito.png'); // Caminho para o logo da Nota de Crédito

        // Log para verificar o caminho final do logo antes de passar para a função NotaCredito
        console.log('Caminho do logo da Nota de Crédito na rota:', logoPath);

        // Chama o serviço NotaCredito
        const pdfBuffer = await NotaCredito(parsed, cod_empresa, nome_empresa, logoPath);

        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'inline; filename=nota_credito.pdf'); // Nome do arquivo PDF
        return res.send(pdfBuffer);
    } catch (err) {
        console.error('Erro na rota /notacredito:', err);
        return res.status(500).json({ error: 'Erro ao gerar PDF da Nota de Crédito', details: err.message });
    }
});

module.exports = router;
